import json
import os
import sys
import traceback
import tempfile
from http.server import BaseHTTPRequestHandler

# --- GLOBAL VARIABLES ---
# Kita simpan model di global scope agar cache tetap jalan
# tapi init-nya nanti (None dulu)
model = None
scaler = None
_model_loaded = False

# --- LAZY IMPORTS & MODEL LOADER ---
def load_dependencies_and_model():
    """
    Fungsi ini melakukan 2 hal berat:
    1. Import library (numpy, joblib, sklearn) -> Lazy Import
    2. Download & Load Model
    """
    global model, scaler, _model_loaded, np, joblib, Request, urlopen, URLError, HTTPError

    print("Status: Starting Lazy Import & Model Loading...")

    # 1. LAZY IMPORT LIBRARIES
    # Import di sini agar Top-Level code ringan & tidak crash saat init
    try:
        import numpy as np
        import joblib
        from urllib.request import urlopen, Request
        from urllib.error import URLError, HTTPError
        print("Status: Libraries imported successfully")
    except Exception as e:
        print("CRITICAL: Failed to import libraries")
        traceback.print_exc()
        raise RuntimeError(f"Library Import Failed: {str(e)}")

    # 2. LOAD MODEL (Jika belum loaded)
    if _model_loaded:
        return

    try:
        # Cek Environment Variables
        model_url = os.environ.get('MODEL_URL')
        scaler_url = os.environ.get('SCALER_URL')

        if not model_url or not scaler_url:
            # Fallback ke local path untuk development
            from pathlib import Path
            base_path = Path(__file__).parent.parent / 'model'
            print(f"Status: Loading from local path: {base_path}")
            
            model_path = base_path / 'rf_cardio_model.joblib'
            scaler_path = base_path / 'scaler_cardio.joblib'
            
            if model_path.exists() and scaler_path.exists():
                model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                _model_loaded = True
                print("Status: Model loaded from local path")
                return
            else:
                raise FileNotFoundError("Environment variables not set and local model not found")

        # Load dari URL (External Storage)
        print(f"Status: Downloading model from {model_url}")
        
        def download_content(url):
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=30) as response:
                return response.read()

        # Download Model
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_model:
            tmp_model.write(download_content(model_url))
            tmp_model_path = tmp_model.name
        
        # Download Scaler
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_scaler:
            tmp_scaler.write(download_content(scaler_url))
            tmp_scaler_path = tmp_scaler.name

        print("Status: Files downloaded, loading to memory...")
        model = joblib.load(tmp_model_path)
        scaler = joblib.load(tmp_scaler_path)
        
        # Cleanup
        os.unlink(tmp_model_path)
        os.unlink(tmp_scaler_path)
        
        _model_loaded = True
        print("Status: Model & Scaler loaded successfully!")

    except Exception as e:
        print("CRITICAL: Model Loading Failed")
        traceback.print_exc()
        raise RuntimeError(f"Model Load Failed: {str(e)}")


# --- MAIN HANDLER ---
def handler(request):
    """
    Vercel Serverless Handler
    """
    # Setup CORS Headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    # Helper response function
    def send_response(status, data):
        return {
            'statusCode': status,
            'headers': headers,
            'body': json.dumps(data)
        }

    try:
        # Handle Preflight OPTIONS
        method = getattr(request, 'method', 'GET')
        if method == 'OPTIONS':
            return send_response(200, {})

        # Handle GET (Health Check)
        if method == 'GET':
            return send_response(200, {
                'status': 'online', 
                'message': 'API is ready. Use POST to predict.',
                'model_loaded': _model_loaded
            })

        # --- DANGER ZONE (Load Berat) ---
        # Kita load di sini, di dalam try-except block
        load_dependencies_and_model()
        # --------------------------------

        # Parse Request Body
        body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
        
        # Feature Mapping
        # Pastikan urutan fitur SAMA PERSIS dengan saat training
        features = [
            float(body.get('height', 170)),
            float(body.get('weight', 70)),
            int(body.get('ap_hi', 120)),
            int(body.get('ap_lo', 80)),
            int(body.get('smoke', 0)),
            int(body.get('alco', 0)),
            int(body.get('active', 1)),
            int(body.get('age', 50)), # age_years
            
            # Derived Features (Hitung ulang di sini)
            float(body.get('weight', 70)) / ((float(body.get('height', 170))/100)**2), # bmi
            int(body.get('ap_hi', 120)) - int(body.get('ap_lo', 80)), # bp_diff
            1 if int(body.get('gender', 1)) == 2 else 0, # gender_male
            
            # One-Hot Encoding Manual
            1 if int(body.get('cholesterol', 1)) == 2 else 0, # chol_2
            1 if int(body.get('cholesterol', 1)) == 3 else 0, # chol_3
            1 if int(body.get('gluc', 1)) == 2 else 0, # gluc_2
            1 if int(body.get('gluc', 1)) == 3 else 0, # gluc_3
            
            # Age Categories
            1 if 30 <= int(body.get('age', 50)) < 45 else 0,
            1 if 45 <= int(body.get('age', 50)) < 60 else 0,
            1 if int(body.get('age', 50)) >= 60 else 0
        ]

        # Prediction
        # Karena lazy import, 'np' baru tersedia di sini
        final_features = np.array([features])
        features_scaled = scaler.transform(final_features)
        
        prediction = model.predict(features_scaled)[0]
        proba = model.predict_proba(features_scaled)[0][1] if hasattr(model, 'predict_proba') else 0

        return send_response(200, {
            'prediction': int(prediction),
            'probability': float(proba),
            'status': 'success'
        })

    except Exception as e:
        # INI BAGIAN PENTING:
        # Karena semua logic ada di dalam try, crash apapun akan ketangkap di sini
        # dan dikirim sebagai JSON ke frontend (bukan error 500 kosong)
        error_detail = traceback.format_exc()
        print("API HANDLER ERROR:", error_detail)
        
        return send_response(500, {
            'error': str(e),
            'type': type(e).__name__,
            'traceback': error_detail
        })