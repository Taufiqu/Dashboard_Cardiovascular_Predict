from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback
import tempfile

# --- GLOBAL VARIABLES (Cache Model di Memory) ---
model = None
scaler = None
_model_loaded = False

# --- LAZY LOADER FUNCTION ---
def load_resources():
    global model, scaler, _model_loaded
    
    # 1. Cek apakah sudah load (biar hemat waktu)
    if _model_loaded:
        return

    print("Status: Starting Lazy Import & Model Loading...")

    # 2. Lazy Import Library (Import di sini biar server start dulu baru loading)
    try:
        import joblib
        from urllib.request import urlopen, Request
    except ImportError as e:
        raise RuntimeError(f"Library Import Failed: {str(e)}")

    # 3. Download & Load Model
    try:
        model_url = os.environ.get('MODEL_URL')
        scaler_url = os.environ.get('SCALER_URL')

        if not model_url or not scaler_url:
            raise ValueError("Environment variables MODEL_URL or SCALER_URL not set")

        print(f"Status: Downloading model from {model_url}")

        def download_file(url):
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=30) as response:
                return response.read()

        # Download ke temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_model:
            tmp_model.write(download_file(model_url))
            tmp_model_path = tmp_model.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_scaler:
            tmp_scaler.write(download_file(scaler_url))
            tmp_scaler_path = tmp_scaler.name

        # Load ke Memory
        model = joblib.load(tmp_model_path)
        scaler = joblib.load(tmp_scaler_path)
        
        # Bersihkan temp file
        os.unlink(tmp_model_path)
        os.unlink(tmp_scaler_path)
        
        _model_loaded = True
        print("Status: Model loaded successfully")

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Model Load Failed: {str(e)}")

# --- CLASS HANDLER (Format Resmi Vercel) ---
class handler(BaseHTTPRequestHandler):

    def _send_response(self, status, data):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_OPTIONS(self):
        self._send_response(200, {})

    def do_GET(self):
        # Health Check Endpoint
        self._send_response(200, {
            "status": "Alive",
            "message": "API Ready. Send POST request to predict.",
            "model_loaded": _model_loaded
        })

    def do_POST(self):
        try:
            # 1. Load Model & Library (Lazy)
            load_resources()
            
            # Import numpy di sini (karena lazy)
            import numpy as np

            # 2. Baca Input Data
            content_length = int(self.headers.get('Content-Length', 0))
            body_str = self.rfile.read(content_length)
            body = json.loads(body_str)

            # 3. Feature Engineering (Sesuai Pipeline Training)
            # Pastikan urutan feature 100% sama dengan features.json
            
            # Ambil raw input
            age = int(body.get('age', 0))
            gender = int(body.get('gender', 1))
            height = float(body.get('height', 0))
            weight = float(body.get('weight', 0))
            ap_hi = int(body.get('ap_hi', 0))
            ap_lo = int(body.get('ap_lo', 0))
            cholesterol = int(body.get('cholesterol', 1))
            gluc = int(body.get('gluc', 1))
            smoke = int(body.get('smoke', 0))
            alco = int(body.get('alco', 0))
            active = int(body.get('active', 1))

            # Hitung Derived Features
            bmi = weight / ((height / 100) ** 2)
            bp_diff = ap_hi - ap_lo
            gender_male = 1 if gender == 2 else 0
            
            # Construct Feature Array (19 Fitur)
            features = [
                height,
                weight,
                ap_hi,
                ap_lo,
                smoke,
                alco,
                active,
                age,           # age_years
                bmi,
                bp_diff,
                gender_male,
                1 if cholesterol == 2 else 0, # cholesterol_2
                1 if cholesterol == 3 else 0, # cholesterol_3
                1 if gluc == 2 else 0,        # gluc_2
                1 if gluc == 3 else 0,        # gluc_3
                1 if 30 <= age < 45 else 0,   # age_cat_30-45
                1 if 45 <= age < 60 else 0,   # age_cat_45-60
                1 if age >= 60 else 0         # age_cat_60+
            ]

            # 4. Prediksi
            final_features = np.array([features])
            features_scaled = scaler.transform(final_features)
            
            prediction = model.predict(features_scaled)[0]
            
            # Coba ambil probabilitas
            proba = 0
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(features_scaled)[0][1]

            # 5. Kirim Hasil
            self._send_response(200, {
                "status": "success",
                "prediction": int(prediction),
                "probability": float(proba)
            })

        except Exception as e:
            # Tangkap Error dan Kirim JSON (Bukan 500 kosong)
            error_msg = str(e)
            trace = traceback.format_exc()
            print("ERROR:", trace)
            
            self._send_response(500, {
                "status": "error",
                "message": error_msg,
                "trace": trace
            })