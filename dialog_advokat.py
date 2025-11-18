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

# Nama file UI yang harus dimuat
UI_FILE_NAME = 'form_advokat.ui'

class DialogAdvokat(QDialog):
    """
    Dialog untuk menambah, mengubah, menampilkan, dan memfilter data Advokat.
    """
    # Menghapus data_advokat=None dari __init__ yang lama,
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
        self.ui.setWindowTitle("Manajemen Data Advokat")

        # 2. Inisialisasi State dan Tabel
        self.advokat_id_terpilih = None
        self.setup_tabel()
        self.mode_tambah() # Set UI ke mode default (Tambah/Form Kosong)

        # 3. Hubungkan Aksi Sinyal
        self.ui.btnSimpan.clicked.connect(self.aksiSimpan)
        self.ui.btnUbah.clicked.connect(self.aksiUbah)
        self.ui.btnBatal.clicked.connect(self.mode_tambah) # Batal = Reset ke mode tambah/form kosong

        # [FITUR FILTER] Hubungkan QLineEdit 'cariAdvokat'
        self.ui.cariAdvokat.textChanged.connect(self.aksiCari)

        # [FITUR TAMPIL DATA] Hubungkan klik tabel untuk mode Ubah
        self.ui.tabelAdvokat.cellClicked.connect(self.ambil_data_tabel)

        # 4. Tampilkan data awal
        self.muat_data()

    # --- SETUP TABEL DAN TAMPIL DATA ---
    def setup_tabel(self):
        """Mengatur properti dasar QTableWidget."""
        tabel = self.ui.tabelAdvokat
        # Kolom di UI: ID, Nama, Lisensi, Spesialisasi (4 kolom)
        judul_kolom = ["ID", "Nama", "Lisensi", "Spesialisasi"]
        tabel.setColumnCount(len(judul_kolom))
        tabel.setHorizontalHeaderLabels(judul_kolom)

        tabel.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabel.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tabel.hideColumn(0) # Sembunyikan ID (kolom 0)

        header = tabel.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

    def muat_data(self):
        """Mengambil semua data advokat dari database dan mengisi tabel."""
        # Fungsi ambilSemuaAdvokat mengembalikan: id_advokat, nama_advokat, spesialisasi, no_lisensi
        # Urutan output DB: ID, Nama, Spesialisasi, Lisensi (4 kolom)
        data = self.aksiCrudHukum.ambilSemuaAdvokat()
        self.tampilkan_di_tabel(data)

    def tampilkan_di_tabel(self, data):
        """Helper: Mengisi data ke QTableWidget."""
        tabel = self.ui.tabelAdvokat
        tabel.setRowCount(0)

        for baris_idx, row_data in enumerate(data):
            tabel.insertRow(baris_idx)
            # Karena urutan di DB dan UI agak berbeda, kita harus menyesuaikan
            # DB: [ID, Nama, Spesialisasi, Lisensi]
            # UI: [ID, Nama, Lisensi, Spesialisasi]

            # Kolom 0 (ID) - dari DB index 0
            tabel.setItem(baris_idx, 0, QTableWidgetItem(str(row_data[0])))
            # Kolom 1 (Nama) - dari DB index 1
            tabel.setItem(baris_idx, 1, QTableWidgetItem(str(row_data[1])))
            # Kolom 2 (Lisensi) - dari DB index 3 (no_lisensi)
            tabel.setItem(baris_idx, 2, QTableWidgetItem(str(row_data[3])))
            # Kolom 3 (Spesialisasi) - dari DB index 2
            tabel.setItem(baris_idx, 3, QTableWidgetItem(str(row_data[2])))

    # --- FITUR FILTER / PENCARIAN ---
    def aksiCari(self, keyword):
        """Dipanggil saat teks di 'cariAdvokat' berubah."""
        if keyword:
            # Fungsi cariAdvokat mengembalikan: id_advokat, nama_advokat, spesialisasi, no_lisensi
            data_hasil = self.aksiCrudHukum.cariAdvokat(keyword)
            self.tampilkan_di_tabel(data_hasil)
        else:
            self.muat_data() # Jika kosong, tampilkan semua data

    # --- INTERAKSI KLIK TABEL ---
    def ambil_data_tabel(self, row, column):
        """Mengisi form input saat baris tabel diklik untuk mode Ubah."""
        tabel = self.ui.tabelAdvokat

        # Ambil data dari tabel (berdasarkan urutan kolom UI)
        self.advokat_id_terpilih = tabel.item(row, 0).text()
        nama = tabel.item(row, 1).text()
        lisensi = tabel.item(row, 2).text()
        spesialisasi = tabel.item(row, 3).text()

        # Isi ke Form Input (sesuai object name di UI)
        self.ui.editIDAdvokat.setText(self.advokat_id_terpilih)
        self.ui.editNamaAdvokat.setText(nama)
        self.ui.editSpesialisasi.setText(spesialisasi)
        self.ui.editLisensi.setText(lisensi)

        self.mode_ubah() # Pindah ke mode Ubah

    # --- MANAJEMEN MODE UI (UBAH/TAMBAH) ---
    def mode_tambah(self):
        """Mengatur UI ke mode input data baru."""
        self.ui.editIDAdvokat.clear()
        self.ui.editNamaAdvokat.clear()
        self.ui.editSpesialisasi.clear()
        self.ui.editLisensi.clear()

        self.advokat_id_terpilih = None
        self.ui.btnSimpan.setEnabled(True)
        self.ui.btnUbah.setEnabled(False)
        self.ui.tabelAdvokat.clearSelection()

    def mode_ubah(self):
        """Mengatur UI ke mode Ubah Data."""
        self.ui.btnSimpan.setEnabled(False)
        self.ui.btnUbah.setEnabled(True)

    # --- VALIDASI INPUT ---
    def validasi_input(self, nama, spesialisasi):
        """Validasi data sebelum disimpan/diubah."""

        if not nama.strip():
            QMessageBox.warning(self, "Validasi Gagal", "Nama Advokat wajib diisi!")
            return False

        if not spesialisasi.strip():
            QMessageBox.warning(self, "Validasi Gagal", "Spesialisasi wajib diisi!")
            return False

        return True

    # --- AKSI SIMPAN DAN UBAH ---
    def get_input_data(self):
        """Mengambil data dari input fields."""
        nama = self.ui.editNamaAdvokat.text()
        spesialisasi = self.ui.editSpesialisasi.text()
        lisensi = self.ui.editLisensi.text()
        return nama, spesialisasi, lisensi

    def aksiSimpan(self):
        """Menyimpan data advokat baru."""
        nama, spesialisasi, lisensi = self.get_input_data()

        if not self.validasi_input(nama, spesialisasi):
            return

        try:
            self.aksiCrudHukum.simpanAdvokat(nama, spesialisasi, lisensi)
            QMessageBox.information(self, "Sukses", "Data Advokat berhasil disimpan.")
            self.mode_tambah() # Reset form
            self.muat_data()   # Refresh tabel
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def aksiUbah(self):
        """Mengubah data advokat yang terpilih."""
        if not self.advokat_id_terpilih:
             QMessageBox.warning(self, "Peringatan", "Pilih data advokat dari tabel untuk diubah.")
             return

        nama, spesialisasi, lisensi = self.get_input_data()

        if not self.validasi_input(nama, spesialisasi):
            return

        try:
            self.aksiCrudHukum.ubahAdvokat(self.advokat_id_terpilih, nama, spesialisasi, lisensi)
            QMessageBox.information(self, "Sukses", "Data Advokat berhasil diubah.")
            self.mode_tambah() # Reset form ke mode tambah
            self.muat_data()   # Refresh tabel
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengubah: {e}")
