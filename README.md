E-Tahfizh: Sistem Informasi Manajemen Hafalan Al-Qur'an

E-Tahfizh adalah aplikasi berbasis web yang dirancang untuk mendigitalisasi proses administrasi dan monitoring hafalan santri di Taman Pendidikan Al-Qur'an (TPQ). Sistem ini menggantikan kartu prestasi manual, memudahkan Ustadz dalam pencatatan setoran hafalan, serta memberikan transparansi perkembangan anak kepada Wali Santri secara real-time.

Project ini dikembangkan sebagai bagian dari program Kuliah Kerja Nyata (KKN) di [Nama Lokasi KKN Anda].

🌟 Fitur Unggulan

🔐 Multi-User Role

Admin: Mengelola data induk (Santri, Ustadz, Kelas) dan konfigurasi sistem.

Ustadz: Mencatat aktivitas harian (Setoran & Absensi) via Smartphone.

Wali Santri: Memantau grafik perkembangan dan absensi anak dari rumah.

📚 Manajemen Akademik

Input Setoran: Mencatat Ziyadah (hafalan baru) dan Murajaah dengan penilaian tajwid (Mumtaz/Jayyid/dll).

Absensi Digital: Presensi harian (Hadir/Sakit/Izin/Alpha) yang terintegrasi dengan laporan.

Gamifikasi Prestasi: Pencatatan penghargaan (Achievement) untuk memotivasi santri.

📊 Laporan & Monitoring

Dashboard Statistik: Ringkasan total hafalan dan keaktifan santri.

Portal Wali Santri: Halaman pencarian publik bagi orang tua untuk cek progres anak tanpa login rumit.

Cetak Rapor: Generate laporan hasil belajar otomatis siap cetak (PDF) lengkap dengan tanda tangan.

Integrasi WhatsApp: Kirim ringkasan laporan ke orang tua via WhatsApp dengan sekali klik.

🛠️ Teknologi yang Digunakan

Backend: Python (Flask Microframework), SQLAlchemy ORM.

Database: MySQL / MariaDB.

Frontend: HTML5, CSS3, Bootstrap 5 (Responsive Mobile-First).

Tools: VS Code, XAMPP, Git.

📸 Tangkapan Layar (Screenshots)

<!-- Anda bisa mengganti link gambar di bawah ini dengan screenshot asli aplikasi Anda -->

Dashboard Ustadz

Input Setoran





Portal Wali Santri

Laporan Cetak





🚀 Cara Instalasi (Localhost)

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer lokal Anda:

1. Persiapan Lingkungan

Pastikan sudah menginstall:

Python 3.x

XAMPP (untuk database MySQL)

Git

2. Clone Repository

Buka terminal/CMD, lalu jalankan:

git clone [https://github.com/USERNAME_GITHUB_ANDA/nama-repo-anda.git](https://github.com/USERNAME_GITHUB_ANDA/nama-repo-anda.git)
cd nama-repo-anda


3. Setup Virtual Environment (Disarankan)

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate


4. Install Dependencies

Install library Python yang dibutuhkan:

pip install -r requirements.txt


(Jika file requirements.txt belum ada, install manual: pip install flask flask-sqlalchemy flask-login mysql-connector-python)

5. Konfigurasi Database

Nyalakan Apache dan MySQL di XAMPP Control Panel.

Buka phpMyAdmin (http://localhost/phpmyadmin).

Buat database baru dengan nama: db_etahfiz (atau sesuaikan dengan config di app.py).

Pastikan konfigurasi database di app.py sudah benar:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/db_etahfiz'


Inisialisasi Tabel Database:
Buka terminal di folder proyek, lalu ketik:

python
>>> from app import db, app
>>> with app.app_context(): db.create_all()
>>> exit()


6. Jalankan Aplikasi

python app.py


Buka browser dan akses alamat: http://localhost:5000

👤 Akun Demo (Default)

Gunakan akun berikut untuk login pertama kali (jika Anda menggunakan data dummy):

Role

Username

Password

Admin

admin

admin123

Ustadz

guru

guru123

(Catatan: Anda mungkin perlu membuat user admin pertama kali secara manual lewat database atau script register)

🤝 Kontribusi

Project ini dikembangkan untuk tujuan pengabdian masyarakat. Masukan dan saran sangat diterima untuk pengembangan fitur selanjutnya.

Tim KKN Mahasiswa [Nama Universitas Anda]
Tahun 2025