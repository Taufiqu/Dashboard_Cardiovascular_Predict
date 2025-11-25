from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# --- HANDLER ---
def handler(request):
    # Setup Headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }

    # Handle OPTIONS (Preflight)
    if hasattr(request, 'method') and request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    # 1. Cek Info System
    sys_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd(),
    }

    # 2. Coba Import Library Satu per Satu (Safely)
    # Kita import di DALAM handler biar kalau crash bisa ditangkap try-except
    lib_status = {}
    
    # Cek Numpy
    try:
        import numpy
        lib_status["numpy"] = f"Success ({numpy.__version__})"
    except Exception as e:
        lib_status["numpy"] = f"FAILED: {str(e)}"
        lib_status["numpy_trace"] = traceback.format_exc()

    # Cek Joblib
    try:
        import joblib
        lib_status["joblib"] = f"Success ({joblib.__version__})"
    except Exception as e:
        lib_status["joblib"] = f"FAILED: {str(e)}"

    # Cek Scikit-Learn (Biang kerok biasanya di sini)
    try:
        import sklearn
        lib_status["sklearn"] = f"Success ({sklearn.__version__})"
    except Exception as e:
        lib_status["sklearn"] = f"FAILED: {str(e)}"
        lib_status["sklearn_trace"] = traceback.format_exc()

    # 3. Return JSON Diagnostic
    # Kalau JSON ini muncul di browser/logging, berarti server SUDAH HIDUP.
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            "status": "Diagnostic Mode",
            "system": sys_info,
            "libraries": lib_status
        }, indent=2)
    }