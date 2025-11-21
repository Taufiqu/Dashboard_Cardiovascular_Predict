# Quick Start: GitHub Releases (5 Menit)

## TL;DR - Langkah Cepat

1. **Buka GitHub repo** → Klik "Releases" → "Create a new release"
2. **Tag:** `v1.0.0`, **Title:** `Model Release`
3. **Upload 2 files:** `rf_cardio_model.joblib` dan `scaler_cardio.joblib`
4. **Publish release**
5. **Copy URL** dari file yang di-upload (klik file → copy URL dari address bar)
6. **Set di Vercel:** Environment Variables → Tambah `MODEL_URL` dan `SCALER_URL`
7. **Redeploy**

## Visual Guide

### Step 1: Buka Releases Page
```
GitHub Repo → Sidebar Kanan → "Releases"
atau langsung: github.com/username/repo/releases
```

### Step 2: Create Release
```
Klik "Create a new release" atau "Draft a new release"
```

### Step 3: Isi Form
```
Tag: v1.0.0
Title: Cardiovascular Model v1.0.0
Description: (opsional)
☑ Set as the latest release
```

### Step 4: Upload Files
```
Scroll ke "Attach binaries"
Drag & drop atau klik:
  - rf_cardio_model.joblib
  - scaler_cardio.joblib
Tunggu upload selesai (beberapa menit untuk 500MB)
```

### Step 5: Publish
```
Klik "Publish release" (tombol hijau)
```

### Step 6: Dapatkan URL
```
Setelah publish, klik pada file yang di-upload
Copy URL dari browser address bar

Contoh URL:
https://github.com/username/repo/releases/download/v1.0.0/rf_cardio_model.joblib
https://github.com/username/repo/releases/download/v1.0.0/scaler_cardio.joblib
```

### Step 7: Set di Vercel
```
Vercel Dashboard → Project → Settings → Environment Variables

Tambahkan:
MODEL_URL = https://github.com/.../rf_cardio_model.joblib
SCALER_URL = https://github.com/.../scaler_cardio.joblib

☑ Production
☑ Preview  
☑ Development

Save
```

### Step 8: Redeploy
```bash
vercel --prod
```

## Format URL yang Benar

✅ **BENAR:**
```
https://github.com/username/repo/releases/download/v1.0.0/rf_cardio_model.joblib
```

❌ **SALAH:**
```
https://github.com/username/repo/releases/tag/v1.0.0
https://github.com/username/repo/releases
https://github.com/username/repo/blob/main/model/rf_cardio_model.joblib
```

**Ciri URL yang benar:**
- Ada `/releases/download/`
- Ada tag version (`v1.0.0`)
- Ada nama file di akhir

## Troubleshooting Cepat

**Q: Upload gagal?**  
A: Coba lagi, pastikan koneksi stabil, upload satu per satu

**Q: URL tidak bisa diakses?**  
A: Pastikan release sudah "Published" (bukan draft), test buka URL di browser

**Q: Model tidak ter-load?**  
A: Cek environment variables sudah benar, cek Vercel logs, pastikan URL format benar

**Q: Cold start lama?**  
A: Normal untuk pertama kali (download 500MB), request berikutnya lebih cepat

## Checklist

- [ ] Release dibuat dan di-publish
- [ ] 2 files sudah di-upload
- [ ] URL sudah di-copy (format benar)
- [ ] Environment variables sudah di-set di Vercel
- [ ] Project sudah di-redeploy
- [ ] API sudah di-test

**Lebih detail? Lihat [GITHUB_RELEASES_GUIDE.md](./GITHUB_RELEASES_GUIDE.md)**

