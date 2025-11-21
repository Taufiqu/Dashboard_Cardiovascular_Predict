# Panduan Lengkap: Upload Model ke GitHub Releases

## Apa itu GitHub Releases?

GitHub Releases adalah fitur GitHub untuk mengupload file besar (sampai 2GB per file) sebagai "release asset". Ini cocok untuk menyimpan model ML yang besar tanpa membuat repository kamu jadi berat.

## Keuntungan GitHub Releases

✅ **Gratis** - Tidak perlu bayar  
✅ **Mudah** - Langsung dari GitHub web interface  
✅ **Public URL** - Langsung dapat direct download URL  
✅ **Versioning** - Bisa buat multiple releases untuk versioning model  
✅ **Tidak membebani repo** - File tidak masuk ke git history  

## Langkah-langkah Detail

### Step 1: Siapkan Model Files

Pastikan kamu punya 2 file:
- `rf_cardio_model.joblib` (~500MB)
- `scaler_cardio.joblib` (biasanya kecil, beberapa KB)

### Step 2: Buat Release di GitHub

1. **Buka repository GitHub kamu** di browser
   - Contoh: `https://github.com/username/Dashboard_Cardiovascular_Predict`

2. **Klik tombol "Releases"** di sidebar kanan
   - Atau langsung ke: `https://github.com/username/Dashboard_Cardiovascular_Predict/releases`

3. **Klik "Create a new release"** (atau "Draft a new release")

### Step 3: Isi Informasi Release

1. **Choose a tag:**
   - Klik "Choose tag" → ketik tag baru, misalnya: `v1.0.0`
   - Atau pilih tag yang sudah ada
   - **Tip:** Tag format biasanya `v1.0.0`, `v1.0.1`, dll

2. **Release title:**
   - Contoh: `Cardiovascular Model v1.0.0`
   - Atau: `Initial Model Release`

3. **Description (opsional):**
   ```
   Initial release of cardiovascular disease prediction model.
   
   Files included:
   - rf_cardio_model.joblib (Random Forest model)
   - scaler_cardio.joblib (StandardScaler)
   ```

4. **Pilih "Set as the latest release"** (centang ini)

### Step 4: Upload Model Files

1. **Scroll ke bagian "Attach binaries"**

2. **Drag & drop atau klik untuk upload:**
   - Upload `rf_cardio_model.joblib`
   - Upload `scaler_cardio.joblib`
   
   **Note:** Upload bisa memakan waktu beberapa menit untuk file 500MB

3. **Tunggu sampai upload selesai** (akan muncul progress bar)

### Step 5: Publish Release

1. **Klik tombol "Publish release"** (hijau di kanan bawah)

2. **Tunggu sampai release terpublish**

### Step 6: Dapatkan Direct Download URL

Setelah release terpublish, kamu akan dapat URL untuk download file:

1. **Klik pada file yang sudah di-upload** (misalnya `rf_cardio_model.joblib`)

2. **Copy URL dari browser address bar**, atau:

3. **Klik kanan pada file → "Copy link address"**

   Format URL akan seperti ini:
   ```
   https://github.com/username/Dashboard_Cardiovascular_Predict/releases/download/v1.0.0/rf_cardio_model.joblib
   https://github.com/username/Dashboard_Cardiovascular_Predict/releases/download/v1.0.0/scaler_cardio.joblib
   ```

   **PENTING:** URL ini adalah direct download link yang bisa langsung dipakai!

### Step 7: Set Environment Variables di Vercel

1. **Buka Vercel Dashboard:**
   - Login ke https://vercel.com
   - Pilih project kamu

2. **Masuk ke Settings:**
   - Klik project → Settings → Environment Variables

