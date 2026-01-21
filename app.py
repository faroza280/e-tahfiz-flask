import os
import time
import json
from datetime import datetime, date, timedelta
from functools import wraps
from io import BytesIO 
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from sqlalchemy.sql import func, extract
import pymysql
from xhtml2pdf import pisa 
import openpyxl 
from openpyxl.styles import Font, PatternFill, Alignment

app = Flask(__name__)

# --- 1. KONFIGURASI APLIKASI ---
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_tahfizh'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'rahasia-super-aman-123' 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- 2. SETUP LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- 3. MODEL DATABASE ---

class Konfigurasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_tpq = db.Column(db.String(100), default="TPQ Al-Ikhlas")
    alamat_tpq = db.Column(db.String(200), default="Jl. Hidayah No. 1, Kota Santri")
    target_bulanan = db.Column(db.Integer, default=150)
    def to_dict(self): return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Ustadz(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20), default='ustadz')
    status = db.Column(db.String(20), default='Aktif')
    
    santri = db.relationship('Santri', backref='ustadz', lazy=True)
    setoran = db.relationship('Setoran', backref='ustadz', lazy=True)
    absensi = db.relationship('Absensi', backref='ustadz', lazy=True) # Relasi Baru
    
    def to_dict(self): return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Santri(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kelas = db.Column(db.String(50))
    foto = db.Column(db.String(255), nullable=True) 
    status = db.Column(db.String(20), default='Aktif')
    ustadz_id = db.Column(db.Integer, db.ForeignKey('ustadz.id'), nullable=False)
    
    setoran = db.relationship('Setoran', backref='santri', lazy=True, cascade="all, delete-orphan")
    absensi = db.relationship('Absensi', backref='santri', lazy=True, cascade="all, delete-orphan") # Relasi Baru
    
    def to_dict(self): return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Setoran(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), nullable=False)
    ustadz_id = db.Column(db.Integer, db.ForeignKey('ustadz.id'), nullable=False)
    surat = db.Column(db.String(100), nullable=False)
    ayat_awal = db.Column(db.Integer, nullable=False)
    ayat_akhir = db.Column(db.Integer, nullable=False)
    kualitas = db.Column(db.String(10), nullable=False)
    catatan = db.Column(db.Text, nullable=True)
    tanggal = db.Column(db.DateTime(timezone=True), server_default=func.now())
    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if d['tanggal']: d['tanggal'] = d['tanggal'].strftime('%Y-%m-%d %H:%M:%S')
        return d

