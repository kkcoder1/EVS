# 🌾 KrishiAI - Multilingual Farmer Crop Advisory Platform

An AI-powered web platform that provides crop suitability recommendations based on soil test parameters, real-time local weather forecasts, explainable AI (XAI) rationale, government scheme matching, SQLite database history, and an interactive AI Farmer Chatbot ("Krishi Mitra").

---

## 🌟 Key Features

- **Machine Learning Recommendation Engine**: Random Forest Classifier trained on 22+ crops (Rice, Wheat, Maize, Cotton, Chickpea, Sugarcane, Jute, Banana, Mango, Apple, etc.) with 98.52% accuracy.
- **Explainable AI (XAI)**: Translates model feature importances into clear, farmer-friendly plain language rationale + interactive Chart.js radar charts.
- **Soil OCR Parser**: Upload PDF or image lab reports (Soil Health Cards) for automatic extraction of N, P, K, pH, moisture, and soil type.
- **Live Weather & Geocoding**: Real-time temperature, humidity, rainfall, and 5-day forecasts via Open-Meteo & OpenStreetMap.
- **Government Scheme Assistant**: Automated lookup matching Central & State schemes (PM-KISAN, PMFBY, Soil Health Card, SMAM, NFSM, MIDH, Micro-Irrigation).
- **Multilingual Support**: Supports 9 languages: **English, Hindi (हिंदी), Punjabi (ਪੰਜਾਬੀ), Marathi (मराठी), Telugu (తెలుగు), Tamil (தமிழ்), Bengali (বাংলা), Gujarati (ગુજરાતી), Kannada (ಕನ್ನಡ)**.
- **AI Farmer Chatbot ("Krishi Mitra")**: Interactive Q&A for pest control, fertilizer dosages, scheme applications, and weather advice with Web Speech API audio read-aloud support.
- **Account System & SQLite Database**: User registration, JWT login, and saved advisory prediction history.

---

## 🚀 How to Publish & Deploy Live (Free Cloud Hosting)

### Method 1: Deploy on Render.com (Recommended - Free Tier)

1. **Initialize Git Repository and Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of KrishiAI platform"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/krishi-ai.git
   git push -u origin main
   ```

2. **Create Web Service on Render**:
   - Go to [render.com](https://render.com) and click **New + -> Web Service**.
   - Connect your GitHub repository `krishi-ai`.
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python model/train_model.py`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Click **Create Web Service**. Render will build and publish your site with a free `https://your-app.onrender.com` link!

---

### Method 2: Deploy with Docker (Railway / Fly.io / DigitalOcean)

You can build and deploy the included `Dockerfile`:
```bash
docker build -t krishi-ai .
docker run -p 8000:8000 krishi-ai
```

---

## 💻 Local Development & Making Future Changes

### 1. Project Directory Structure
```
├── backend/
│   ├── main.py                # FastAPI server entry point & API endpoints
│   ├── database.py            # SQLite & SQLAlchemy database setup
│   ├── models.py              # User, History & Chat DB schemas
│   ├── auth_service.py        # PBKDF2 password hashing & JWT token auth
│   ├── weather_service.py     # Open-Meteo Weather & Geocoding API
│   ├── ocr_service.py         # PDF & Image Soil Report OCR parser
│   ├── xai_service.py         # Plain language Explainable AI engine
│   ├── scheme_service.py      # Government scheme database
│   ├── translation_service.py # 9-language translation dictionary
│   └── chatbot_service.py     # AI Farmer Assistant ("Krishi Mitra") engine
├── model/
│   ├── train_model.py         # ML model training script
│   ├── crop_recommendation_model.pkl # Trained Random Forest model
│   └── crop_metadata.json     # Agronomic metadata per crop
├── static/
│   ├── index.html             # Glassmorphism Single Page Application layout
│   ├── style.css              # Custom responsive stylesheet
│   └── app.js                 # Frontend interactivity, map, charts, auth & audio
├── Dockerfile                 # Production Docker container manifest
├── Procfile                   # Web process command for cloud platforms
└── requirements.txt           # Python dependencies list
```

---

### 2. How to Make Future Changes

#### A. Adding New Crops or Modifying ML Ranges
1. Open [`model/train_model.py`](file:///Users/keshavkhandelwal/Documents/1_proj/model/train_model.py).
2. Add your new crop profile dictionary under `CROP_PROFILES` with its N, P, K, pH, temp, humidity, and rainfall ranges.
3. Retrain the model by running:
   ```bash
   ./venv/bin/python model/train_model.py
   ```

#### B. Adding New Government Schemes
1. Open [`backend/scheme_service.py`](file:///Users/keshavkhandelwal/Documents/1_proj/backend/scheme_service.py).
2. Add a new scheme object to `SCHEMES_DATABASE`.

#### C. Modifying UI Text or Adding Translations
1. Open [`backend/translation_service.py`](file:///Users/keshavkhandelwal/Documents/1_proj/backend/translation_service.py).
2. Update crop translations under `CROP_TRANSLATIONS` or UI strings under `UI_TRANSLATIONS`.

#### D. Running the Local Server
```bash
./venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` in your browser.

---

## 📜 License
Hackathon Open Source Project - 2026.
