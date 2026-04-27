# Bike Sharing Analysis Dashboard

Dashboard ini merupakan proyek akhir untuk analisis data penyewaan sepeda menggunakan Bike Sharing Dataset. Proyek ini mencakup seluruh siklus analisis data, mulai dari pembersihan data (Data Cleaning), eksplorasi data (EDA), hingga pembuatan dashboard interaktif menggunakan Streamlit.

## Deskripsi Proyek
Analisis ini bertujuan untuk memberikan wawasan strategis mengenai faktor-faktor yang memengaruhi jumlah penyewaan sepeda harian serta membedakan perilaku antara tipe pengguna:
- Casual (pengguna santai)
- Registered (pengguna terdaftar)

## Struktur Direktori
submission
	/dashboard
	│── dashboard.py 
	│── main_data.csv 
	/data
	│── day.csv 
	│── hour.csv 
	notebook.ipynb 
	requirements.txt 
	README.md 

## Setup Environment

### 1. Membuat Virtual Environment (Disarankan)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate
# Mac/Linux
python -m venv venv
source venv/bin/activate

2. Instalasi Library
Install semua dependensi dengan:
pip install -r requirements.txt

Atau manual:
pip install pandas streamlit plotly scipy matplotlib seaborn
Cara Menjalankan Dashboard

Pastikan berada di folder proyek, lalu jalankan:
streamlit run dashboard.py

⚠️ Catatan Penting
Jika muncul error pada bagian Advanced Analysis (RFM), pastikan sudah menginstall:
pip install scipy

Library scipy diperlukan untuk fungsi seperti gaussian_kde. Tanpa itu, visualisasi akan error.

Setelah benar, akan diarahkan pada:
  Local URL: http://localhost:8501 
  Network URL: http://172.20.10.12:8501 

Pertanyaan Bisnis & Insight
1. Bagaimana pengaruh kondisi lingkungan terhadap penyewaan?
Cuaca cerah mendominasi jumlah penyewaan (~4.876 unit)
Suhu memiliki korelasi positif yang cukup kuat (0.63)
Artinya: semakin hangat suhu, semakin tinggi permintaan sepeda

2. Apa perbedaan pola pengguna Casual vs Registered?
Casual (Santai)
Aktivitas meningkat dari siang hingga sore
Cenderung digunakan untuk rekreasi

Registered (Terdaftar)
Pola komuter (rutinitas kerja)
Puncak penggunaan:
Pagi: sekitar 08.00
Sore: sekitar 17.00

Kesimpulan
Faktor cuaca dan suhu sangat memengaruhi permintaan
Terdapat perbedaan pola perilaku yang jelas antara pengguna casual dan registered
Data ini dapat dimanfaatkan untuk:
Optimasi jumlah sepeda
Strategi operasional berbasis waktu & cuaca