# MODEL BARU: ABSENSI
class Absensi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    santri_id = db.Column(db.Integer, db.ForeignKey('santri.id'), nullable=False)
    ustadz_id = db.Column(db.Integer, db.ForeignKey('ustadz.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False) # Hadir, Sakit, Izin, Alpha
    keterangan = db.Column(db.String(255), nullable=True)
    tanggal = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if d['tanggal']: d['tanggal'] = d['tanggal'].strftime('%Y-%m-%d %H:%M:%S')
        return d

@login_manager.user_loader
def load_user(user_id):
    return Ustadz.query.get(int(user_id))

@app.context_processor
def inject_config():
    config = Konfigurasi.query.first()
    if not config: config = Konfigurasi(nama_tpq="E-Tahfizh", alamat_tpq="-", target_bulanan=150)
    return dict(config_tpq=config)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Akses ditolak! Halaman ini khusus Administrator.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES AUTH ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        user = Ustadz.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            if user.status != 'Aktif':
                flash('Akun Nonaktif.', 'danger'); return redirect(url_for('login'))
            login_user(user)
            flash(f'Ahlan, {user.nama}!', 'success')
            return redirect(url_for('index'))
        else: flash('Login gagal.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout(): logout_user(); flash('Anda telah keluar.', 'info'); return redirect(url_for('login'))

# --- ROUTES UTAMA ---
@app.route('/')
@login_required
def index():
    total_santri = Santri.query.filter_by(status='Aktif').count()
    hari_ini = datetime.now().date()
    setoran_hari_ini = Setoran.query.filter(func.date(Setoran.tanggal) == hari_ini).count()
    # Hitung Absensi Hari Ini (Fitur Baru)
    absensi_hari_ini = Absensi.query.filter(func.date(Absensi.tanggal) == hari_ini).count()
    total_ayat_global = db.session.query(func.sum(Setoran.ayat_akhir - Setoran.ayat_awal + 1)).scalar() or 0
    
    bulan_ini = datetime.now().month
    subquery = db.session.query(Setoran.santri_id, func.count(Setoran.id).label('jumlah_setor')).filter(extract('month', Setoran.tanggal) == bulan_ini).group_by(Setoran.santri_id).subquery()
    top_santri_data = db.session.query(Santri).join(subquery, Santri.id == subquery.c.santri_id).order_by(subquery.c.jumlah_setor.desc()).first()

    labels_grafik, data_grafik = [], []
    for i in range(6, -1, -1):
        tgl = hari_ini - timedelta(days=i)
        jml = Setoran.query.filter(func.date(Setoran.tanggal) == tgl).count()
        labels_grafik.append(tgl.strftime('%d/%m'))
        data_grafik.append(jml)
    
    santri_binaan = []
    if current_user.role == 'ustadz':
        santri_binaan = Santri.query.filter_by(ustadz_id=current_user.id, status='Aktif').all()
    
    return render_template('dashboard.html', total_santri=total_santri, setoran_hari_ini=setoran_hari_ini, absensi_hari_ini=absensi_hari_ini, total_ayat_global=total_ayat_global, top_santri=top_santri_data, labels_grafik=labels_grafik, data_grafik=data_grafik, santri_binaan=santri_binaan, active_page='dashboard')

# --- ROUTE UNTUK FITUR ABSENSI (Tambahkan di app.py) ---

@app.route('/absensi', methods=['GET', 'POST'])
@login_required
def halaman_absensi():
    # 1. Logika Penyimpanan Data (POST)
    if request.method == 'POST':
        santri_id = request.form.get('santri_id')
        status = request.form.get('status') # Hadir, Sakit, Izin, Alpha
        keterangan = request.form.get('keterangan')
        
        # Validasi sederhana
        if not santri_id or not status:
            flash('Harap pilih Santri dan Status Kehadiran!', 'warning')
            return redirect(url_for('halaman_absensi'))

        # Cek Duplikasi: Apakah santri ini SUDAH diabsen hari ini?
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        existing_absen = Absensi.query.filter(
            Absensi.santri_id == santri_id,
            Absensi.tanggal >= today_start
        ).first()

        if existing_absen:
            # Jika sudah ada, Update saja datanya
            existing_absen.status = status
            existing_absen.keterangan = keterangan
            existing_absen.ustadz_id = current_user.id # Update siapa yang mengabsen terakhir
            flash('Data absensi hari ini berhasil diperbarui.', 'info')
        else:
            # Jika belum, Buat Baru
            absen_baru = Absensi(
                santri_id=santri_id,
                ustadz_id=current_user.id, # Ambil ID Ustadz yang sedang login
                status=status,
                keterangan=keterangan
            )
            db.session.add(absen_baru)
            flash('Absensi berhasil disimpan.', 'success')
        
        db.session.commit()
        return redirect(url_for('halaman_absensi'))

    # 2. Logika Tampilan (GET)
    # Ambil daftar santri aktif (bisa difilter per ustadz jika perlu)
    if current_user.role == 'admin':
        santri_list = Santri.query.filter_by(status='Aktif').all()
    else:
        # Jika Ustadz biasa, hanya tampilkan santri binaannya saja
        santri_list = Santri.query.filter_by(status='Aktif', ustadz_id=current_user.id).all()
    
    # Ambil riwayat absensi HARI INI untuk ditampilkan di tabel bawah
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Query riwayat (Join agar bisa ambil nama santri)
    riwayat_hari_ini = db.session.query(Absensi, Santri).join(Santri, Absensi.santri_id == Santri.id)\
        .filter(Absensi.tanggal >= today_start).all()

    return render_template('absensi.html', santri_list=santri_list, riwayat=riwayat_hari_ini)

@app.route('/absensi/delete/<int:id>', methods=['POST'])
@login_required
def delete_absensi(id):
    data = Absensi.query.get_or_404(id)
    # Proteksi: Hanya admin atau pembuat data yang bisa hapus
    if current_user.role != 'admin' and data.ustadz_id != current_user.id:
        flash('Anda tidak memiliki akses menghapus data ini.', 'danger')
        return redirect(url_for('halaman_absensi'))
        
    db.session.delete(data)
    db.session.commit()
    flash('Data absensi dihapus.', 'success')
    return redirect(url_for('halaman_absensi'))

# ... (ROUTE ADMIN, SANTRI, SETORAN, DLL TETAP SAMA) ...
# SAYA TULIS ULANG AGAR COPY PASTE AMAN:

@app.route('/admin/ustadz')
@login_required
@admin_required
def admin_ustadz(): return render_template('admin_ustadz.html', semua_ustadz=Ustadz.query.all(), active_page='admin_ustadz')

@app.route('/admin/ustadz/tambah', methods=['POST'])
@login_required
@admin_required
def tambah_ustadz():
    if Ustadz.query.filter_by(username=request.form.get('username')).first():
        flash('Username dipakai.', 'warning'); return redirect(url_for('admin_ustadz'))
    pw = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
    db.session.add(Ustadz(nama=request.form.get('nama'), username=request.form.get('username'), password=pw, role=request.form.get('role'), status='Aktif'))
    db.session.commit(); flash('Sukses tambah ustadz.', 'success'); return redirect(url_for('admin_ustadz'))

@app.route('/admin/ustadz/edit/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_ustadz(id):
    u = Ustadz.query.get_or_404(id)
    u.nama = request.form.get('nama'); u.username = request.form.get('username'); u.role = request.form.get('role'); u.status = request.form.get('status')
    if request.form.get('password'): u.password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256')
    try: db.session.commit(); flash('Update sukses.', 'success')
    except: db.session.rollback(); flash('Gagal update.', 'danger')
    return redirect(url_for('admin_ustadz'))

@app.route('/admin/ustadz/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_ustadz(id):
    if id == current_user.id: flash('Tidak bisa hapus diri sendiri.', 'warning'); return redirect(url_for('admin_ustadz'))
    u = Ustadz.query.get_or_404(id)
    # Pindahkan setoran ke admin lain dulu
    admin_lain = current_user.id
    if u.santri: flash('Gagal: Ustadz ini masih punya santri.', 'warning')
    else: 
        try:
            Setoran.query.filter_by(ustadz_id=id).update(dict(ustadz_id=admin_lain))
            Absensi.query.filter_by(ustadz_id=id).update(dict(ustadz_id=admin_lain)) # Pindahkan absensi juga
            db.session.commit()
            db.session.delete(u); db.session.commit(); flash('Ustadz dihapus.', 'success')
        except: db.session.rollback()
    return redirect(url_for('admin_ustadz'))

@app.route('/santri')
@login_required
def halaman_santri():
    kw = request.args.get('q'); cls = request.args.get('kelas'); sts = request.args.get('status', 'Aktif')
    q = Santri.query
    if kw: q = q.filter((Santri.nama.like(f"%{kw}%")) | (Santri.kelas.like(f"%{kw}%")))
    if cls: q = q.filter(Santri.kelas == cls)
    if sts != 'Semua': q = q.filter(Santri.status == sts)
    kelas_list = [k[0] for k in db.session.query(Santri.kelas).distinct().order_by(Santri.kelas).all() if k[0]]
    return render_template('santri.html', semua_santri=q.all(), active_page='santri', daftar_kelas=kelas_list, kelas_pilih=cls, status_pilih=sts)

@app.route('/santri/tambah', methods=['GET', 'POST'])
@login_required
@admin_required
def tambah_santri():
    if request.method == 'POST':
        file = request.files.get('foto'); fname = None
        if file and allowed_file(file.filename):
            fname = f"{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
        db.session.add(Santri(nama=request.form.get('nama'), kelas=request.form.get('kelas'), ustadz_id=int(request.form.get('ustadz_id')), foto=fname, status='Aktif'))
        db.session.commit(); flash('Santri ditambah.', 'success'); return redirect(url_for('halaman_santri'))
    return render_template('tambah_santri.html', semua_ustadz=Ustadz.query.filter_by(status='Aktif').all(), active_page='santri')

@app.route('/santri/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_santri(id):
    s = Santri.query.get_or_404(id)
    if request.method == 'POST':
        s.nama = request.form.get('nama'); s.kelas = request.form.get('kelas'); s.ustadz_id = int(request.form.get('ustadz_id'))
        file = request.files.get('foto')
        if file and allowed_file(file.filename):
            if s.foto: 
                try: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], s.foto))
                except: pass
            s.foto = f"{int(time.time())}_{secure_filename(file.filename)}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], s.foto))
        db.session.commit(); flash('Santri diupdate.', 'success'); return redirect(url_for('halaman_santri'))
    return render_template('edit_santri.html', santri=s, semua_ustadz=Ustadz.query.filter_by(status='Aktif').all(), active_page='santri')

@app.route('/santri/hapus/<int:id>', methods=['POST'])
@login_required
@admin_required
def hapus_santri(id):
    s = Santri.query.get_or_404(id)
    try:
        Setoran.query.filter_by(santri_id=id).delete()
        Absensi.query.filter_by(santri_id=id).delete() # Hapus absensi juga
        if s.foto: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], s.foto))
        db.session.delete(s); db.session.commit(); flash('Dihapus.', 'success')
    except: db.session.rollback()
    return redirect(url_for('halaman_santri'))

