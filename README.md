# Electricity Consumption Prediction — COMPFEST-17

Prediksi konsumsi listrik harian berbasis data cuaca, dibangun untuk seleksi COMPFEST Academy 17.

## Struktur File

| File | Keterangan |
|------|------------|
| `train.csv` | Data pelatihan (fitur + target `electricity_consumption`) |
| `test.csv` | Data uji (fitur saja) |
| `test_seleksi_academy_compfest.ipynb` | Notebook eksplorasi awal |
| `improved_pipeline.py` | Pipeline ML yang sudah diperbaiki ✅ |
| `submission.csv` | Hasil prediksi dari notebook awal |
| `submission_improved.csv` | Hasil prediksi dari pipeline yang diperbaiki |

## Cara Menjalankan Pipeline yang Diperbaiki

### Lokal
```bash
pip install pandas numpy scikit-learn matplotlib seaborn scipy xgboost
python improved_pipeline.py
```

### Google Colab
1. Upload `train.csv`, `test.csv`, dan `improved_pipeline.py` ke Google Drive.
2. Ubah variabel path di bagian **KONFIGURASI**:
   ```python
   TRAIN_PATH = "/content/drive/MyDrive/Test Colab/train.csv"
   TEST_PATH  = "/content/drive/MyDrive/Test Colab/test.csv"
   ```
3. Jalankan sel per sel atau `%run improved_pipeline.py`.

## Perbaikan dari Versi Sebelumnya

| # | Perbaikan |
|---|-----------|
| 1 | Semua import dikumpulkan di satu tempat |
| 2 | Path data tidak hardcoded |
| 3 | Outlier **dideteksi dan di-clip** (sebelumnya hanya dideteksi) |
| 4 | Feature engineering dijadikan fungsi — tidak ada duplikasi kode |
| 5 | Cyclical encoding (sin/cos) untuk bulan & hari |
| 6 | Fitur turunan: `temp_range`, `sunshine_ratio`, `wind_gust_ratio`, dll. |
| 7 | `StandardScaler` di-fit **hanya pada data train** |
| 8 | **6 model** dibandingkan: Linear, Ridge, Lasso, RF, GradientBoosting, XGBoost |
| 9 | Metrik lengkap: **RMSE, MAE, R²** |
| 10 | **5-Fold Cross-Validation** pada model terbaik |
| 11 | Visualisasi **Feature Importance** |
| 12 | Scatter plot **Prediksi vs Aktual** |

## Fitur yang Digunakan

### Fitur Cuaca (dari dataset)
- Suhu maksimum/minimum (aktual & apparent)
- Durasi sinar matahari & daylight
- Kecepatan angin & gusts
- Arah angin dominan
- Radiasi shortwave
- Evapotranspirasi

### Fitur Rekayasa (dari `date`)
| Fitur | Keterangan |
|-------|------------|
| year, month, day | Komponen tanggal |
| dayofweek, dayofyear | Hari dalam minggu/tahun |
| weekofyear, quarter | Minggu ISO & kuartal |
| is_weekend | 1 jika Sabtu/Minggu |
| month_sin/cos | Cyclical encoding bulan |
| dow_sin/cos | Cyclical encoding hari |
| doy_sin/cos | Cyclical encoding hari dalam setahun |

### Fitur Turunan (dari cuaca)
| Fitur | Formula |
|-------|---------|
| temp_range | temp_max − temp_min |
| apparent_temp_range | apparent_max − apparent_min |
| temp_diff_max/min | temp_actual − temp_apparent |
| sunshine_ratio | sunshine_duration / daylight_duration |
| wind_gust_ratio | wind_speed / wind_gusts |

## Cara Menjalankan Dashboard (React & FastAPI)

Proyek ini telah ditambahkan dengan sebuah Dashboard Live bergaya Neobrutalism yang memprediksi cuaca secara langsung menggunakan **FastAPI** dan **React + Vite**. 
Dasbor mengambil data prediksi cuaca (15 hari) dari *Open-Meteo* API menggunakan koordinat untuk berbagai area di DKI Jakarta.

### Prasyarat:
Pastikan Anda memiliki [Node.js](https://nodejs.org/) (untuk React) dan [Python 3.8+](https://www.python.org/) (untuk FastAPI).

### 1. Menjalankan Backend (FastAPI Server)
Buka terminal baru di root direktori proyek, lalu jalankan:
```bash
# Pastikan library terinstall
pip install fastapi uvicorn requests pandas numpy scikit-learn joblib

# Jalankan server API (port 8005)
python -m uvicorn main:app --host 0.0.0.0 --port 8005
```

### 2. Menjalankan Frontend (React App)
Buka terminal lain, arahkan ke folder `energy-dashboard`, lalu jalankan:
```bash
cd energy-dashboard
npm install
npm run dev
```

Buka URL **`http://localhost:5173/`** di peramban (browser) Anda. Anda akan melihat halaman pendaratan utama (*Landing Page*). Klik tombol **Mulai Analisis** untuk masuk ke bagian *Dashboard* cuaca interaktif ⚡.