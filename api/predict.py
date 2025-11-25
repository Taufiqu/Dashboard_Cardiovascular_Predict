import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

# Import dengan error handling yang lebih baik
try:
    import joblib
    import numpy as np
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
    IMPORTS_OK = True
except Exception as e:
    # Tangkap SEMUA jenis error (bukan cuma ImportError)
    print("="*50)
    print("CRITICAL STARTUP ERROR")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
    print("="*50)
    IMPORTS_OK = False
# -------------------------------

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
            print(f"Loading model from external storage...")
            print(f"MODEL_URL: {model_url}")
            print(f"SCALER_URL: {scaler_url}")
            
            try:
                # Helper function untuk download dengan retry dan redirect handling
                def download_file(url, file_type):
                    print(f"Downloading {file_type} from: {url}")
                    max_redirects = 5
                    redirect_count = 0
                    current_url = url
                    
                    while redirect_count < max_redirects:
                        try:
                            req = Request(current_url)
                            req.add_header('User-Agent', 'Mozilla/5.0')
                            with urlopen(req, timeout=60) as response:
                                if response.status == 200:
                                    return response
                                elif response.status in [301, 302, 303, 307, 308]:
                                    # Handle redirect
                                    redirect_url = response.headers.get('Location')
                                    if redirect_url:
                                        print(f"Redirecting to: {redirect_url}")
                                        current_url = redirect_url
                                        redirect_count += 1
                                        continue
                                    else:
                                        raise Exception(f"No redirect location found")
                                else:
                                    raise Exception(f"HTTP {response.status}: {response.reason}")
                        except HTTPError as e:
                            raise Exception(f"HTTP Error {e.code}: {e.reason}")
                        except URLError as e:
                            raise Exception(f"URL Error: {e.reason}")
                        except Exception as e:
                            raise Exception(f"Download error: {str(e)}")
                    
                    raise Exception(f"Too many redirects ({max_redirects})")
                
                # Download model ke temporary file
                print("Downloading model file...")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_model:
                    response = download_file(model_url, "model")
                    file_size = 0
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        tmp_model.write(chunk)
                        file_size += len(chunk)
                    model_path = tmp_model.name
                print(f"Model downloaded: {file_size} bytes")
                
                # Download scaler ke temporary file
                print("Downloading scaler file...")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.joblib') as tmp_scaler:
                    response = download_file(scaler_url, "scaler")
                    file_size = 0
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        tmp_scaler.write(chunk)
                        file_size += len(chunk)
                    scaler_path = tmp_scaler.name
                print(f"Scaler downloaded: {file_size} bytes")
                
                # Load model and scaler
                print("Loading model into memory...")
                model = joblib.load(model_path)
                print("Model loaded successfully")
                
                print("Loading scaler into memory...")
                scaler = joblib.load(scaler_path)
                print("Scaler loaded successfully")
                
                # Cleanup temporary files
                os.unlink(model_path)
                os.unlink(scaler_path)
                print("Model loaded from external storage successfully.")
            except Exception as download_error:
                print(f"Error downloading/loading model: {download_error}")
                import traceback
                print(traceback.format_exc())
                raise
        
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
    # Default headers - bisa diakses di semua scope
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Helper function untuk error response - bisa diakses di semua scope
    def make_error_response(status_code, error_msg, details=None, custom_headers=None):
        response_body = {'error': error_msg}
        if details:
            if isinstance(details, dict):
                response_body['details'] = details
            else:
                response_body['details'] = str(details)
        return {
            'statusCode': status_code,
            'headers': custom_headers or default_headers,
            'body': json.dumps(response_body)
        }
    
    # Wrap seluruh handler dengan try-except untuk catch semua error
    try:
        print("=" * 50)
        print("Handler called")
        print(f"IMPORTS_OK: {IMPORTS_OK}")
        print(f"Request type: {type(request)}")
        if request:
            try:
                print(f"Request attributes: {dir(request)}")
            except:
                pass
        print("=" * 50)
        
        # Check imports first
        if not IMPORTS_OK:
            print("ERROR: Imports failed")
            return make_error_response(500, 'Required Python packages not available', 
                'joblib, numpy, or scikit-learn may not be installed')
        
        # Initialize
        print("Initializing handler...")
        headers = default_headers.copy()
        
        # Wrapper untuk return error response (local scope)
        def error_response(status_code, error_msg, details=None):
            return make_error_response(status_code, error_msg, details, headers)
        
        # Check request object
        if request is None:
            return error_response(500, 'Request object is None')
        
        # Get method safely - handle different request object formats
        try:
            method = request.method
        except AttributeError:
            # Try alternative ways to get method
            method = getattr(request, 'method', None) or getattr(request, 'httpMethod', None) or 'GET'
        
        print(f"Request method: {method}")
    
    except Exception as init_error:
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL ERROR in handler initialization: {init_error}")
        print(f"Traceback: {error_trace}")
        return make_error_response(500, 'Handler initialization failed', {
            'error': str(init_error),
            'type': type(init_error).__name__,
            'traceback': error_trace
        })
    
    # Main handler logic
    try:

        # Handle preflight request
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }

        # Handle GET request dengan info message
        if method == 'GET':
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

        if method != 'POST':
            return error_response(405, 'Method not allowed. Use POST method.')

        # Load model jika belum di-load
        if not _model_loaded:
            try:
                print("=" * 50)
                print("Attempting to load model...")
                print(f"MODEL_URL set: {bool(os.environ.get('MODEL_URL'))}")
                print(f"SCALER_URL set: {bool(os.environ.get('SCALER_URL'))}")
                load_model_from_storage()
                print("Model loaded successfully")
                print("=" * 50)
            except Exception as load_error:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Error loading model: {load_error}")
                print(f"Traceback: {error_trace}")
                
                # Get environment variables (masked for security)
                model_url = os.environ.get('MODEL_URL', '')
                scaler_url = os.environ.get('SCALER_URL', '')
                model_url_preview = model_url[:50] + '...' if len(model_url) > 50 else model_url
                scaler_url_preview = scaler_url[:50] + '...' if len(scaler_url) > 50 else scaler_url
                
                return error_response(
                    500, 
                    'Failed to load model',
                    {
                        'error': str(load_error),
                        'error_type': type(load_error).__name__,
                        'hint': 'Make sure MODEL_URL and SCALER_URL environment variables are set correctly and URLs are accessible.',
                        'model_url_set': bool(model_url),
                        'scaler_url_set': bool(scaler_url),
                        'model_url_preview': model_url_preview if model_url else None,
                        'scaler_url_preview': scaler_url_preview if scaler_url else None,
                        'troubleshooting': [
                            'Check if URLs are direct download links (not HTML pages)',
                            'Test URLs in browser - should download file directly',
                            'For GitHub Releases, use format: https://github.com/username/repo/releases/download/tag/file.joblib',
                            'Check Vercel function logs for detailed error messages'
                        ]
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
        try:
            return error_response(400, 'Invalid JSON in request body', str(e))
        except:
            return make_error_response(400, 'Invalid JSON in request body', str(e))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Unexpected error in handler: {str(e)}")
        print(f"Traceback: {error_trace}")
        try:
            return error_response(500, 'Internal server error', {
                'message': str(e),
                'type': type(e).__name__
            })
        except:
            return make_error_response(500, 'Internal server error', {
                'message': str(e),
                'type': type(e).__name__
            })
    except BaseException as e:
        # Catch semua error termasuk SystemExit, KeyboardInterrupt, dll
        import traceback
        error_trace = traceback.format_exc()
        print(f"CRITICAL ERROR (BaseException): {str(e)}")
        print(f"Traceback: {error_trace}")
        return make_error_response(500, 'Critical server error', {
            'message': str(e),
            'type': type(e).__name__
        })

