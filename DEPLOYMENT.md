# Deployment Guide - Large Model (500MB)

## Masalah
Model `rf_cardio_model.joblib` berukuran ~500MB, melebihi limit Vercel:
- Free tier: 50MB
- Pro tier: 250MB
- Enterprise: bisa lebih besar

## Solusi: External Storage

Kita akan menyimpan model di external storage (S3, Google Cloud Storage, dll) dan load saat runtime.

### Opsi 1: Google Cloud Storage (Recommended)

1. **Upload model ke Google Cloud Storage:**
```bash
# Install gcloud CLI
# Upload model
gsutil cp model/rf_cardio_model.joblib gs://your-bucket-name/models/
gsutil cp model/scaler_cardio.joblib gs://your-bucket-name/models/

# Buat public URL atau signed URL
# Public URL format: https://storage.googleapis.com/your-bucket-name/models/rf_cardio_model.joblib
```

2. **Set Environment Variables di Vercel:**
```
MODEL_URL=https://storage.googleapis.com/your-bucket-name/models/rf_cardio_model.joblib
SCALER_URL=https://storage.googleapis.com/your-bucket-name/models/scaler_cardio.joblib
```

### Opsi 2: AWS S3

1. **Upload model ke S3:**
```bash
aws s3 cp model/rf_cardio_model.joblib s3://your-bucket-name/models/
aws s3 cp model/scaler_cardio.joblib s3://your-bucket-name/models/

# Buat public URL atau presigned URL
```

2. **Set Environment Variables di Vercel:**
```
MODEL_URL=https://your-bucket-name.s3.amazonaws.com/models/rf_cardio_model.joblib
SCALER_URL=https://your-bucket-name.s3.amazonaws.com/models/scaler_cardio.joblib
```

### Opsi 3: GitHub Releases (Free, Recommended untuk Quick Start)

**📖 Lihat panduan lengkap di: [GITHUB_RELEASES_GUIDE.md](./GITHUB_RELEASES_GUIDE.md)**

Quick steps:
1. Buat release di GitHub (Releases → Create a new release)
2. Upload model files sebagai release assets
3. Dapatkan direct download URL
4. Set sebagai environment variables di Vercel

**Format URL:**
```
MODEL_URL=https://github.com/your-username/your-repo/releases/download/v1.0.0/rf_cardio_model.joblib
SCALER_URL=https://github.com/your-username/your-repo/releases/download/v1.0.0/scaler_cardio.joblib
```

### Opsi 4: Cloudinary / Other CDN

Bisa juga pakai Cloudinary atau CDN lain yang support file besar.

## Setup di Vercel

1. **Set Environment Variables:**
   - Masuk ke Vercel Dashboard
   - Pilih project
   - Settings → Environment Variables
   - Tambahkan:
     - `MODEL_URL` = URL ke model file
     - `SCALER_URL` = URL ke scaler file

2. **Deploy:**
```bash
vercel --prod
```

## Catatan Penting

- **Cold Start:** Model akan di-download saat pertama kali function dipanggil (cold start). Ini bisa memakan waktu 5-10 detik.
- **Caching:** Vercel akan cache model di memory untuk beberapa waktu, jadi request berikutnya akan lebih cepat.
- **Cost:** Download dari external storage akan ada biaya bandwidth, tapi biasanya sangat murah.
- **Security:** Untuk production, gunakan signed URLs atau private storage dengan authentication.

## Development (Local)

Untuk development local, model akan otomatis di-load dari folder `model/` jika `MODEL_URL` dan `SCALER_URL` tidak di-set.

## Alternative: Reduce Model Size

Jika ingin tetap pakai model di repo, pertimbangkan:
1. **Quantize model** - reduce precision (float64 → float32)
2. **Reduce n_estimators** - kurangi jumlah trees di Random Forest
3. **Use smaller model** - train ulang dengan parameter yang lebih kecil

Tapi ini akan mengurangi akurasi model.

