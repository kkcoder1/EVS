import hashlib
import os
import json
import base64
import time
from typing import Optional
from sqlalchemy.orm import Session
from backend.models import User

SECRET_KEY = "krishi_ai_secret_key_hackathon_2026"

def hash_password(password: str) -> str:
    """Hashes password securely using PBKDF2 SHA256"""
    salt = b"krishi_salt_static"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: int = 86400 * 30) -> str:
    """Generates signed JWT-like JSON token"""
    to_encode = data.copy()
    to_encode['exp'] = int(time.time()) + expires_delta
    payload_str = json.dumps(to_encode)
    encoded_payload = base64.urlsafe_b64encode(payload_str.encode()).decode().rstrip("=")
    
    # Signature
    signature = hashlib.sha256(f"{encoded_payload}.{SECRET_KEY}".encode()).hexdigest()
    return f"{encoded_payload}.{signature}"

def decode_access_token(token: str) -> Optional[dict]:
    """Decodes and validates JWT-like token"""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        encoded_payload, signature = parts
        
        expected_sig = hashlib.sha256(f"{encoded_payload}.{SECRET_KEY}".encode()).hexdigest()
        if signature != expected_sig:
            return None
            
        # Add padding back if necessary
        padding = 4 - (len(encoded_payload) % 4)
        if padding != 4:
            encoded_payload += "=" * padding
            
        payload_str = base64.urlsafe_b64decode(encoded_payload).decode()
        data = json.loads(payload_str)
        
        if data.get('exp', 0) < time.time():
            return None # Expired
            
        return data
    except Exception:
        return None

def get_current_user_from_token(db: Session, token: str) -> Optional[User]:
    data = decode_access_token(token)
    if not data or "user_id" not in data:
        return None
    return db.query(User).filter(User.id == data["user_id"]).first()