3. **Tambahkan 2 environment variables:**

   **Variable 1:**
   - Name: `MODEL_URL`
   - Value: `https://github.com/username/Dashboard_Cardiovascular_Predict/releases/download/v1.0.0/rf_cardio_model.joblib`
   - Environment: Production, Preview, Development (centang semua)

   **Variable 2:**
   - Name: `SCALER_URL`
   - Value: `https://github.com/username/Dashboard_Cardiovascular_Predict/releases/download/v1.0.0/scaler_cardio.joblib`
   - Environment: Production, Preview, Development (centang semua)

4. **Klik "Save"**

### Step 8: Redeploy di Vercel

Setelah set environment variables:

1. **Redeploy project:**
   ```bash
   vercel --prod
   ```
   
   Atau dari Vercel Dashboard:
   - Klik "Deployments" → "Redeploy" pada deployment terbaru

2. **Test API:**
   - Coba hit endpoint `/api/predict` 
   - Request pertama mungkin lambat (cold start + download model)
   - Request berikutnya akan lebih cepat

## Tips & Best Practices

### 1. Versioning Model

Saat update model, buat release baru dengan tag berbeda:
- `v1.0.0` - Initial release
- `v1.1.0` - Updated model
- `v2.0.0` - Major update

Update environment variables di Vercel dengan URL release baru.

### 2. Private Repository

Jika repository private:
- URL masih bisa diakses langsung (tidak perlu authentication)
- Tapi hanya orang yang punya akses ke repo yang bisa download
- Untuk public access, perlu buat repository public atau gunakan storage lain

### 3. File Size Limit

- GitHub Releases: **2GB per file** (cukup untuk model 500MB)
- Total release size: Tidak ada limit yang jelas, tapi praktisnya sampai beberapa GB

### 4. Alternative: GitHub LFS

Jika file lebih dari 2GB, bisa pakai **GitHub LFS (Large File Storage)**:
- Tapi ini lebih kompleks dan ada limit untuk free tier
- GitHub Releases lebih simple untuk use case ini

## Troubleshooting

### Problem: Upload gagal atau timeout

**Solusi:**
- Coba upload lagi
- Pastikan koneksi internet stabil
- Upload satu per satu (jangan sekaligus)

### Problem: URL tidak bisa diakses

**Solusi:**
- Pastikan release sudah "Published" (bukan draft)
- Pastikan URL format benar (harus ada `/releases/download/`)
- Coba buka URL langsung di browser untuk test

### Problem: Model tidak ter-load di Vercel

**Solusi:**
- Pastikan environment variables sudah di-set dengan benar
- Pastikan URL bisa diakses (test di browser)
- Cek Vercel function logs untuk error message
- Pastikan format URL benar (harus direct download link)

### Problem: Cold start terlalu lama

**Solusi:**
- Ini normal untuk pertama kali (model 500MB perlu waktu download)
- Vercel akan cache model di memory
- Request berikutnya akan lebih cepat
- Pertimbangkan keep-alive atau warm-up function

## Contoh URL Format

```
✅ BENAR:
https://github.com/username/repo-name/releases/download/v1.0.0/rf_cardio_model.joblib

❌ SALAH:
https://github.com/username/repo-name/releases/tag/v1.0.0
https://github.com/username/repo-name/releases
```

## Checklist Deploy

- [ ] Model files sudah siap (`rf_cardio_model.joblib` dan `scaler_cardio.joblib`)
- [ ] Release sudah dibuat di GitHub
- [ ] Model files sudah di-upload ke release
- [ ] Release sudah di-publish
- [ ] Direct download URL sudah didapat
- [ ] Environment variables sudah di-set di Vercel (`MODEL_URL` dan `SCALER_URL`)
- [ ] Project sudah di-redeploy di Vercel
- [ ] API sudah di-test dan berfungsi

## Next Steps

Setelah setup selesai:
1. Test API endpoint `/api/predict`
2. Monitor Vercel function logs untuk memastikan model ter-load dengan benar
3. Test dengan berbagai input untuk memastikan prediksi akurat

Selamat! Model kamu sekarang sudah bisa di-deploy di Vercel tanpa masalah size limit! 🎉

