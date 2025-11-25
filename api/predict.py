from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback
import tempfile

# --- GLOBAL VARIABLES ---
model = None
scaler = None
_model_loaded = False

# --- LAZY LOADER ---
def load_resources():
    global model, scaler, _model_loaded
    if _model_loaded: return

    try:
        import joblib
        from urllib.request import urlopen, Request
    except ImportError as e:
        raise RuntimeError(f"Library Import Failed: {str(e)}")

    try:
        model_url = os.environ.get('MODEL_URL')
        scaler_url = os.environ.get('SCALER_URL')

        if not model_url or not scaler_url:
            raise ValueError("Environment variables MODEL_URL or SCALER_URL not set")

        def download_file(url):
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=30) as response:
                return response.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_model:
            tmp_model.write(download_file(model_url))
            tmp_model_path = tmp_model.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_scaler:
            tmp_scaler.write(download_file(scaler_url))
            tmp_scaler_path = tmp_scaler.name

        model = joblib.load(tmp_model_path)
        scaler = joblib.load(tmp_scaler_path)
        
        os.unlink(tmp_model_path)
        os.unlink(tmp_scaler_path)
        
        _model_loaded = True
        print("Status: Model loaded successfully")

    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Model Load Failed: {str(e)}")

# --- HANDLER ---
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
        self._send_response(200, {
            "status": "Alive",
            "message": "API Ready. Send POST request to predict.",
            "model_loaded": _model_loaded
        })

    def do_POST(self):
        try:
            load_resources()
            import numpy as np

            content_length = int(self.headers.get('Content-Length', 0))
            body_str = self.rfile.read(content_length)
            body = json.loads(body_str)

            # --- 1. FEATURE CONSTRUCTION (18 Fitur) ---
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

            bmi = weight / ((height / 100) ** 2)
            bp_diff = ap_hi - ap_lo
            gender_male = 1 if gender == 2 else 0
            
            # --- 2. SPLIT FEATURES ---
            # Kelompok 1: Numeric Features (Wajib di-Scale) - 11 Fitur
            features_numeric = [
                height, weight, ap_hi, ap_lo, smoke, alco, active,
                age, bmi, bp_diff, gender_male
            ]

            # Kelompok 2: Dummy Features (Tidak di-Scale) - 7 Fitur
            features_dummy = [
                1 if cholesterol == 2 else 0,
                1 if cholesterol == 3 else 0,
                1 if gluc == 2 else 0,
                1 if gluc == 3 else 0,
                1 if 30 <= age < 45 else 0,
                1 if 45 <= age < 60 else 0,
                1 if age >= 60 else 0
            ]

            # --- 3. SCALING & COMBINE ---
            # Scale cuma yang numerik
            numeric_array = np.array([features_numeric])
            scaled_numeric = scaler.transform(numeric_array) # Output: (1, 11)
            
            # Gabungin balik sama dummy (tanpa scale)
            dummy_array = np.array([features_dummy]) # Output: (1, 7)
            
            # Final input: (1, 18)
            final_features = np.concatenate([scaled_numeric, dummy_array], axis=1)

            # --- 4. PREDICT ---
            prediction = model.predict(final_features)[0]
            
            proba = 0
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(final_features)[0][1]

            self._send_response(200, {
                "status": "success",
                "prediction": int(prediction),
                "probability": float(proba)
            })

        except Exception as e:
            error_msg = str(e)
            trace = traceback.format_exc()
            print("ERROR:", trace)
            self._send_response(500, {
                "status": "error",
                "message": error_msg,
                "trace": trace
            })