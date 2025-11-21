# Troubleshooting: Python Process Exited with Exit Status 1

## Error yang Terjadi

```
Python process exited with exit status: 1
```

## Kemungkinan Penyebab

### 1. Import Dependencies Gagal

**Gejala:** Error saat import `joblib`, `numpy`, atau `scikit-learn`

**Solusi:**
- Pastikan `requirements.txt` sudah benar
- Pastikan semua dependencies terinstall
- Cek build logs di Vercel untuk error detail

### 2. Environment Variables Belum Di-Set

**Gejala:** Model tidak bisa di-load, error "Model files not found"

**Solusi:**
1. Buka Vercel Dashboard → Project → Settings → Environment Variables
2. Pastikan ada:
   - `MODEL_URL` = URL ke model file
   - `SCALER_URL` = URL ke scaler file
3. Pastikan sudah di-centang untuk Production, Preview, Development
4. Redeploy setelah set environment variables

### 3. Model URL Tidak Valid

**Gejala:** Error saat download model dari URL

**Solusi:**
- Test URL di browser, harus langsung download file
- Pastikan URL format benar (harus direct download link)
- Untuk GitHub Releases, format: `https://github.com/username/repo/releases/download/v1.0.0/file.joblib`

### 4. Syntax Error atau Code Error

**Gejala:** Python process crash saat function dijalankan

**Solusi:**
- Cek function logs di Vercel untuk error detail
- Pastikan tidak ada syntax error
- Test code local dulu sebelum deploy

## Cara Debug

### 1. Cek Function Logs di Vercel

1. Buka Vercel Dashboard
2. Pilih project
3. Klik "Deployments" → deployment terbaru
4. Klik "Functions" tab
5. Klik `/api/predict`
6. Lihat logs untuk error detail

### 2. Test dengan GET Request

Hit endpoint dengan GET request:
```
GET https://your-app.vercel.app/api/predict
```

Akan dapat response:
```json
{
  "message": "Cardiovascular Prediction API",
  "endpoint": "/api/predict",
  "method": "POST",
  "status": "Model not loaded yet" // atau "Model loaded"
}
```

### 3. Test Environment Variables

Cek apakah environment variables sudah di-set:
- Vercel Dashboard → Settings → Environment Variables
- Pastikan `MODEL_URL` dan `SCALER_URL` ada

### 4. Test Model URL

Buka URL model di browser:
- Harus langsung download file
- Tidak boleh redirect atau error 404

## Checklist Debugging

- [ ] Cek function logs di Vercel
- [ ] Pastikan environment variables sudah di-set
- [ ] Test model URL di browser (harus bisa download)
- [ ] Test dengan GET request (harus dapat response)
- [ ] Cek build logs untuk error saat install dependencies
- [ ] Pastikan `requirements.txt` sudah benar

## Common Solutions

### Solution 1: Set Environment Variables

Jika belum set environment variables:

1. Upload model ke GitHub Releases (lihat `GITHUB_RELEASES_GUIDE.md`)
2. Dapatkan direct download URL
3. Set di Vercel:
   - `MODEL_URL` = URL model
   - `SCALER_URL` = URL scaler
4. Redeploy

### Solution 2: Fix Import Error

Jika ada import error, pastikan `requirements.txt`:
```
setuptools>=68.0.0
joblib>=1.3.2
numpy>=1.24.3,<2.0.0
scikit-learn>=1.3.2
```

### Solution 3: Check Code Syntax

Test syntax local:
```bash
python -m py_compile api/predict.py
```

Jika tidak ada error, syntax sudah benar.

## Next Steps

1. **Cek function logs** untuk error detail
2. **Set environment variables** jika belum
3. **Test model URL** di browser
4. **Redeploy** setelah fix

Jika masih error, share function logs dari Vercel untuk debugging lebih lanjut.

