import sys
from PySide6.QtWidgets import QMessageBox, QDialog
from PySide6.QtCore import QFile, QDateTime, Qt
from PySide6.QtUiTools import QUiLoader

from crud_hukum import crud_hukum

UI_FILE_NAME = 'form_jadwal.ui'

class DialogJadwal(QDialog):
    def __init__(self, parent=None, id_perkara=None, data_jadwal=None):
        super().__init__(parent)

        filenya = QFile(UI_FILE_NAME)
        if not filenya.exists():
            QMessageBox.critical(self, "Error UI", f"File UI '{UI_FILE_NAME}' tidak ditemukan!")
            return

        filenya.open(QFile.ReadOnly)
        muatFile = QUiLoader()
        self.ui = muatFile.load(filenya, self)
        self.aksiCrudHukum = crud_hukum()

        if hasattr(self.ui, 'centralWidget') and self.ui.centralWidget():
            self.setLayout(self.ui.centralWidget().layout())

        self.mode = "TAMBAH"
        self.jadwal_id = None
        self.fk_id_perkara = id_perkara

        # Asumsi ada btnUbahJadwal di UI untuk mode ubah
        btnUbah = getattr(self.ui, 'btnUbahJadwal', None)
        if btnUbah:
            btnUbah.setText("Update Jadwal")
            btnUbah.clicked.connect(self.aksiSimpan)

        if data_jadwal:
            self.mode = "UBAH"
            self.jadwal_id = data_jadwal['id']
            self.fk_id_perkara = data_jadwal['id_perkara']
            self.ui.setWindowTitle(f"Ubah Jadwal Sidang (ID Pkr: {self.fk_id_perkara})")
            self.isi_form(data_jadwal)
            self.ui.btnSimpanJadwal.hide()
            if btnUbah: btnUbah.show()
        elif id_perkara:
            self.ui.setWindowTitle(f"Tambah Jadwal Sidang Baru (ID Pkr: {self.fk_id_perkara})")
            if btnUbah: btnUbah.hide()
            self.ui.editTanggalSidang.setDateTime(QDateTime.currentDateTime())
        else:
            QMessageBox.critical(self, "Error", "ID Perkara tidak ditemukan.")
            self.close()
            return

        self.ui.btnSimpanJadwal.clicked.connect(self.aksiSimpan)
        self.ui.btnBatal.clicked.connect(self.close)


    def isi_form(self, data):
        """Mengisi form dengan data jadwal yang akan diubah."""
        # PERBAIKAN: Menggunakan key 'tanggal_sidang' dan 'lokasi_sidang'
        dt = QDateTime.fromString(str(data['tanggal_sidang']), "yyyy-MM-dd HH:mm:ss")
        if dt.isValid():
             self.ui.editTanggalSidang.setDateTime(dt)

        self.ui.editAgenda.setText(data['agenda'])
        self.ui.editLokasi.setText(data['lokasi_sidang']) # PERBAIKAN: Menggunakan key lokasi_sidang


    def aksiSimpan(self):
        tgl_sidang_dt = self.ui.editTanggalSidang.dateTime()
        tgl_sidang_str = tgl_sidang_dt.toString("yyyy-MM-dd HH:mm:ss") # String format untuk MySQL

        agenda = self.ui.editAgenda.toPlainText()
        lokasi = self.ui.editLokasi.text()

        if not agenda or not lokasi:
            QMessageBox.warning(self, "Peringatan", "Agenda dan Lokasi wajib diisi.")
            return

        try:
            if self.mode == "TAMBAH":
                self.aksiCrudHukum.simpanJadwal(self.fk_id_perkara, tgl_sidang_str, agenda, lokasi)
                pesan = "Jadwal sidang baru berhasil disimpan."
            else:
                self.aksiCrudHukum.ubahJadwal(self.jadwal_id, tgl_sidang_str, agenda, lokasi)
                pesan = "Jadwal sidang berhasil diubah."

            QMessageBox.information(self, "Sukses", pesan)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Terjadi kesalahan database: {e}")
