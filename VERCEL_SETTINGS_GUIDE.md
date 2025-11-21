# Panduan Vercel Settings: Build & Output

## Build & Output Settings di Vercel Dashboard

Ketika setup project di Vercel, kamu akan diminta isi beberapa settings. Berikut yang harus diisi:

### 1. Framework Preset
**Pilih:** `Other` atau `Vite` (jika ada opsi Vite)

**Kenapa?** Project ini pakai Vite, tapi Vercel mungkin belum auto-detect. Pilih "Other" kalau tidak ada opsi Vite.

### 2. Root Directory
**Isi:** `.` (titik, artinya root project)

**Atau kosongkan** - biarkan default

### 3. Build Command
**Isi:** 
```
npm run build
```

**Atau:**
```
tsc && vite build
```

**Penjelasan:**
- `npm run build` menjalankan script dari `package.json`
- Script ini akan compile TypeScript (`tsc`) lalu build dengan Vite (`vite build`)

### 4. Output Directory
**Isi:**
```
dist
```

**Penjelasan:**
- Vite secara default output build ke folder `dist/`
- Ini sesuai dengan setting di `vercel.json` (`distDir: "dist"`)

### 5. Install Command
**Isi:** (biarkan default)
```
npm install
```

**Atau kosongkan** - Vercel akan auto-detect

### 6. Development Command (Opsional)
**Isi:** (untuk preview development)
```
npm run dev
```

**Atau kosongkan** - tidak wajib

## Visual Guide di Vercel Dashboard

Ketika import project atau setup baru:

```
┌─────────────────────────────────────┐
│ Framework Preset                     │
│ [Other ▼]                            │
├─────────────────────────────────────┤
│ Root Directory                       │
│ [.                    ]              │
├─────────────────────────────────────┤
│ Build Command                        │
│ [npm run build        ]              │
├─────────────────────────────────────┤
│ Output Directory                     │
│ [dist                 ]              │
├─────────────────────────────────────┤
│ Install Command                      │
│ [npm install          ]              │
└─────────────────────────────────────┘
```

## Auto-Detection

**Good News:** Karena sudah ada `vercel.json`, Vercel sebenarnya bisa auto-detect settings ini!

Tapi kalau auto-detect tidak bekerja atau kamu mau manual setup, gunakan settings di atas.

## Settings yang Sudah Ada di vercel.json

File `vercel.json` sudah mengatur:
- Build command untuk frontend (static build)
- Python serverless function untuk `/api/predict`
- Routing untuk SPA (Single Page Application)
- Max duration untuk function (30 detik)

Jadi sebenarnya Vercel akan otomatis pakai config dari `vercel.json`.

## Checklist Settings

Setelah deploy, pastikan:

- [ ] Build berhasil (cek di Deployments tab)
- [ ] Frontend bisa diakses (homepage load)
- [ ] API endpoint `/api/predict` bisa diakses
- [ ] Environment variables sudah di-set (`MODEL_URL` dan `SCALER_URL`)

## Troubleshooting

### Problem: Build gagal

**Cek:**
1. Build command benar: `npm run build`
2. Output directory benar: `dist`
3. Node version (Vercel auto-detect, biasanya Node 18+)
4. Build logs di Vercel dashboard untuk error detail

### Problem: Frontend tidak load

**Cek:**
1. Output directory sudah benar (`dist`)
2. File `index.html` ada di `dist/`
3. Routing sudah benar (harus redirect semua ke `index.html` untuk SPA)

### Problem: API tidak bekerja

**Cek:**
1. File `api/predict.py` ada
2. Python runtime terdeteksi
3. Environment variables sudah di-set
4. Function logs di Vercel untuk error detail

## Summary: Quick Copy-Paste

Kalau mau cepat, copy-paste ini:

```
Framework Preset: Other
Root Directory: .
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

**Atau biarkan kosong** - Vercel akan auto-detect dari `vercel.json` dan `package.json`!

## Catatan Penting

1. **vercel.json sudah mengatur semuanya** - jadi sebenarnya kamu bisa biarkan auto-detect
2. **Manual setup hanya perlu** kalau auto-detect tidak bekerja
3. **Setelah deploy pertama**, kamu bisa edit settings di: Project → Settings → General

## Next Steps

Setelah settings benar:
1. Deploy project
2. Set environment variables (`MODEL_URL` dan `SCALER_URL`)
3. Test API endpoint
4. Monitor function logs

Selamat deploy! 🚀

