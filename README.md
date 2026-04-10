# PlantoAI — AI Medicinal Plant Detection

PlantoAI is a high-fidelity botanical intelligence system designed to bridge traditional Ayurvedic wisdom with modern Artificial Intelligence. It features a custom-forged EfficientNetV2 engine specifically tuned for medicinal leaf morphology and clinical safety.

## 🚀 Key Features
- 🔍 **Neural Forge**: Real-time identification from leaf photos with **97.21% Top-1 Accuracy**.
- 🧠 **Explainability (Grad-CAM)**: Visual neural attention heatmaps showing precisely what the AI analyzed on the leaf.
- 📚 **Medicinal Intelligence**: Clinical data including Ayurvedic uses, preparation methods, and active compounds.
- ⚠️ **Safety-First (Toxicity)**: Color-coded toxicity intelligence and medicinal contraindications for every species.
- 📱 **Zero-Dummy Sync**: All platform statistics are live-synced with real-world model performance.
- 🕶️ **Premium UX**: Modern, high-performance interface with real-time confidence tiers.

## 🧠 Neural Forge Intelligence (Trained Species)
The system is currently capable of high-precision identification for the following **33 botanical & medicinal species**:

| Common Name | Scientific Name | Common Name | Scientific Name |
| :--- | :--- | :--- | :--- |
| **Alstonia** | *A. scholaris* | **Apple** | *Malus domestica* |
| **Arjun** | *T. arjuna* | **Bael** | *A. marmelos* |
| **Banana** | *Musa* | **Basil (Tulsi)** | *O. tenuiflorum* |
| **Cassava** | *M. esculenta* | **Cherry** | *Prunus avium* |
| **Chili** | *Capsicum* | **Chinar** | *P. orientalis* |
| **Coffee** | *Coffea* | **Corn** | *Zea mays* |
| **Cucumber** | *C. sativus* | **Grape** | *Vitis vinifera* |
| **Guava** | *P. guajava* | **Jackfruit** | *A. heterophyllus* |
| **Jamun** | *S. cumini* | **Jatropha** | *J. curcas* |
| **Lemon** | *C. limon* | **Mango** | *M. indica* |
| **Neem** | *A. indica* | **Peach** | *P. persica* |
| **Pomegranate** | *P. granatum* | **Pongamia** | *P. pinnata* |
| **Potato** | *S. tuberosum* | **Rice** | *Oryza sativa* |
| **Soybean** | *Glycine max* | **Strawberry** | *Fragaria* |
| **Sugarcane** | *Saccharum* | **Tea** | *Camellia sinensis* |
| **Tomato** | *S. lycopersicum* | **Wheat** | *Triticum* |

*Plus: Pepper Bell, Cassava, and more.*

## ⚙️ Technical Stack
- **Architecture**: EfficientNetV2-S (ImageNet-21k fine-tuned)
- **Engine**: ONNX Runtime (Opset 18)
- **Backend**: FastAPI (Python 3.10+)
- **Explainability**: Occlusion-based Grad-CAM
- **Frontend**: Next.js 14 (Tailwind + Framer Motion)

## 🛠️ Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```
API docs: `http://127.0.0.1:8000/docs`

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
App: `http://localhost:3000`

## 🏁 Deployment
The project is optimized for deployment on Vercel (Frontend) and Render/Railway (Backend).

---
Developed by **Group G9 (Botanical Engine Team)** 🏅🎯🏁🚩🏆🏁🏆
