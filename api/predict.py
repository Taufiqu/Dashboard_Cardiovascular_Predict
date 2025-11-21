import json
import os
import sys
import tempfile
from pathlib import Path

try:
    import joblib
    import numpy as np
    from urllib.request import urlopen
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

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
    # Handle CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Wrapper untuk return error response
    def error_response(status_code, error_msg, details=None):
        response_body = {'error': error_msg}
        if details:
            response_body['details'] = str(details)
        return {
            'statusCode': status_code,
            'headers': headers,
            'body': json.dumps(response_body)
        }
    
    try:

        # Handle preflight request
        if request.method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }

        # Handle GET request dengan info message
        if request.method == 'GET':
            model_status = 'loaded' if _model_loaded else 'not loaded'
            env_check = {
                'MODEL_URL': 'set' if os.environ.get('MODEL_URL') else 'not set',
                'SCALER_URL': 'set' if os.environ.get('SCALER_URL') else 'not set'
            }
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Cardiovascular Prediction API',
                    'endpoint': '/api/predict',
                    'method': 'POST',
                    'model_status': model_status,
                    'environment_variables': env_check
                })
            }

        if request.method != 'POST':
            return error_response(405, 'Method not allowed. Use POST method.')

        # Load model jika belum di-load
        if not _model_loaded:
            try:
                print("Attempting to load model...")
                load_model_from_storage()
                print("Model loaded successfully")
            except Exception as load_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error loading model: {load_error}")
                print(f"Traceback: {error_trace}")
                return error_response(
                    500, 
                    'Failed to load model',
                    {
                        'error': str(load_error),
                        'hint': 'Make sure MODEL_URL and SCALER_URL environment variables are set correctly.',
                        'model_url_set': bool(os.environ.get('MODEL_URL')),
                        'scaler_url_set': bool(os.environ.get('SCALER_URL'))
                    }
                )
        
        # Parse request body
        try:
            # Vercel Python request.body adalah string
            if hasattr(request, 'body'):
                body_str = request.body if isinstance(request.body, str) else request.body.decode('utf-8')
            else:
                body_str = ''
            body = json.loads(body_str) if body_str else {}
        except Exception as parse_error:
            return error_response(400, 'Invalid request body', str(parse_error))
        
        # Validasi input
        required_fields = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                          'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        
        for field in required_fields:
            if field not in body:
                return error_response(400, f'Missing required field: {field}')

        # Feature engineering - sama seperti di training pipeline
        try:
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
        except (ValueError, KeyError) as e:
            return error_response(400, f'Invalid input value: {str(e)}')

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
            return error_response(500, 'Model not loaded. Please check server logs.')

    except json.JSONDecodeError as e:
        return error_response(400, 'Invalid JSON in request body', str(e))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in handler: {str(e)}")
        print(f"Traceback: {error_trace}")
        return error_response(500, 'Internal server error', {
            'message': str(e),
            'type': type(e).__name__
        })

