import os

# 1. Read the original ml_service.py
file_path = "backend/app/services/ml_service.py"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Add imports and Grad-CAM logic at the top
top_code = """
import cv2
import base64

MEDICINAL_DB = {
    "tulsi": {"uses": "Cough, cold, fever, immunity", "prep": "Boil 10-15 leaves as tea", "caution": "Avoid during pregnancy", "toxic": False},
    "neem": {"uses": "Antibacterial, antifungal, skin diseases", "prep": "Apply leaf paste or drink boiled leaves", "caution": "Small doses only", "toxic": False},
    "aloe vera": {"uses": "Burns, skin, digestion, immunity", "prep": "Extract gel from leaf directly", "caution": "Avoid yellow latex layer", "toxic": False},
    "ashwagandha": {"uses": "Stress, immunity, energy", "prep": "Mix powder in milk", "caution": "Avoid if hyperthyroid", "toxic": False},
    "datura": {"uses": "Medical use only", "prep": "NEVER self-administer", "caution": "HIGHLY TOXIC", "toxic": True},
    "oleander": {"uses": "External use only", "prep": "NEVER consume", "caution": "CARDIAC TOXIN \u2014 extremely dangerous", "toxic": True}
}

def get_medicinal_info(plant_name: str) -> dict:
    name_lower = plant_name.lower()
    for key in MEDICINAL_DB:
        if key in name_lower or name_lower in key:
            return MEDICINAL_DB[key]
    return {"uses": "General wellness", "prep": "Consult practitioner", "caution": "Verify identity", "toxic": False}

def get_last_conv_layer(model):
    for layer in reversed(model.layers):
        if len(layer.output_shape) == 4:
            return layer.name
    raise ValueError("No conv layer found")

def get_gradcam_base64(model, img_array, class_idx):
    try:
        last_conv = get_last_conv_layer(model)
        import tensorflow as tf
        grad_model = tf.keras.Model(
            inputs=model.input,
            outputs=[model.get_layer(last_conv).output, model.output]
        )
        with tf.GradientTape() as tape:
            conv_outputs, predictions = grad_model(img_array)
            loss = predictions[:, class_idx]
        grads = tape.gradient(loss, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        import numpy as np
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
        heatmap = heatmap.numpy()
        
        heatmap_resized = cv2.resize(heatmap, (224, 224))
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        
        orig_img = img_array[0]
        if np.min(orig_img) < 0:
             orig_img = (orig_img + 1.0) * 127.5
        elif np.max(orig_img) <= 1.0:
             orig_img = orig_img * 255.0
             
        superimposed = cv2.addWeighted(np.uint8(orig_img), 0.6, heatmap_colored, 0.4, 0)
        _, buffer = cv2.imencode('.jpg', superimposed)
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Grad-CAM error: {e}")
        return None

"""
code = code.replace("from app.config import settings", top_code + "\nfrom app.config import settings")

# 3. Modify master model loading logic
old_load = """            if TF_AVAILABLE:
                # Priority 1: MobileNetV2 Master (17MB) - Verified 80-Class
                mobilenet_h5 = settings.MOBILENET_MODEL_PATH.replace('.onnx', '.h5')
                
                if os.path.exists(mobilenet_h5):
                    self.h5_model = tf.keras.models.load_model(mobilenet_h5, compile=False)
                    self.h5_model_type = "mobilenet-v2-master"
                    logger.info(f"Loaded Master 80-Class H5 Model from {mobilenet_h5}")
                else:
                    self.h5_model = None
                    self.h5_model_type = "none" """

new_load = """            if TF_AVAILABLE:
                eff_h5 = os.path.join(settings.MODEL_DIR, "efficientnetv2_best.h5")
                if os.path.exists(eff_h5):
                    self.h5_model = tf.keras.models.load_model(eff_h5, compile=False)
                    self.h5_model_type = "efficientnet-v2-s-master"
                    logger.info(f"Loaded Master H5 Model from {eff_h5}")
                else:
                    self.h5_model = None
                    self.h5_model_type = "none" """

code = code.replace(old_load, new_load)

# 4. Modify the return to include gradcam and medicinal info
old_return = """            return {
                "predicted_class": predicted_class,
                "predicted_class_index": int(pred_idx),
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_version": model_version,
                "ensemble_used": ensemble_used,
                "is_ambiguous": is_ambiguous,
                "gate": gate if isinstance(gate, dict) else None
            }"""

new_return = """            med_info = get_medicinal_info(predicted_class)
            gradcam_base64 = None
            if self.h5_model and model_version == self.h5_model_type:
                gradcam_base64 = get_gradcam_base64(self.h5_model, h5_input, int(pred_idx))

            return {
                "predicted_class": predicted_class,
                "predicted_class_index": int(pred_idx),
                "confidence": confidence,
                "top_predictions": top_predictions,
                "model_version": model_version,
                "ensemble_used": ensemble_used,
                "is_ambiguous": is_ambiguous,
                "gate": gate if isinstance(gate, dict) else None,
                "gradcam_base64": gradcam_base64,
                "medicinal_info": med_info,
                "is_toxic": med_info["toxic"],
                "caution": med_info["caution"]
            }"""

code = code.replace(old_return, new_return)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Patching ml_service.py successful!")
