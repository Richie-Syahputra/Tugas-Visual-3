import sys
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QTableWidgetItem,
    QMessageBox,
    QDialog,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QFile
# --- INI YANG HARUS DIPASTIKAN BENAR ---
from PySide6.QtUiTools import QUiLoader

# Import modul CRUD
from crud_hukum import crud_hukum

# Import semua form/dialog (Asumsikan ini ada)
from dialog_klien import DialogKlien
from dialog_advokat import DialogAdvokat
from dialog_perkara import DialogPerkara
from dialog_jadwal import DialogJadwal

MAIN_UI_FILE = 'mainwindow.ui'

class MainWindow(QMainWindow):
    """
    Kelas Utama Aplikasi (Dasbor).
    """
    def __init__(self):
        super().__init__()

        # 1. Load UI Utama menggunakan QUiLoader
        filenya = QFile(MAIN_UI_FILE)
        if not filenya.exists():
            QMessageBox.critical(self, "Error UI", f"File UI '{MAIN_UI_FILE}' tidak ditemukan!")
            sys.exit(1)

        filenya.open(QFile.ReadOnly)
        # Gunakan QUiLoader
        loader = QUiLoader()

        # self.ui adalah objek QMainWindow yang dimuat dari file.
        self.ui = loader.load(filenya)
        filenya.close()

        # 2. Pindahkan elemen kunci dari self.ui ke self
        if hasattr(self.ui, 'centralwidget'):
            self.setCentralWidget(self.ui.centralwidget)
        if hasattr(self.ui, 'menubar'):
            self.setMenuBar(self.ui.menubar)

        self.setWindowTitle("Sistem Informasi Manajemen LBH")

        # 3. Inisialisasi CRUD (Tidak berubah)
        try:
            self.db = crud_hukum()
        except Exception as e:
            QMessageBox.critical(self, "Koneksi Database Gagal", str(e))
            sys.exit(1)

        # 4. Setup dan Muat Tabel Perkara
        self.setup_perkara_table()

        # 5. Hubungkan Aksi QMenuBar (Menggunakan self.ui)
        if hasattr(self.ui, 'actionKeluar'):
            self.ui.actionKeluar.triggered.connect(self.close)

        if hasattr(self.ui, 'actionBukaKlien'):
            self.ui.actionBukaKlien.triggered.connect(self.buka_manajemen_klien)

        if hasattr(self.ui, 'actionBukaAdvokat'):
            self.ui.actionBukaAdvokat.triggered.connect(self.buka_manajemen_advokat)

        if hasattr(self.ui, 'actionBukaPerkara'):
            self.ui.actionBukaPerkara.triggered.connect(self.buka_tambah_perkara)

        # 6. Hubungkan Tombol-Tombol di Bawah Tabel (Menggunakan self.ui)
        self.ui.btnRefresh.clicked.connect(self.refresh_perkara_table)
        self.ui.btnUbahPerkara.clicked.connect(self.aksiUbahPerkara)
        self.ui.btnHapusPerkara.clicked.connect(self.aksiHapusPerkara)
        self.ui.btnBukaJadwal.clicked.connect(self.buka_manajemen_jadwal)


    def setup_perkara_table(self):
        table = self.ui.tableViewUtama
        header_labels = ["ID Perkara", "No. Perkara", "Nama Klien", "Nama Advokat", "Jenis Perkara", "Tgl Daftar", "Status", "ID Klien", "ID Advokat"]
        table.setColumnCount(len(header_labels))
        table.setHorizontalHeaderLabels(header_labels)
        table.hideColumn(0)
        table.hideColumn(7)
        table.hideColumn(8)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.refresh_perkara_table()


    def refresh_perkara_table(self):
        if not hasattr(self.db, 'conn') or not self.db.conn.is_connected(): return
        data_perkara = self.db.ambilSemuaPerkaraJoin()
        table = self.ui.tableViewUtama
        table.setRowCount(0)
        if data_perkara:
            table.setRowCount(len(data_perkara))
            for row_num, row_data in enumerate(data_perkara):
                for col_num, data in enumerate(row_data):
                    item = QTableWidgetItem(str(data))
                    table.setItem(row_num, col_num, item)
            table.resizeColumnsToContents()
            table.horizontalHeader().setStretchLastSection(True)

    # ... (Semua fungsi lain tetap sama, menggunakan self.ui)

    # [FUNGSI LAINNYA DIHAPUS UNTUK MENYINGKAT, TETAPI HARUS ADA DI FILE ANDA]
    # (Pastikan semua fungsi seperti buka_manajemen_klien, aksiUbahPerkara, dll. ada dan menggunakan self.ui)


    # --- FUNGSI DIALOG/AKSI (Disertakan di sini hanya untuk memastikan tidak ada yang hilang) ---
    def buka_manajemen_klien(self):
        try:
            dialog = DialogKlien(self)
            if dialog.exec() == QDialog.Accepted: self.refresh_perkara_table()
        except Exception as e: QMessageBox.critical(self, "Error Buka Klien", f"Gagal memuat form klien.\nError: {e}")

    def buka_manajemen_advokat(self):
        try:
            dialog = DialogAdvokat(self)
            if dialog.exec() == QDialog.Accepted: self.refresh_perkara_table()
        except Exception as e: QMessageBox.critical(self, "Error Buka Advokat", f"Gagal memuat form advokat.\nError: {e}")

    def buka_tambah_perkara(self, data_perkara=None):
        try:
            dialog = DialogPerkara(self, data_perkara=data_perkara)
            if dialog.exec() == QDialog.Accepted: self.refresh_perkara_table()
        except Exception as e: QMessageBox.critical(self, "Error Buka Perkara", f"Gagal memuat form perkara.\nError: {e}")

    def get_selected_perkara_data(self):
        table = self.ui.tableViewUtama
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih satu data perkara dari tabel terlebih dahulu.")
            return None, None
        row_index = selected_rows[0].row()
        data = {'id': table.item(row_index, 0).text(), 'nomor_perkara': table.item(row_index, 1).text(), 'nama_klien': table.item(row_index, 2).text(), 'nama_advokat': table.item(row_index, 3).text(), 'jenis_perkara': table.item(row_index, 4).text(), 'tanggal_daftar': table.item(row_index, 5).text(), 'status_perkara': table.item(row_index, 6).text(), 'id_klien': table.item(row_index, 7).text(), 'id_advokat': table.item(row_index, 8).text()}
        return data, row_index

    def aksiUbahPerkara(self):
        data_perkara, row = self.get_selected_perkara_data()
        if data_perkara: self.buka_tambah_perkara(data_perkara=data_perkara)

    def aksiHapusPerkara(self):
        if not hasattr(self.db, 'conn') or not self.db.conn.is_connected():
            QMessageBox.critical(self, "Error", "Koneksi database terputus.")
            return
        data_perkara, row = self.get_selected_perkara_data()
        if data_perkara:
            id_perkara = data_perkara['id']; no_perkara = data_perkara['nomor_perkara']
            konfirmasi = QMessageBox.question(self, "Konfirmasi Hapus", f"Yakin ingin menghapus perkara:\n{no_perkara}? Menghapus perkara akan menghapus semua jadwal terkait!", QMessageBox.Yes | QMessageBox.No)
            if konfirmasi == QMessageBox.Yes:
                try:
                    self.db.hapusPerkara(id_perkara)
                    QMessageBox.information(self, "Sukses", f"Perkara {no_perkara} berhasil dihapus."); self.refresh_perkara_table()
                except Exception as e: QMessageBox.critical(self, "Error", f"Gagal menghapus data: {e}")

    def buka_manajemen_jadwal(self):
        data_perkara, row = self.get_selected_perkara_data()
        if data_perkara:
            id_perkara = data_perkara['id']
            try:
                dialog = DialogJadwal(self, id_perkara=id_perkara)
                dialog.exec()
            except Exception as e: QMessageBox.critical(self, "Error Buka Jadwal", f"Gagal memuat form jadwal.\nError: {e}")
    # --- END FUNGSI LAINNYA ---


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
