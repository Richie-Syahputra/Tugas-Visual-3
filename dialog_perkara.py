import sys
from PySide6.QtWidgets import QWidget, QMessageBox, QDialog
from PySide6.QtCore import QFile, QDate, Qt # Import Qt
from PySide6.QtUiTools import QUiLoader

from crud_hukum import crud_hukum

UI_FILE_NAME = 'form_perkara.ui'

class DialogPerkara(QDialog):
    def __init__(self, parent=None, data_perkara=None):
        super().__init__(parent)

        filenya = QFile(UI_FILE_NAME)
        if not filenya.exists():
            QMessageBox.critical(self, "Error UI", f"File UI '{UI_FILE_NAME}' tidak ditemukan!")
            return

        filenya.open(QFile.ReadOnly)
        muatFile = QUiLoader()
        self.ui = muatFile.load(filenya, self)
        self.aksiCrudHukum = crud_hukum()
        # Asumsi Anda menggunakan layout yang benar di UI
        # self.setLayout(self.ui.layout())

        self.data_klien = {}
        self.data_advokat = {}

        self.isi_master_data()
        self.isi_status_perkara()

        self.mode = "TAMBAH"
        self.perkara_id = None

        if data_perkara:
            self.mode = "UBAH"
            self.perkara_id = data_perkara['id']
            self.ui.setWindowTitle("Ubah Data Perkara")
            self.isi_form(data_perkara)
            self.ui.btnSimpanPerkara.hide()
            self.ui.btnUbahPerkara.setText("Update Data")
            self.ui.editNomorPerkara.setEnabled(False)
        else:
            self.ui.setWindowTitle("Tambah Data Perkara Baru")
            self.ui.btnUbahPerkara.hide()

        self.ui.btnSimpanPerkara.clicked.connect(self.aksiSimpan)
        self.ui.btnUbahPerkara.clicked.connect(self.aksiSimpan)
        self.ui.btnBatal.clicked.connect(self.close)


    def isi_status_perkara(self):
        status_list = ["Berjalan", "Selesai", "Banding", "Kasasi", "Non-Aktif"]
        self.ui.comboStatusPerkara.addItems(status_list)


    def isi_master_data(self):
        klien_data = self.aksiCrudHukum.ambilSemuaKlien()
        self.ui.comboPilihKlien.clear()

        for id_klien, nama_klien, *rest in klien_data:
            self.data_klien[nama_klien] = str(id_klien)
            self.ui.comboPilihKlien.addItem(nama_klien)

        advokat_data = self.aksiCrudHukum.ambilSemuaAdvokat()
        self.ui.comboPilihAdvokat.clear()

        for id_advokat, nama_advokat, *rest in advokat_data:
            self.data_advokat[nama_advokat] = str(id_advokat)
            self.ui.comboPilihAdvokat.addItem(nama_advokat)

        if not self.data_klien or not self.data_advokat:
             # Tidak ada QMessageBox di sini karena ini akan dipanggil saat inisialisasi
             pass


    def aksiSimpan(self):
        nomor = self.ui.editNomorPerkara.text()
        jenis = self.ui.editJenisPerkara.text()

        # PERBAIKAN: Menggunakan format ISO Date
        tgl_daftar = self.ui.editTanggalDaftar.date().toString(Qt.DateFormat.ISODate)
        status = self.ui.comboStatusPerkara.currentText()

        nama_klien_terpilih = self.ui.comboPilihKlien.currentText()
        id_klien = self.data_klien.get(nama_klien_terpilih)

        nama_advokat_terpilih = self.ui.comboPilihAdvokat.currentText()
        id_advokat = self.data_advokat.get(nama_advokat_terpilih)

        if not nomor or not jenis or not id_klien or not id_advokat:
            QMessageBox.warning(self, "Peringatan", "Semua field wajib diisi.")
            return

        try:
            if self.mode == "TAMBAH":
                self.aksiCrudHukum.simpanPerkara(id_klien, id_advokat, nomor, jenis, tgl_daftar, status)
                pesan = "Data Perkara baru berhasil disimpan."
            else:
                self.aksiCrudHukum.ubahPerkara(self.perkara_id, id_klien, id_advokat, nomor, jenis, tgl_daftar, status)
                pesan = "Data Perkara berhasil diubah."

            QMessageBox.information(self, "Sukses", pesan)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan database: {e}")

    # --- Fungsi untuk Mode Ubah ---
    def isi_form(self, data):
        """Mengisi form dengan data perkara yang akan diubah."""
        # PERBAIKAN: Menggunakan key 'nomor_perkara' dan 'tanggal_daftar'
        self.ui.editNomorPerkara.setText(data['nomor_perkara'])
        self.ui.editJenisPerkara.setText(data['jenis_perkara'])

        tgl = QDate.fromString(data['tanggal_daftar'], Qt.DateFormat.ISODate)
        self.ui.editTanggalDaftar.setDate(tgl)

        index_status = self.ui.comboStatusPerkara.findText(data['status_perkara'])
        if index_status >= 0:
            self.ui.comboStatusPerkara.setCurrentIndex(index_status)

        index_klien = self.ui.comboPilihKlien.findText(data['nama_klien'])
        if index_klien >= 0:
            self.ui.comboPilihKlien.setCurrentIndex(index_klien)

        index_advokat = self.ui.comboPilihAdvokat.findText(data['nama_advokat'])
        if index_advokat >= 0:
            self.ui.comboPilihAdvokat.setCurrentIndex(index_advokat)
