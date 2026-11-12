# Bike Sharing Data Analysis Dashboard 🚲

Proyek analisis data penyewaan sepeda **Capital Bikeshare (Washington D.C., 2011–2012)**.
Analisis menjawab tiga pertanyaan bisnis (SMART):

1. Pada jam berapa puncak penyewaan terjadi di hari kerja vs akhir pekan/libur?
2. Seberapa besar pengaruh musim dan kondisi cuaca terhadap penyewaan harian?
3. Berapa pertumbuhan penyewaan 2012 vs 2011 (YoY), dan tipe pengguna mana yang tumbuh lebih cepat?

## Struktur Direktori

```
submission
├── dashboard
│   ├── main_data.csv      # data per jam (sudah bersih)
│   ├── day_data.csv       # data harian (sudah bersih)
│   └── dashboard.py       # aplikasi Streamlit
├── data
│   ├── day.csv            # data mentah harian
│   └── hour.csv           # data mentah per jam
├── notebook.ipynb         # proses analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                # tautan dashboard di Streamlit Cloud
```

## Setup Environment

Disarankan menggunakan Python 3.9 atau lebih baru.

**Shell / Terminal (venv)**
```
cd submission
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Anaconda**
```
conda create --name bike-ds python=3.11
conda activate bike-ds
pip install -r requirements.txt
```

## Menjalankan Dashboard

```
cd submission
streamlit run dashboard/dashboard.py
```

Dashboard akan terbuka di `http://localhost:8501`. Fitur: filter rentang tanggal & tipe hari, KPI ringkas,
dan empat tab (Pola per Jam, Musim & Cuaca, Tren Bulanan, Analisis Lanjutan).

## Menjalankan Notebook

Buka `notebook.ipynb` dengan Jupyter/VS Code/Colab dan jalankan seluruh sel dari atas ke bawah.
Sel terakhir pada tahap *Cleaning Data* akan membuat ulang `dashboard/main_data.csv` dan `dashboard/day_data.csv`.
(Di Colab, unggah folder `data/` terlebih dahulu.)

## Deploy ke Streamlit Community Cloud

1. Unggah folder `submission` ke repositori GitHub.
2. Di https://share.streamlit.io pilih *New app*, lalu atur **Main file path** ke `dashboard/dashboard.py`.
3. Salin URL aplikasi ke `url.txt`.

## Sumber Data

Fanaee-T, H. & Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence.
Data: Capital Bikeshare System & freemeteo.com.
