import onnxruntime as ort
import numpy as np
import cv2
import base64
import json
import time
import os
import logging
from PIL import Image, ImageOps
from io import BytesIO

logger = logging.getLogger(__name__)

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(_HERE))

def _find(fname, dirs):
    for d in dirs:
        p = os.path.normpath(os.path.join(_BACKEND, d, fname))
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'{fname} not found')

MODEL_PATH = _find('plantoai_model.onnx', ['ml_models'])
CLASS_PATH = _find('class_names.json',    ['app/data'])
KB_PATH    = _find('medicinal_knowledge.json', ['app/data'])

IMG_SIZE   = 224
OOD_THRESH = 0.20
CONF_THRESH = 0.50
MEAN = np.array([0.485,0.456,0.406], dtype=np.float32)
STD  = np.array([0.229,0.224,0.225], dtype=np.float32)

class MLService:
    def __init__(self):
        with open(CLASS_PATH, encoding='utf-8') as f:
            raw = json.load(f)
        self.class_names = [c['name'] if isinstance(c,dict) else c for c in raw]

        with open(KB_PATH, encoding='utf-8') as f:
            self.kb = json.load(f)

        self.sess = ort.InferenceSession(MODEL_PATH,
            providers=['CPUExecutionProvider'])

        logger.info(f'Loaded {len(self.class_names)} clinical class names.')
        logger.info(f'Synchronized {len(self.kb)} botanical monographs.')

    def _kb(self, name):
        for k in [name, name.replace(' ','_'), name.lower(), name.title()]:
            if k in self.kb: return self.kb[k]
        for k in self.kb:
            if name.lower() in k.lower() or k.lower() in name.lower():
                return self.kb[k]
        return {}

    def _pre(self, img):
        img = ImageOps.exif_transpose(img).convert('RGB')
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.LANCZOS)
        a = (np.array(img, dtype=np.float32)/255.0 - MEAN) / STD
        return a.transpose(2,0,1)[np.newaxis].astype(np.float32)

    def _softmax(self, x):
        e = np.exp(x - x.max())
        return e / e.sum()

    def _gradcam(self, img_np, inp, cls_idx):
        try:
            ps=28; h=w=IMG_SIZE
            sal=np.zeros((h//ps, w//ps))
            base=self._softmax(
                self.sess.run(['output'],{'input':inp})[0][0])[cls_idx]
            for i in range(h//ps):
                for j in range(w//ps):
                    m=inp.copy()
                    m[0,:,i*ps:(i+1)*ps,j*ps:(j+1)*ps]=0
                    sal[i,j]=base-self._softmax(
                        self.sess.run(['output'],{'input':m})[0][0])[cls_idx]
            sal=np.maximum(sal,0)
            if sal.max()>0: sal/=sal.max()
            hm=cv2.resize(sal,(w,h))
            hmc=cv2.applyColorMap((hm*255).astype(np.uint8),cv2.COLORMAP_JET)
            hmr=cv2.cvtColor(hmc,cv2.COLOR_BGR2RGB)
            ov=(0.55*img_np+0.45*hmr).astype(np.uint8)
            def b64(a):
                _,buf=cv2.imencode('.png',
                    cv2.cvtColor(a,cv2.COLOR_RGB2BGR))
                return 'data:image/png;base64,'+base64.b64encode(buf).decode()
            return {'heatmap_base64':b64(hmr),'overlay_base64':b64(ov)}
        except Exception as e:
            logger.warning(f'Grad-CAM skipped: {e}')
            return {}

    def predict(self, raw_bytes: bytes) -> dict:
        t0 = time.time()
        try:
            img = Image.open(BytesIO(raw_bytes))
        except Exception as e:
            return {'success':False,'error':'invalid_image','message':str(e)}

        inp = self._pre(img)

        try:
            logits = self.sess.run(['output'],{'input':inp})[0][0]
        except Exception as e:
            return {'success':False,'error':'model_error','message':str(e)}

        probs = self._softmax(logits)
        top   = np.argsort(probs)[::-1]
        conf  = float(probs[top[0]])

        if conf < OOD_THRESH:
            return {
                'success': False,
                'error': 'not_a_plant',
                'message': 'Image does not appear to be a medicinal plant leaf.',
                'suggestion': 'Use a clear photo of a single leaf with good lighting.'
            }

        cname = self.class_names[top[0]]
        top3  = [
            {'rank':i+1,
             'name':self.class_names[top[i]],
             'confidence':round(float(probs[top[i]])*100,2)}
            for i in range(min(3,len(top)))
        ]
        kb      = self._kb(cname)
        img_np  = np.array(img.convert('RGB').resize((IMG_SIZE,IMG_SIZE)))
        gcam    = self._gradcam(img_np, inp, int(top[0]))

        return {
            'success':          True,
            'class_name':       cname,
            'confidence_pct':   round(conf*100,2),
            'confidence_label': 'High' if conf>=0.80 else
                                'Medium' if conf>=CONF_THRESH else 'Low',
            'quality_passed':   conf>=CONF_THRESH,
            'quality_score':    round(conf,4),
            'top3':             top3,
            'knowledge':        kb,
            'gradcam':          gcam,
            'inference_ms':     int((time.time()-t0)*1000)
        }

ml_service = MLService()
