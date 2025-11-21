# Cardiovascular Dashboard

Dashboard analitik dan prediksi untuk penyakit cardiovascular menggunakan React, Vite, dan Python serverless functions di Vercel.

## Fitur

- 📊 **Analytics Page**: Visualisasi data dari Looker Studio
- 🔮 **Predict Page**: Prediksi risiko cardiovascular disease menggunakan machine learning model

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python serverless functions (Vercel)
- **ML Model**: Random Forest (scikit-learn)
- **Deployment**: Vercel

## Setup Development

1. Install dependencies:
```bash
npm install
```

2. Jalankan development server:
```bash
npm run dev
```

3. Buka browser di `http://localhost:5173`

## Setup Looker Studio Embed

1. Buka file `src/pages/Analytics.tsx`
2. Ganti `lookerStudioUrl` dengan embed URL dari Looker Studio kamu
3. Format URL: `https://lookerstudio.google.com/embed/reporting/YOUR_REPORT_ID/page/YOUR_PAGE_ID`

## Deploy ke Vercel

1. Install Vercel CLI (jika belum):
```bash
npm i -g vercel
```

2. Login ke Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

Atau langsung push ke GitHub dan connect ke Vercel dari dashboard.

## Struktur Project

```
.
├── api/
│   └── predict.py          # Serverless function untuk predict
├── model/
│   ├── rf_cardio_model.joblib
│   └── scaler_cardio.joblib
├── src/
│   ├── components/
│   │   └── Navbar.tsx
│   ├── pages/
│   │   ├── Analytics.tsx
│   │   └── Predict.tsx
│   ├── App.tsx
│   └── main.tsx
├── vercel.json
├── requirements.txt
└── package.json
```

## Catatan Penting

### Model Size & Deployment

Model `rf_cardio_model.joblib` berukuran ~500MB, melebihi limit Vercel (Free: 50MB, Pro: 250MB).

**Solusi: Gunakan External Storage**

1. Upload model ke external storage (Google Cloud Storage, AWS S3, atau GitHub Releases)
2. Set environment variables di Vercel:
   - `MODEL_URL` = URL ke model file
   - `SCALER_URL` = URL ke scaler file
3. Model akan di-download otomatis saat pertama kali function dipanggil

**Untuk Development Local:**
- Model akan otomatis di-load dari folder `model/` jika environment variables tidak di-set

Lihat `DEPLOYMENT.md` untuk panduan lengkap setup external storage.

### Lainnya

- Pastikan urutan features di `api/predict.py` sesuai dengan training data
- Model menggunakan 19 features dengan feature engineering otomatis

## API Endpoint

### POST `/api/predict`

Request body:
```json
{
  "age": 50,
  "gender": 2,
  "height": 170,
  "weight": 70,
  "ap_hi": 120,
  "ap_lo": 80,
  "cholesterol": 1,
  "gluc": 1,
  "smoke": 0,
  "alco": 0,
  "active": 1
}
```

Response:
```json
{
  "prediction": 0,
  "probability": 0.23
}
```

