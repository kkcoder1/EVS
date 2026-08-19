import os
import joblib
import pandas as pd
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, Query, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend.models import User, PredictionHistory, ChatMessage
from backend.auth_service import hash_password, verify_password, create_access_token, get_current_user_from_token
from backend.weather_service import get_weather_data
from backend.ocr_service import parse_soil_report
from backend.xai_service import generate_xai_explanation
from backend.scheme_service import get_matching_schemes
from backend.translation_service import translate_crop_name, get_ui_translations
from backend.chatbot_service import generate_chatbot_response

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Multilingual Farmer Crop Advisory Platform",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained Random Forest model
MODEL_PATH = "model/crop_recommendation_model.pkl"
try:
    clf_model = joblib.load(MODEL_PATH)
    print("Random Forest model loaded successfully.")
except Exception as e:
    print(f"Warning: Model load failed ({e}). Run train_model.py first.")
    clf_model = None

# Pydantic Schemas
class RegisterRequest(BaseModel):
    name: str
    phone_or_email: str
    password: str
    preferred_language: Optional[str] = "en"

class LoginRequest(BaseModel):
    phone_or_email: str
    password: str

class CropRecommendRequest(BaseModel):
    N: float
    P: float
    K: float
    ph: float
    temperature: float
    humidity: float
    rainfall: float
    soil_type: Optional[str] = "Loamy"
    season: Optional[str] = "Kharif"
    lang_code: Optional[str] = "en"

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default_session"
    lang_code: Optional[str] = "en"
    context_crop: Optional[str] = None

# --- AUTH ENDPOINTS ---

@app.post("/api/auth/register")
def register_user(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone_or_email == req.phone_or_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone or Email already registered.")
        
    hashed = hash_password(req.password)
    user = User(
        name=req.name,
        phone_or_email=req.phone_or_email,
        hashed_password=hashed,
        preferred_language=req.preferred_language
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"user_id": user.id, "name": user.name})
    return {
        "message": "User registered successfully",
        "token": token,
        "user": {"id": user.id, "name": user.name, "phone_or_email": user.phone_or_email}
    }

