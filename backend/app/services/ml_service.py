import os, json, logging, base64, time, threading, cv2
import numpy as np
from io import BytesIO

# --- ABSOLUTE PATH HARDENING ---
_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_HERE)
_BACKEND_ROOT = os.path.dirname(_APP_DIR)

DATA_DIR = os.path.join(_APP_DIR, "data")
MODEL_DIR = os.path.join(_BACKEND_ROOT, "ml_models")

CLASS_PATH = os.path.join(DATA_DIR, "class_names.json")
KB_PATH    = os.path.join(DATA_DIR, "medicinal_knowledge.json")
BEST_MODEL = os.path.join(MODEL_DIR, "best.pt")

IMG_SIZE = 224

class MLService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.class_names = []
        self.kb = {}
        self.model = None
        self.model_loaded = False
        
        # Load fast metadata immediately
        self._load_metadata()
        
    def deferred_init(self):
        """Trigger heavy imports and model load in background."""
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_metadata(self):
        try:
            if os.path.exists(CLASS_PATH):
                with open(CLASS_PATH) as f:
                    raw = json.load(f)
                    if isinstance(raw, list):
                        self.class_names = [c["name"] if isinstance(c, dict) else c for c in raw]
                    else:
                        self.class_names = sorted(list(raw.values()))
                self.logger.info(f"Loaded {len(self.class_names)} clinical class names.")
            else:
                self.logger.error(f"CRITICAL: class_names.json missing at {CLASS_PATH}")

            if os.path.exists(KB_PATH):
                with open(KB_PATH) as f:
                    self.kb = json.load(f)
                self.logger.info(f"Loaded {len(self.kb)} medicinal monographs.")
        except Exception as e:
            self.logger.error(f"Metadata init failed: {e}")

    def _load_model(self):
        """Heavy imports deferred here."""
        try:
            import torch
            import torch.nn as nn
            from torchvision import transforms, models
            from PIL import Image, ImageOps
            
            # Recreate architecture
            self.model = models.mobilenet_v3_large(weights=None)
            self.model.classifier[3] = nn.Linear(self.model.classifier[3].in_features, max(25, len(self.class_names)))
            
            if os.path.exists(BEST_MODEL):
                self.model.load_state_dict(torch.load(BEST_MODEL, map_location='cpu'))
                self.model.eval()
                self.model_loaded = True
                self.logger.info("Successfully loaded production AI model.")
            else:
                self.logger.warning("No production model found. AI Brain building in progress.")
        except Exception as e:
            self.logger.error(f"Background Model load failed: {e}")

    def _kb(self, name):
        target = name.lower().replace("_", " ").split(" ")[0]
        for k in self.kb:
            if target == k.lower(): return self.kb[k]
        for k in self.kb:
            if target in k.lower() or k.lower() in target:
                return self.kb[k]
        return {}

    def predict(self, raw_bytes: bytes) -> dict:
        """Perform high-confidence medicinal plant identification with production hardening."""
        if self.model is None:
            return {"success": False, "error": "Neural Engine Offline"}

        t0 = time.time()
        try:
            # 1. Byte-stream intake
            img = Image.open(BytesIO(raw_bytes))
            
            # 2. Exif Orientation Fix (Crucial for smartphone photos)
            img = ImageOps.exif_transpose(img).convert("RGB")
            
            # 3. G9 Preprocessing Pipe
            img_tensor = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])(img).unsqueeze(0)

            # 4. Neural Inference
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probs = torch.nn.functional.softmax(outputs[0], dim=0)
                conf, idx = torch.max(probs, dim=0)

            conf_val = float(conf.item())
            
            # 5. Botanical Guardrail (Out-of-Distribution Detection)
            if conf_val < 0.25: # OOD Threshold
                return {
                    "success": False,
                    "error": "not_a_medicinal_plant",
                    "message": "The G9 Engine could not verify this as a recognized medicinal species. Please ensure the leaf is clear and well-lit.",
                    "confidence": conf_val
                }

            predicted_class = self.class_names[idx.item()]
            kb = self._kb(predicted_class)
            
            # Phase 6: Active Learning Data Flywheel (Novelty Claim)
            self._archive_prediction(raw_bytes, predicted_class, conf_val)
            
            return {
                "success": True,
                "class_name": predicted_class,
                "confidence_pct": round(conf_val * 100, 2),
                "confidence_label": "High" if conf_val > 0.85 else "Medium" if conf_val > 0.50 else "Low",
                "knowledge": kb,
                "inference_ms": int((time.time() - t0) * 1000)
            }
        except Exception as e:
            self.logger.error(f"Production inference error: {e}")
            return {"success": False, "error": "Internal Processing Error", "details": str(e)}

    def _archive_prediction(self, raw_bytes, label, confidence):
        """Asynchronously archive high-confidence images for future model re-training."""
        try:
            # Only archive high-quality examples to prevent dataset poisoning
            if confidence < 0.60: return 
            
            archive_root = os.path.join(_BACKEND_ROOT, "app", "data", "active_learning")
            label_dir = os.path.join(archive_root, label.replace(" ", "_"))
            os.makedirs(label_dir, exist_ok=True)
            
            ts = int(time.time() * 1000)
            fname = f"user_{ts}.jpg"
            with open(os.path.join(label_dir, fname), "wb") as f:
                f.write(raw_bytes)
            self.logger.info(f"Archived image for {label} (Active Learning Loop)")
        except Exception as e:
            self.logger.warning(f"Active Learning Archiver failed: {e}")

    def _gradcam(self, img_np, inp, cls_idx):
        try:
            ps=28; h=w=IMG_SIZE
            sal=np.zeros((h//ps, w//ps))
            base=self._softmax(self._run(inp))[cls_idx]
            for i in range(h//ps):
                for j in range(w//ps):
                    m=inp.copy()
                    m[0,:,i*ps:(i+1)*ps,j*ps:(j+1)*ps]=0
                    sal[i,j]=base-self._softmax(self._run(m))[cls_idx]
            sal=np.maximum(sal,0)
            if sal.max()>0: sal/=sal.max()
            hm =cv2.resize(sal,(w,h))
            hmc=cv2.applyColorMap((hm*255).astype(np.uint8),cv2.COLORMAP_JET)
            hmr=cv2.cvtColor(hmc,cv2.COLOR_BGR2RGB)
            ov =(0.55*img_np+0.45*hmr).astype(np.uint8)
            def b64(a):
                _,buf=cv2.imencode(".png",cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
                return "data:image/png;base64,"+base64.b64encode(buf).decode()
            return {"heatmap_base64":b64(hmr),"overlay_base64":b64(ov)}
        except Exception as e:
            print(f"Grad-CAM error: {e}"); return {}

ml_service = MLService()
