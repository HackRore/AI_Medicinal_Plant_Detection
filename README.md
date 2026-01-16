# 🌿 AI Medicinal Plant Detection System

> **AI-Based Medicinal Plant Detection Via Leaf Image Recognition**

A professional multi-platform system designed to identify medicinal plants using advanced leaf recognition technology. This project focuses on delivering high-accuracy results through both **Web** and **Mobile** interfaces.

---

## 🖼️ System Preview

<div align="center">
  <img src="docs/screenshots/1.png" width="800" alt="Home Dashboard">
  <p><i>Modern, interactive landing page providing instant access to botanical intelligence.</i></p>
  <br>
  
  <img src="docs/screenshots/7.png" width="800" alt="Neural Scanner Interface">
  <p><i>Advanced Neural Scanner with real-time feedback and high-accuracy classification.</i></p>
  <br>

  <img src="docs/screenshots/8.png" width="800" alt="Explainable AI Results">
  <p><i>Explainable AI (XAI) results using Grad-CAM and LIME for transparent predictions.</i></p>
  <br>
  
  <img src="docs/screenshots/4.png" width="800" alt="About Section">
  <p><i>Comprehensive project guidance and dedicated team information.</i></p>
</div>

---

## 🏗️ Project Stages

Here is the current state of development for each module:

- [x] **Stage 1: Backend Engine** - Fully functional REST API built with FastAPI, integrated with ML services.
- [x] **Stage 2: Machine Learning Pipeline** - Completed training and optimization of detection models.
- [x] **Stage 3: Web Application** - Responsive Next.js 14 dashboard for desktop users.
- [x] **Stage 4: Mobile Application** - React Native app for field identification and scanning.
- [x] **Stage 5: Documentation & Presentation** - Research report and system guides finalized.

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

To set up the project on a new machine after cloning, follow these steps:

### 1. Automated Setup (Recommended)
Run the provided PowerShell script to automatically configure environment files and ML placeholders:
```powershell
.\setup.ps1
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload
```
*The `seed_data.py` script will create the database and populate it with initial medicinal plant data.*

### 3. Web Application
```bash
cd frontend
npm install
npm run dev
```

### 4. Mobile Application
```bash
cd mobile
npm install
npx expo start
```

---

## 📖 Essential Guides

- [**Quick Start Guide**](docs/QUICKSTART.md) - *(Coming Soon)* Complete setup instructions.
- [**Testing Guide**](TESTING_GUIDE.md) - *(In Progress)* Module verification steps.
- [**Project Report**](docs/original_report.pdf) - *(Under Review)* Research and final report.

---

## 👥 Team & Guidance

### 👩‍🎓 Project Team (Group G9)
- **Madhura Wankhade**
- **Ravindra Ahire**
- **Samruddhi Gholap**
- **Pranali Ghugarkar**

### 👩‍🏫 Project Guide
- **Ms. Sneha Bankar**
  *Department of Artificial Intelligence and Data Science*
  *Dr. D. Y. Patil College of Engineering & Innovation*

---

**Made with ❤️ for healthcare accessibility and botanical preservation**
