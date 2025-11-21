import json
import joblib
import numpy as np
import os
import tempfile
from pathlib import Path
from urllib.request import urlopen

# Feature order sesuai dengan features.json dari training pipeline
# Urutan ini HARUS sama persis dengan urutan saat training
FEATURE_ORDER = [
    "height",
    "weight",
    "ap_hi",
    "ap_lo",
    "smoke",
    "alco",
    "active",
    "age_years",
    "bmi",
    "bp_diff",
    "gender_male",
    "cholesterol_2",
    "cholesterol_3",
    "gluc_2",
    "gluc_3",
    "age_cat_30-45",
    "age_cat_45-60",
    "age_cat_60+"
]

# Model dan scaler - akan di-load saat pertama kali digunakan
model = None
scaler = None
_model_loaded = False

def load_model_from_storage():
    """
    Load model dari external storage atau local path.
    Prioritas:
    1. Environment variable (MODEL_URL, SCALER_URL) - untuk external storage
    2. Local path (untuk development)
    """
    global model, scaler, _model_loaded
    
    if _model_loaded:
        return
    
    try:
        # Option 1: Load dari external storage (S3, Cloud Storage, dll)
        model_url = os.environ.get('MODEL_URL')
        scaler_url = os.environ.get('SCALER_URL')
        
        if model_url and scaler_url:
            print("Loading model from external storage...")
            # Download model dan scaler ke temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_model:
                with urlopen(model_url) as response:
                    tmp_model.write(response.read())
                model_path = tmp_model.name
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_scaler:
                with urlopen(scaler_url) as response:
                    tmp_scaler.write(response.read())
                scaler_path = tmp_scaler.name
            
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path)
            
            # Cleanup temporary files
            os.unlink(model_path)
            os.unlink(scaler_path)
            print("Model loaded from external storage successfully.")
        
        # Option 2: Load dari local path (untuk development/testing)
        else:
            MODEL_PATH = Path(__file__).parent.parent / 'model' / 'rf_cardio_model.joblib'
            SCALER_PATH = Path(__file__).parent.parent / 'model' / 'scaler_cardio.joblib'
            
            if MODEL_PATH.exists() and SCALER_PATH.exists():
                print("Loading model from local path...")
                model = joblib.load(MODEL_PATH)
                scaler = joblib.load(SCALER_PATH)
                print("Model loaded from local path successfully.")
            else:
                raise FileNotFoundError("Model files not found. Set MODEL_URL and SCALER_URL environment variables.")
        
        _model_loaded = True
        print(f"Model loaded. Expected {len(FEATURE_ORDER)} features.")
        
    except Exception as e:
        print(f"Error loading model/scaler: {e}")
        model = None
        scaler = None
        raise

def handler(request):
    """
    Serverless function handler untuk predict cardiovascular disease
    """
    # Handle CORS
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    # Handle preflight request
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # Handle GET request dengan info message
    if request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Cardiovascular Prediction API',
                'endpoint': '/api/predict',
                'method': 'POST',
                'status': 'Model loaded' if _model_loaded else 'Model not loaded yet'
            })
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed. Use POST method.'})
        }

    try:
        # Load model jika belum di-load
        if not _model_loaded:
            try:
                load_model_from_storage()
            except Exception as load_error:
                return {
                    'statusCode': 500,
                    'headers': headers,
                    'body': json.dumps({
                        'error': 'Failed to load model',
                        'details': str(load_error),
                        'hint': 'Make sure MODEL_URL and SCALER_URL environment variables are set correctly.'
                    })
                }
        
        # Parse request body
        # Vercel Python request.body adalah string
        body_str = request.body if isinstance(request.body, str) else request.body.decode('utf-8')
        body = json.loads(body_str) if body_str else {}
        
        # Validasi input
        required_fields = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                          'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': f'Missing field: {field}'})
                }

        # Feature engineering - sama seperti di training pipeline
        age_years = int(body['age'])
        height = float(body['height'])
        weight = float(body['weight'])
        ap_hi = int(body['ap_hi'])
        ap_lo = int(body['ap_lo'])
        gender = int(body['gender'])
        cholesterol = int(body['cholesterol'])
        gluc = int(body['gluc'])
        smoke = int(body['smoke'])
        alco = int(body['alco'])
        active = int(body['active'])

        # Calculate derived features
        bmi = weight / ((height / 100) ** 2)
        bp_diff = ap_hi - ap_lo
        gender_male = 1 if gender == 2 else 0

        # Age categories (matching training pipeline bins: [0, 30, 45, 60, 200])
        age_cat_30_45 = 1 if 30 <= age_years < 45 else 0
        age_cat_45_60 = 1 if 45 <= age_years < 60 else 0
        age_cat_60_plus = 1 if age_years >= 60 else 0

        # Dummy variables untuk cholesterol (drop_first=True, jadi baseline adalah cholesterol=1)
        cholesterol_2 = 1 if cholesterol == 2 else 0
        cholesterol_3 = 1 if cholesterol == 3 else 0

        # Dummy variables untuk gluc (drop_first=True, jadi baseline adalah gluc=1)
        gluc_2 = 1 if gluc == 2 else 0
        gluc_3 = 1 if gluc == 3 else 0

        # Build features dictionary sesuai urutan di FEATURE_ORDER
        features_dict = {
            'height': height,
            'weight': weight,
            'ap_hi': ap_hi,
            'ap_lo': ap_lo,
            'smoke': smoke,
            'alco': alco,
            'active': active,
            'age_years': age_years,
            'bmi': bmi,
            'bp_diff': bp_diff,
            'gender_male': gender_male,
            'cholesterol_2': cholesterol_2,
            'cholesterol_3': cholesterol_3,
            'gluc_2': gluc_2,
            'gluc_3': gluc_3,
            'age_cat_30-45': age_cat_30_45,
            'age_cat_45-60': age_cat_45_60,
            'age_cat_60+': age_cat_60_plus
        }

        # Convert ke array sesuai urutan FEATURE_ORDER
        features_array = np.array([[features_dict[feat] for feat in FEATURE_ORDER]])

        # Scale features
        if scaler is not None:
            features_scaled = scaler.transform(features_array)
        else:
            features_scaled = features_array

        # Predict
        if model is not None:
            prediction = model.predict(features_scaled)[0]
            
            # Get probability if available
            probability = None
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features_scaled)[0]
                probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'prediction': int(prediction),
                    'probability': probability
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Model not loaded'})
            }

    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON'})
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in handler: {str(e)}")
        print(f"Traceback: {error_trace}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'type': type(e).__name__
            })
        }