@app.route('/santri/status/<int:id>', methods=['POST'])
@login_required
def update_status_santri(id):
    s = Santri.query.get_or_404(id); s.status = request.form.get('status'); db.session.commit()
    flash(f'Status diubah: {s.status}', 'info'); return redirect(url_for('halaman_santri'))

@app.route('/santri/detail/<int:id>')
@login_required
def detail_santri(id):
    s = Santri.query.get_or_404(id)
    tot = db.session.query(func.sum(Setoran.ayat_akhir - Setoran.ayat_awal + 1)).filter_by(santri_id=id).scalar() or 0
    riw = Setoran.query.filter_by(santri_id=id).order_by(Setoran.tanggal.desc()).all()
    return render_template('detail_santri.html', santri=s, total_ayat=tot, riwayat=riw, active_page='santri')

@app.route('/setoran', methods=['GET', 'POST'])
@login_required
def halaman_setoran():
    if request.method == 'POST':
        db.session.add(Setoran(santri_id=int(request.form.get('santriSelect')), ustadz_id=current_user.id, surat=request.form.get('suratSelect'), ayat_awal=int(request.form.get('ayatAwal')), ayat_akhir=int(request.form.get('ayatAkhir')), kualitas=request.form.get('kualitas'), catatan=request.form.get('catatanInput')))
        db.session.commit(); flash('Setoran masuk.', 'success'); return redirect(url_for('halaman_setoran'))
    return render_template('setoran.html', semua_santri=Santri.query.filter_by(status='Aktif').all(), setoran_terkini=Setoran.query.order_by(Setoran.tanggal.desc()).limit(20).all(), active_page='setoran')

