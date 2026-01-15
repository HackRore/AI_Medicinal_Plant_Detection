# 🌿 AI Medicinal Plant Detection System

> **AI-Based Medicinal Plant Detection Via Leaf Image Recognition**

A professional multi-platform system designed to identify medicinal plants using advanced leaf recognition technology. This project focuses on delivering high-accuracy results through both **Web** and **Mobile** interfaces.

---

## 📈 Current Project Progress

All core modules are fully developed and integrated. The system is ready for testing and demonstration.

- [x] **Backend Engine**: FastAPI core with ML model integration and database management.
- [x] **Machine Learning Pipeline**: Trained MobileNetV2 and ViT models with explainability (Grad-CAM).
- [x] **Web Dashboard**: Responsive Next.js interface for image upload and analysis.
- [x] **Mobile Application**: React Native app for instant leaf scanning on-the-go.
- [x] **Documentation**: Comprehensive guides for setup and quickstart.

---

## 🏗️ Project Structure

Explore the codebase directly through these functional links:

- [**backend/**](backend/) - The API engine and ML services.
- [**frontend/**](frontend/) - The Next.js 14 Web application.
- [**mobile/**](mobile/) - The React Native Expo mobile app.
- [**ml_pipeline/**](ml_pipeline/) - Research, training scripts, and model exports.
- [**docs/**](docs/) - System documentation and research report.

---

## 🚀 Getting Started

### 1. Web Application
```bash
cd frontend
npm install
npm run dev
```
*Access via http://localhost:3000*

### 2. Mobile Application
```bash
cd mobile
npm install
npx expo start
```
*Scan the QR code with the Expo Go app.*

### 3. Backend (Local Setup)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## 📖 Essential Guides

- [**Quick Start Guide**](docs/QUICKSTART.md) - Get up and running in minutes.
- [**Testing Guide**](TESTING_GUIDE.md) - How to verify each module.
- [**Project Report**](docs/original_report.pdf) - Detailed research and implementation details.

---

## 👥 Team & Guidance

### 👩‍🎓 Project Team (Group G14)
- **Madhura Wankhade** (Exam No: 24167)
- **Ravindra Ahire** (Exam No: 24101)
- **Samruddhi Gholap** (Exam No: 24116)
- **Pranali Ghugarkar** (Exam No: 24117)

### 👩‍🏫 Project Guide
- **Ms. Sneha Bankar**
  *Department of Artificial Intelligence and Data Science*
  *Dr. D. Y. Patil College of Engineering & Innovation*

---

**Made with ❤️ for healthcare accessibility and botanical preservation**
