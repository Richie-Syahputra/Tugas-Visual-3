import sys
from PySide6.QtWidgets import (
    QWidget,
    QMessageBox,
    QDialog,
    QTableWidgetItem,
    QHeaderView, # Digunakan untuk mengatur lebar kolom tabel
    QAbstractItemView # Digunakan untuk mengatur perilaku seleksi tabel
)
from PySide6.QtCore import QFile, Qt
from PySide6.QtUiTools import QUiLoader

# Import modul CRUD
from crud_hukum import crud_hukum

# Nama file UI yang harus Anda buat/simpan di Qt Designer
UI_FILE_NAME = 'form_klien.ui'

class DialogKlien(QDialog):
    """
    Dialog untuk menambah, mengubah, menampilkan, dan memfilter data Klien.
    """
    # Menghapus data_klien=None dari __init__ agar lebih sederhana,
    # karena mode Ubah/Tambah ditentukan oleh interaksi klik tabel.
    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. Load UI menggunakan QUiLoader
        filenya = QFile(UI_FILE_NAME)
        if not filenya.exists():
            QMessageBox.critical(self, "Error UI", f"File UI '{UI_FILE_NAME}' tidak ditemukan!")
            return

        filenya.open(QFile.ReadOnly)
        muatFile = QUiLoader()
        self.ui = muatFile.load(filenya, self)
        self.aksiCrudHukum = crud_hukum()
        self.setLayout(self.ui.layout())
        self.ui.setWindowTitle("Manajemen Data Klien")

        # 2. Inisialisasi State dan Tabel
        self.klien_id_terpilih = None # ID klien yang sedang dalam mode ubah
        self.setup_tabel()
        self.mode_tambah() # Set UI ke mode default (Tambah)

        # 3. Hubungkan Aksi Sinyal
        self.ui.btnSimpan.clicked.connect(self.aksiSimpan)
        self.ui.btnUbah.clicked.connect(self.aksiUbah)
        self.ui.btnBatal.clicked.connect(self.mode_tambah) # Batal = Reset ke mode tambah/form kosong

        # [FITUR FILTER] Hubungkan QLineEdit 'cariKlien' ke fungsi cari
        self.ui.cariKlien.textChanged.connect(self.aksiCari)

        # [FITUR TAMPIL DATA] Hubungkan klik tabel untuk mode Ubah
        self.ui.tabelKlien.cellClicked.connect(self.ambil_data_tabel)

        # 4. Tampilkan data awal
        self.muat_data()

    # --- SETUP TABEL DAN TAMPIL DATA ---
    def setup_tabel(self):
        """Mengatur properti dasar QTableWidget."""
        tabel = self.ui.tabelKlien
        # Sesuaikan dengan definisi kolom di UI Anda
        judul_kolom = ["ID", "Nama", "Alamat", "Telp", "Email"]
        tabel.setColumnCount(len(judul_kolom))
        tabel.setHorizontalHeaderLabels(judul_kolom)

        tabel.setSelectionBehavior(QAbstractItemView.SelectRows) # Pilih satu baris penuh
        tabel.setEditTriggers(QAbstractItemView.NoEditTriggers) # Tidak bisa edit langsung di tabel
        tabel.hideColumn(0) # Sembunyikan ID (kolom 0)

        # Atur lebar kolom agar memenuhi tabel
        header = tabel.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    def muat_data(self):
        """Mengambil semua data klien dari database dan mengisi tabel."""
        data = self.aksiCrudHukum.ambilSemuaKlien() # Asumsi fungsi ini sudah ada di crud_hukum.py
        self.tampilkan_di_tabel(data)

    def tampilkan_di_tabel(self, data):
        """Helper: Mengisi data ke QTableWidget."""
        tabel = self.ui.tabelKlien
        tabel.setRowCount(0)

        for baris_idx, row_data in enumerate(data):
            tabel.insertRow(baris_idx)
            for kolom_idx, item_data in enumerate(row_data):
                item = QTableWidgetItem(str(item_data))
                tabel.setItem(baris_idx, kolom_idx, item)

    # --- FITUR FILTER / PENCARIAN ---
    def aksiCari(self, keyword):
        """Dipanggil saat teks di 'cariKlien' berubah."""
        if keyword:
            # Asumsi fungsi cariKlien sudah ditambahkan di crud_hukum.py
            data_hasil = self.aksiCrudHukum.cariKlien(keyword)
            self.tampilkan_di_tabel(data_hasil)
        else:
            self.muat_data() # Jika kosong, tampilkan semua data

    # --- INTERAKSI KLIK TABEL ---
    def ambil_data_tabel(self, row, column):
        """Mengisi form input saat baris tabel diklik untuk mode Ubah."""
        tabel = self.ui.tabelKlien

        # ID ada di kolom 0, selalu ambil dari sana
        self.klien_id_terpilih = tabel.item(row, 0).text()
        nama = tabel.item(row, 1).text()
        alamat = tabel.item(row, 2).text()
        telepon = tabel.item(row, 3).text()
        email = tabel.item(row, 4).text()

        # Isi ke Form Input
        # Perhatikan: editID di UI sudah dibuat visible, kita gunakan untuk menampilkan ID terpilih
        self.ui.editID.setText(self.klien_id_terpilih)
        self.ui.editNama.setText(nama)
        self.ui.editAlamat.setText(alamat)
        self.ui.editTelp.setText(telepon)
        self.ui.editEmail.setText(email)

        self.mode_ubah() # Pindah ke mode Ubah

    # --- MANAJEMEN MODE UI (UBAH/TAMBAH) ---
    def mode_tambah(self):
        """Mengatur UI ke mode input data baru."""
        self.ui.editID.clear()
        self.ui.editNama.clear()
        self.ui.editAlamat.clear()
        self.ui.editTelp.clear()
        self.ui.editEmail.clear()

        self.klien_id_terpilih = None # Reset ID yang terpilih
        self.ui.btnSimpan.setEnabled(True)
        self.ui.btnUbah.setEnabled(False)
        self.ui.tabelKlien.clearSelection()

    def mode_ubah(self):
        """Mengatur UI ke mode Ubah Data."""
        self.ui.btnSimpan.setEnabled(False) # Jangan biarkan simpan data baru saat mode ubah
        self.ui.btnUbah.setEnabled(True)

    # --- VALIDASI INPUT ---
    def validasi_input(self, nama, alamat, telepon):
        """Validasi data sebelum disimpan/diubah."""

        # 1. Cek Kolom Wajib
        if not nama.strip():
            QMessageBox.warning(self, "Validasi Gagal", "Nama Klien wajib diisi!")
            return False

        if not alamat.strip():
            QMessageBox.warning(self, "Validasi Gagal", "Alamat wajib diisi!")
            return False

        # 2. Cek Telepon (Harus Angka jika diisi)
        if telepon and not telepon.isdigit():
             QMessageBox.warning(self, "Validasi Gagal", "Nomor Telepon harus berupa angka!")
             return False

        return True

    # --- AKSI SIMPAN DAN UBAH ---
    def get_input_data(self):
        """Mengambil data dari input fields."""
        # Menggunakan .text() karena semua field di UI Anda adalah QLineEdit
        nama = self.ui.editNama.text()
        alamat = self.ui.editAlamat.text()
        telepon = self.ui.editTelp.text()
        email = self.ui.editEmail.text()
        return nama, alamat, telepon, email

    def aksiSimpan(self):
        """Menyimpan data klien baru."""
        nama, alamat, telepon, email = self.get_input_data()

        if not self.validasi_input(nama, alamat, telepon):
            return

        try:
            self.aksiCrudHukum.simpanKlien(nama, alamat, telepon, email)
            QMessageBox.information(self, "Sukses", "Data Klien berhasil disimpan.")
            self.mode_tambah() # Reset form
            self.muat_data()   # Refresh tabel
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def aksiUbah(self):
        """Mengubah data klien yang terpilih."""
        if not self.klien_id_terpilih:
             QMessageBox.warning(self, "Peringatan", "Pilih data klien dari tabel untuk diubah.")
             return

        nama, alamat, telepon, email = self.get_input_data()

        if not self.validasi_input(nama, alamat, telepon):
            return

        try:
            self.aksiCrudHukum.ubahKlien(self.klien_id_terpilih, nama, alamat, telepon, email)
            QMessageBox.information(self, "Sukses", "Data Klien berhasil diubah.")
            self.mode_tambah() # Reset form ke mode tambah
            self.muat_data()   # Refresh tabel
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengubah: {e}")