@app.route('/setoran/hapus/<int:id>', methods=['POST'])
@login_required
def hapus_setoran(id):
    s = Setoran.query.get_or_404(id)
    if current_user.role == 'admin' or s.ustadz_id == current_user.id:
        db.session.delete(s); db.session.commit(); flash('Setoran dihapus.', 'info')
    else: flash('Tidak berhak.', 'danger')
    return redirect(url_for('halaman_setoran'))

@app.route('/laporan')
@login_required
def halaman_laporan():
    s_id = request.args.get('santri_id'); bln = request.args.get('bulan', datetime.now().month, type=int); thn = request.args.get('tahun', datetime.now().year, type=int)
    dl, st, stp = None, None, None
    if s_id:
        stp = Santri.query.get(s_id)
        if stp:
            dl = Setoran.query.filter(Setoran.santri_id == s_id, extract('month', Setoran.tanggal) == bln, extract('year', Setoran.tanggal) == thn).order_by(Setoran.tanggal.desc()).all()
            tb = sum((s.ayat_akhir - s.ayat_awal + 1) for s in dl)
            tg = db.session.query(func.sum(Setoran.ayat_akhir - Setoran.ayat_awal + 1)).filter(Setoran.santri_id == s_id).scalar() or 0
            cfg = Konfigurasi.query.first(); trg = cfg.target_bulanan if cfg else 150
            st = {'total_ayat': tb, 'total_global': tg, 'total_setoran': len(dl), 'target': trg, 'persentase': min(int((tb/trg)*100), 100), 'sisa': max(trg-tb, 0)}
    return render_template('laporan.html', semua_santri=Santri.query.all(), santri_terpilih=stp, data_laporan=dl, statistik=st, bulan_pilih=bln, tahun_pilih=thn, active_page='laporan')

