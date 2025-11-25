from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

def handler(request):
    # Setup Headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }

    # 1. Cek Info Environment System
    sys_info = {
        "python_version": sys.version,
        "platform": sys.platform,
        "cwd": os.getcwd(),
    }

    # 2. Coba Import Library Satu per Satu (Safely)
    # Ini akan memberi tahu kita library mana yang bikin crash
    lib_status = {}
    
    # Cek Numpy
    try:
        import numpy
        lib_status["numpy"] = f"Success ({numpy.__version__})"
    except Exception as e:
        lib_status["numpy"] = f"FAILED: {str(e)}"

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
        # Coba tangkap error binary/linking yang lebih dalam
        lib_status["sklearn_traceback"] = traceback.format_exc()

    # 3. Return JSON Diagnostic
    # Kalau ini berhasil muncul di browser, berarti Server Vercel SEHAT.
    # Masalahnya cuma di library.
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            "status": "Diagnostic Mode",
            "system": sys_info,
            "libraries": lib_status
        }, indent=2)
    }