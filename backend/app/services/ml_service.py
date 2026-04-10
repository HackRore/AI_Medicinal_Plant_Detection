"""
Complete ML service: ONNX inference + occlusion Grad-CAM + knowledge lookup.
All data served from trained model and knowledge base — zero hardcoded values.
"""
import onnxruntime as ort, numpy as np, cv2, base64, json, time, os
from PIL import Image
from io import BytesIO

BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(BASE, "ml_models", "plantoai_model.onnx")
CLASS_PATH  = os.path.join(BASE, "app",       "data", "class_names.json")
KB_PATH     = os.path.join(BASE, "app",       "data", "medicinal_knowledge.json")

# Fallback model names in order of preference
for candidate in ["plantoai_model.onnx","efficientnetv2_12class.onnx","efficientnetv2.onnx"]:
    p = os.path.join(BASE,"ml_models",candidate)
    if os.path.exists(p): MODEL_PATH = p; break

IMG_SIZE    = 224
OOD_THRESH  = 0.25
CONF_THRESH = 0.50
MEAN = np.array([0.485,0.456,0.406], dtype=np.float32)
STD  = np.array([0.229,0.224,0.225], dtype=np.float32)

class MLService:
    def __init__(self):
        # Load class names
        with open(CLASS_PATH) as f: raw = json.load(f)
        self.class_names = [c["name"] if isinstance(c,dict) else c for c in raw]
        # Load knowledge base
        with open(KB_PATH) as f: self.kb = json.load(f)
        # Load ONNX model
        self.sess = ort.InferenceSession(MODEL_PATH,
            providers=["CUDAExecutionProvider","CPUExecutionProvider"])
        print(f"MLService ready | classes: {len(self.class_names)} | {os.path.basename(MODEL_PATH)}")

    def _pre(self, img):
        img = img.convert("RGB").resize((IMG_SIZE,IMG_SIZE), Image.LANCZOS)
        a   = (np.array(img, dtype=np.float32)/255.0 - MEAN) / STD
        return a.transpose(2,0,1)[np.newaxis].astype(np.float32)

    def _run(self, inp): return self.sess.run(["output"],{"input":inp})[0][0]

    def _softmax(self, x): e=np.exp(x-x.max()); return e/e.sum()

    def _kb(self, name):
        # Normalize: 'Apple leaf' -> 'apple', 'Tomato Early blight' -> 'tomato'
        target = name.lower().replace("_", " ").split(" ")[0]
        
        # Priority 1: Exact Match (Case Insensitive)
        for k in self.kb:
            if target == k.lower(): return self.kb[k]
            
        # Priority 2: Partial Search
        for k in self.kb:
            if target in k.lower() or k.lower() in target:
                return self.kb[k]
        return {}

    def predict(self, raw_bytes: bytes) -> dict:
        t0  = time.time()
        img = Image.open(BytesIO(raw_bytes)).convert("RGB")
        inp = self._pre(img)
        try: logits = self._run(inp)
        except Exception as e:
            return {"success":False,"error":"model_error","message":str(e)}

        probs = self._softmax(logits)
        top   = np.argsort(probs)[::-1]
        conf  = float(probs[top[0]])

        if conf < OOD_THRESH:
            return {"success":False,"error":"not_a_plant",
                    "message":"Image does not appear to contain a recognizable medicinal plant leaf.",
                    "suggestion":"Use a clear photo of a single leaf. Ensure good lighting and plain background."}

        cname = self.class_names[top[0]]
        top3  = [{"rank":i+1,"name":self.class_names[top[i]],
                  "confidence":round(float(probs[top[i]])*100,2)}
                 for i in range(min(3,len(top)))]
        kb    = self._kb(cname)
        img_np= np.array(img.resize((IMG_SIZE,IMG_SIZE)))
        gcam  = self._gradcam(img_np, inp, int(top[0]))

        return {"success":True,"class_name":cname,
                "confidence_pct":round(conf*100,2),
                "confidence_label":"High" if conf>=0.80 else "Medium" if conf>=CONF_THRESH else "Low",
                "quality_passed":conf>=CONF_THRESH,"quality_score":round(conf,4),
                "top3":top3,"knowledge":kb,"gradcam":gcam,
                "inference_ms":int((time.time()-t0)*1000)}

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