@app.route('/laporan/download_pdf')
@login_required
def download_pdf():
    # ... (PDF Logic Sama)
    s_id = request.args.get('santri_id'); bln = request.args.get('bulan', datetime.now().month, type=int); thn = request.args.get('tahun', datetime.now().year, type=int)
    if not s_id: return redirect(url_for('halaman_laporan'))
    s = Santri.query.get_or_404(s_id); u = Ustadz.query.get(s.ustadz_id)
    dl = Setoran.query.filter(Setoran.santri_id == s_id, extract('month', Setoran.tanggal) == bln, extract('year', Setoran.tanggal) == thn).order_by(Setoran.tanggal.asc()).all()
    tot = sum((x.ayat_akhir - x.ayat_awal + 1) for x in dl)
    cfg = Konfigurasi.query.first() or Konfigurasi()
    nama_bln = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    html = render_template('pdf_laporan.html', santri=s, ustadz=u, data=dl, bulan_nama=nama_bln[bln], tahun=thn, total_ayat=tot, total_hadir=len(dl), tanggal_cetak=datetime.now().strftime('%d %B %Y'), config=cfg)
    result = BytesIO(); pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err: result.seek(0); return send_file(result, download_name=f"Laporan_{s.nama}.pdf", as_attachment=True)
    return "Gagal", 500

@app.route('/laporan/download_excel')
@login_required
def download_excel():
    # ... (Excel Logic Sama)
    bln = request.args.get('bulan', datetime.now().month, type=int); thn = request.args.get('tahun', datetime.now().year, type=int)
    dr = db.session.query(Setoran, Santri, Ustadz).join(Santri, Setoran.santri_id == Santri.id).join(Ustadz, Setoran.ustadz_id == Ustadz.id).filter(extract('month', Setoran.tanggal) == bln, extract('year', Setoran.tanggal) == thn).order_by(Setoran.tanggal.asc()).all()
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Rekap"
    ws.append(["No", "Tanggal", "Jam", "Nama Santri", "Kelas", "Hafalan", "Ayat", "Total", "Nilai", "Penyimak"])
    for i, row in enumerate(dr, 1):
        s, sa, u = row.Setoran, row.Santri, row.Ustadz
        ws.append([i, s.tanggal.strftime('%d-%m-%Y'), s.tanggal.strftime('%H:%M'), sa.nama, sa.kelas, s.surat, f"{s.ayat_awal}-{s.ayat_akhir}", s.ayat_akhir-s.ayat_awal+1, s.kualitas, u.nama])
    out = BytesIO(); wb.save(out); out.seek(0); return send_file(out, download_name=f"Rekap_{bln}_{thn}.xlsx", as_attachment=True)

@app.route('/prestasi')
@login_required
def halaman_prestasi():
    sq = db.session.query(Setoran.santri_id, func.sum(Setoran.ayat_akhir - Setoran.ayat_awal + 1).label('total')).group_by(Setoran.santri_id).subquery()
    ld = db.session.query(Santri, func.coalesce(sq.c.total, 0).label('skor')).outerjoin(sq, Santri.id == sq.c.santri_id).order_by(func.coalesce(sq.c.total, 0).desc()).all()
    return render_template('prestasi.html', leaderboard=ld, active_page='prestasi')