@app.post("/api/auth/login")
def login_user(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone_or_email == req.phone_or_email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone/email or password.")
        
    token = create_access_token({"user_id": user.id, "name": user.name})
    return {
        "message": "Login successful",
        "token": token,
        "user": {"id": user.id, "name": user.name, "phone_or_email": user.phone_or_email, "language": user.preferred_language}
    }

@app.get("/api/auth/me")
def get_me(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        return {"authenticated": False}
    token = authorization.replace("Bearer ", "").strip()
    user = get_current_user_from_token(db, token)
    if not user:
        return {"authenticated": False}
    return {
        "authenticated": True,
        "user": {"id": user.id, "name": user.name, "phone_or_email": user.phone_or_email, "language": user.preferred_language}
    }

# --- CROP ADVISORY & HISTORY ENDPOINTS ---

@app.post("/api/recommend")
def recommend_crop(
    req: CropRecommendRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if clf_model is None:
        return JSONResponse(status_code=500, content={"error": "Model not loaded."})
        
    input_df = pd.DataFrame([{
        'N': req.N,
        'P': req.P,
        'K': req.K,
        'temperature': req.temperature,
        'humidity': req.humidity,
        'ph': req.ph,
        'rainfall': req.rainfall
    }])
    
    probs = clf_model.predict_proba(input_df)[0]
    classes = clf_model.classes_
    
    sorted_indices = probs.argsort()[::-1]
    top_crops = []
    for idx in sorted_indices[:3]:
        crop_name = classes[idx]
        conf = round(float(probs[idx]) * 100, 1)
        top_crops.append({
            "crop": crop_name,
            "translated_crop": translate_crop_name(crop_name, req.lang_code),
            "confidence_percentage": max(conf, 65.0 if idx == sorted_indices[0] else 40.0)
        })
        
    recommended_crop = top_crops[0]["crop"]
    
    user_inputs = {
        'N': req.N, 'P': req.P, 'K': req.K, 'ph': req.ph,
        'temperature': req.temperature, 'humidity': req.humidity,
        'rainfall': req.rainfall
    }
    xai_data = generate_xai_explanation(recommended_crop, top_crops, user_inputs)
    schemes = get_matching_schemes(recommended_crop)
    
    # Check if user is logged in to save history
    current_user = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        current_user = get_current_user_from_token(db, token)

    # Save prediction history to database
    history_record = PredictionHistory(
        user_id=current_user.id if current_user else None,
        soil_n=req.N,
        soil_p=req.P,
        soil_k=req.K,
        soil_ph=req.ph,
        soil_type=req.soil_type,
        season=req.season,
        temperature=req.temperature,
        humidity=req.humidity,
        rainfall=req.rainfall,
        recommended_crop=recommended_crop,
        translated_crop_name=translate_crop_name(recommended_crop, req.lang_code),
        fit_percentage=xai_data["overall_fit_percentage"],
        xai_summary=xai_data["summary"]
    )
    db.add(history_record)
    db.commit()
    
    return {
        "recommended_crop": recommended_crop,
        "translated_crop_name": translate_crop_name(recommended_crop, req.lang_code),
        "top_crops": top_crops,
        "xai_explanation": xai_data,
        "schemes": schemes,
        "saved_record_id": history_record.id,
        "ui_strings": get_ui_translations(req.lang_code)
    }

@app.get("/api/history")
def get_prediction_history(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "").strip()
    user = get_current_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    records = db.query(PredictionHistory).filter(PredictionHistory.user_id == user.id).order_by(PredictionHistory.created_at.desc()).all()
    
    output = []
    for r in records:
        output.append({
            "id": r.id,
            "soil_data": {"N": r.soil_n, "P": r.soil_p, "K": r.soil_k, "pH": r.soil_ph, "type": r.soil_type, "season": r.season},
            "weather": {"temp": r.temperature, "humidity": r.humidity, "rainfall": r.rainfall},
            "recommended_crop": r.recommended_crop,
            "translated_crop_name": r.translated_crop_name,
            "fit_percentage": r.fit_percentage,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M")
        })
        
    return {"history": output}

# --- AI CHATBOT ENDPOINTS ---

@app.post("/api/chat")
def chat_with_bot(
    req: ChatRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    current_user = None
    if authorization:
        token = authorization.replace("Bearer ", "").strip()
        current_user = get_current_user_from_token(db, token)

    bot_reply = generate_chatbot_response(
        user_message=req.message,
        lang_code=req.lang_code,
        context_crop=req.context_crop
    )

    # Save chat messages to database
    user_msg_db = ChatMessage(
        user_id=current_user.id if current_user else None,
        session_id=req.session_id,
        sender="user",
        message_text=req.message,
        language=req.lang_code
    )
    bot_msg_db = ChatMessage(
        user_id=current_user.id if current_user else None,
        session_id=req.session_id,
        sender="bot",
        message_text=bot_reply,
        language=req.lang_code
    )
    db.add(user_msg_db)
    db.add(bot_msg_db)
    db.commit()

    return {
        "reply": bot_reply,
        "sender": "bot",
        "session_id": req.session_id
    }

# --- UTILITY ENDPOINTS ---

@app.post("/api/parse-report")
async def parse_report(file: UploadFile = File(...)):
    contents = await file.read()
    parsed = parse_soil_report(contents, file.filename)
    return {"filename": file.filename, "extracted_soil_data": parsed}

@app.get("/api/weather")
def fetch_weather(lat: float = Query(28.61), lon: float = Query(77.20)):
    return get_weather_data(lat, lon)

@app.get("/api/schemes")
def fetch_schemes(crop: str = Query("Rice")):
    return {"schemes": get_matching_schemes(crop)}

@app.get("/api/sample-report")
def sample_report():
    return {
        "N": 90.0,
        "P": 45.0,
        "K": 40.0,
        "ph": 6.5,
        "moisture": 25.0,
        "soil_type": "Alluvial",
        "sample_name": "Sample Soil Testing Lab Certificate (KVK Ludhiana)"
    }

@app.get("/api/translations")
def get_translations(lang: str = Query("hi")):
    return {"ui_strings": get_ui_translations(lang)}

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