@app.route('/pengaturan')
@login_required
def halaman_pengaturan(): return render_template('pengaturan.html', active_page='pengaturan')

@app.route('/pengaturan/update_profil', methods=['POST'])
@login_required
def update_profil():
    current_user.nama = request.form.get('nama'); db.session.commit(); return redirect(url_for('halaman_pengaturan'))

@app.route('/pengaturan/update_password', methods=['POST'])
@login_required
def update_password():
    if check_password_hash(current_user.password, request.form.get('password_lama')):
        if request.form.get('password_baru') == request.form.get('konfirmasi_password'):
            current_user.password = generate_password_hash(request.form.get('password_baru'), method='pbkdf2:sha256')
            db.session.commit(); return redirect(url_for('logout'))
    return redirect(url_for('halaman_pengaturan'))

@app.route('/pengaturan/update_sekolah', methods=['POST'])
@login_required
def update_sekolah():
    c = Konfigurasi.query.first() or Konfigurasi(); db.session.add(c)
    c.nama_tpq = request.form.get('nama_tpq'); c.alamat_tpq = request.form.get('alamat_tpq'); 
    if request.form.get('target_bulanan'): c.target_bulanan = int(request.form.get('target_bulanan'))
    db.session.commit(); flash('Info sekolah update.', 'success'); return redirect(url_for('halaman_pengaturan'))

@app.route('/pengaturan/backup')
@login_required
@admin_required
def backup_db():
    data = {'config': [c.to_dict() for c in Konfigurasi.query.all()], 'ustadz': [u.to_dict() for u in Ustadz.query.all()], 'santri': [s.to_dict() for s in Santri.query.all()], 'setoran': [s.to_dict() for s in Setoran.query.all()], 'absensi': [a.to_dict() for a in Absensi.query.all()]}
    return send_file(BytesIO(json.dumps(data, indent=4, default=str).encode('utf-8')), download_name=f"Backup_{datetime.now().strftime('%Y%m%d')}.json", as_attachment=True, mimetype='application/json')

@app.route('/pengaturan/restore', methods=['POST'])
@login_required
@admin_required
def restore_db():
    f = request.files.get('file_backup')
    if f and f.filename.endswith('.json'):
        try:
            d = json.load(f)
            db.session.query(Absensi).delete(); db.session.query(Setoran).delete(); db.session.query(Santri).delete(); db.session.query(Ustadz).delete(); db.session.query(Konfigurasi).delete(); db.session.commit()
            for x in d.get('config', []): db.session.add(Konfigurasi(**x))
            for x in d.get('ustadz', []): db.session.add(Ustadz(**x))
            for x in d.get('santri', []): db.session.add(Santri(**x))
            for x in d.get('setoran', []): db.session.add(Setoran(**x))
            for x in d.get('absensi', []): db.session.add(Absensi(**x))
            db.session.commit(); flash('Restore Sukses.', 'success'); return redirect(url_for('logout'))
        except Exception as e: db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('halaman_pengaturan'))

@app.route('/api/santri/<int:santri_id>')
@login_required
def get_santri_api(santri_id):
    s = Santri.query.get(santri_id); 
    if not s: return jsonify({'error': 'Not found'}), 404
    tot = db.session.query(func.sum(Setoran.ayat_akhir - Setoran.ayat_awal + 1)).filter_by(santri_id=santri_id).scalar() or 0
    tr = Setoran.query.filter_by(santri_id=santri_id).order_by(Setoran.tanggal.desc()).first()
    url = url_for('static', filename='uploads/'+s.foto) if s.foto else None
    return jsonify({'nama': s.nama, 'kelas': s.kelas, 'foto_url': url, 'total_hafalan': tot, 'terakhir_surat': tr.surat if tr else '-'})

# --- ROUTE UNTUK PORTAL WALI SANTRI (PUBLIC) ---

@app.route('/portal-wali', methods=['GET', 'POST'])
def portal_wali():
    # Halaman ini bisa diakses TANPA Login
    santri_data = None
    riwayat_setoran = []
    riwayat_absensi = []
    summary = {'total_setoran': 0, 'hadir': 0, 'sakit': 0, 'izin': 0, 'alpha': 0}
    
    keyword = request.args.get('keyword') # Mengambil parameter pencarian dari URL
    
    if keyword:
        # Cari santri berdasarkan Nama (menggunakan ILIKE/LIKE untuk pencarian mirip)
        # Note: func.lower digunakan agar pencarian tidak sensitif huruf besar/kecil
        santri_data = Santri.query.filter(Santri.nama.ilike(f"%{keyword}%")).first()
        
        if santri_data:
            # Jika santri ditemukan, ambil data detailnya
            
            # 1. Ambil Riwayat Setoran (5 Terakhir)
            riwayat_setoran = Setoran.query.filter_by(santri_id=santri_data.id)\
                .order_by(Setoran.tanggal.desc()).limit(10).all()
            
            # 2. Ambil Riwayat Absensi (Bulan Ini/Terakhir)
            riwayat_absensi = Absensi.query.filter_by(santri_id=santri_data.id)\
                .order_by(Absensi.tanggal.desc()).limit(10).all()
            
            # 3. Hitung Statistik Sederhana
            summary['total_setoran'] = Setoran.query.filter_by(santri_id=santri_data.id).count()
            summary['hadir'] = Absensi.query.filter_by(santri_id=santri_data.id, status='Hadir').count()
            summary['sakit'] = Absensi.query.filter_by(santri_id=santri_data.id, status='Sakit').count()
            summary['izin'] = Absensi.query.filter_by(santri_id=santri_data.id, status='Izin').count()
            summary['alpha'] = Absensi.query.filter_by(santri_id=santri_data.id, status='Alpha').count()
        else:
            flash(f'Data santri dengan nama "{keyword}" tidak ditemukan.', 'warning')

    return render_template('portal_wali.html', 
                        santri=santri_data, 
                        setoran=riwayat_setoran, 
                        absensi=riwayat_absensi,
                        summary=summary,
                        keyword=keyword)

# --- ROUTE CETAK LAPORAN (PDF/PRINT) ---

@app.route('/laporan/cetak/<int:santri_id>')
def cetak_laporan(santri_id):
    # Ambil data santri
    santri = Santri.query.get_or_404(santri_id)
    
    # Ambil data bulan ini (Default)
    # Di aplikasi real, bisa ditambahkan filter bulan
    start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    # Query Setoran Bulan Ini
    setoran_list = Setoran.query.filter(
        Setoran.santri_id == santri_id,
        Setoran.tanggal >= start_date
    ).order_by(Setoran.tanggal.asc()).all()
    
    # Query Absensi Bulan Ini
    absensi_list = Absensi.query.filter(
        Absensi.santri_id == santri_id,
        Absensi.tanggal >= start_date
    ).order_by(Absensi.tanggal.asc()).all()
    
    # Hitung Ringkasan
    summary = {
        'hadir': sum(1 for a in absensi_list if a.status == 'Hadir'),
        'sakit': sum(1 for a in absensi_list if a.status == 'Sakit'),
        'izin':  sum(1 for a in absensi_list if a.status == 'Izin'),
        'alpha': sum(1 for a in absensi_list if a.status == 'Alpha'),
        'total_setoran': len(setoran_list),
        'nilai_rata_rata': 'Mumtaz' # Logika penyederhanaan (bisa dibuat rumus rata-rata)
    }

    return render_template('laporan_cetak.html', 
                        santri=santri, 
                        setoran=setoran_list, 
                        absensi=absensi_list,
                        summary=summary,
                        tanggal_cetak=datetime.now())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Konfigurasi.query.first(): db.session.add(Konfigurasi()); db.session.commit()
        if not Ustadz.query.filter_by(username='admin').first():
            db.session.add(Ustadz(nama='Administrator', username='admin', password=generate_password_hash('admin123', method='pbkdf2:sha256'), role='admin'))
            db.session.commit()
    app.run(debug=True)