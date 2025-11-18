import mysql.connector
from mysql.connector import Error

class crud_hukum:
    """
    Kelas yang menangani semua operasi CRUD dan Filter untuk database LBH.
    """
    def __init__(self):
        self.conn = None
        try:
            # Pastikan detail koneksi ini sesuai dengan konfigurasi database Anda
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='root', # <--- PASTIKAN PASSWORD BENAR
                database='dbvisual3_2310010493' # <--- PERBAIKAN NAMA DATABASE
            )
            if self.conn.is_connected():
                print("Koneksi dbvisual3_2310010493 berhasil!")
            else:
                raise Exception("Koneksi GAGAL!")
        except Error as e:
            # Pesan error yang informatif
            raise Exception(f"Error Koneksi MySQL: Pastikan MySQL/XAMPP berjalan. Error: {e}")

    def __del__(self):
        """Pastikan koneksi database ditutup saat objek dihancurkan."""
        if self.conn and self.conn.is_connected():
            self.conn.close()

    # =========================================================
    #                    OPERASI KLIEN (tbl_klien)
    # =========================================================

    def simpanKlien(self, nama, alamat, telepon, email):
        aksiCur = self.conn.cursor()
        sql = "INSERT INTO tbl_klien(nama_klien, alamat, telepon, email) VALUES (%s, %s, %s, %s)"
        data = (nama, alamat, telepon, email)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def ambilSemuaKlien(self):
        aksiCur = self.conn.cursor()
        aksiCur.execute("SELECT id_klien, nama_klien, alamat, telepon, email FROM tbl_klien")
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil

    def ubahKlien(self, id_klien, nama, alamat, telepon, email):
        aksiCur = self.conn.cursor()
        sql = "UPDATE tbl_klien SET nama_klien=%s, alamat=%s, telepon=%s, email=%s WHERE id_klien=%s"
        data = (nama, alamat, telepon, email, id_klien)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def hapusKlien(self, id_klien):
        aksiCur = self.conn.cursor()
        aksiCur.execute("DELETE FROM tbl_klien WHERE id_klien=%s", (id_klien,))
        self.conn.commit()
        aksiCur.close()

    def cariKlien(self, keyword):
        """Mencari klien berdasarkan nama atau alamat."""
        aksiCur = self.conn.cursor()
        keyword_like = f"%{keyword}%"
        query = "SELECT id_klien, nama_klien, alamat, telepon, email FROM tbl_klien WHERE nama_klien LIKE %s OR alamat LIKE %s"
        args = (keyword_like, keyword_like)
        aksiCur.execute(query, args)
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil


    # =========================================================
    #                    OPERASI ADVOKAT (tbl_advokat)
    # =========================================================

    def simpanAdvokat(self, nama, spesialisasi, lisensi):
        aksiCur = self.conn.cursor()
        sql = "INSERT INTO tbl_advokat(nama_advokat, spesialisasi, no_lisensi) VALUES (%s, %s, %s)"
        data = (nama, spesialisasi, lisensi)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def ambilSemuaAdvokat(self):
        aksiCur = self.conn.cursor()
        # Urutan: ID, Nama, Spesialisasi, No_Lisensi
        aksiCur.execute("SELECT id_advokat, nama_advokat, spesialisasi, no_lisensi FROM tbl_advokat")
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil

    def ubahAdvokat(self, id_advokat, nama, spesialisasi, lisensi):
        aksiCur = self.conn.cursor()
        sql = "UPDATE tbl_advokat SET nama_advokat=%s, spesialisasi=%s, no_lisensi=%s WHERE id_advokat=%s"
        data = (nama, spesialisasi, lisensi, id_advokat)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def hapusAdvokat(self, id_advokat):
        aksiCur = self.conn.cursor()
        aksiCur.execute("DELETE FROM tbl_advokat WHERE id_advokat=%s", (id_advokat,))
        self.conn.commit()
        aksiCur.close()

    def cariAdvokat(self, keyword):
        """Mencari advokat berdasarkan nama atau spesialisasi."""
        aksiCur = self.conn.cursor()
        keyword_like = f"%{keyword}%"
        # Urutan: ID, Nama, Spesialisasi, No_Lisensi
        query = "SELECT id_advokat, nama_advokat, spesialisasi, no_lisensi FROM tbl_advokat WHERE nama_advokat LIKE %s OR spesialisasi LIKE %s"
        args = (keyword_like, keyword_like)
        aksiCur.execute(query, args)
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil


    # =========================================================
    #                    OPERASI PERKARA (tbl_perkara)
    # =========================================================

    def simpanPerkara(self, id_klien, id_advokat, nomor, jenis, tgl_daftar, status):
        aksiCur = self.conn.cursor()
        sql = ("INSERT INTO tbl_perkara(fk_id_klien, fk_id_advokat, nomor_perkara, jenis_perkara, tanggal_daftar, status_perkara) "
               "VALUES (%s, %s, %s, %s, %s, %s)")
        data = (id_klien, id_advokat, nomor, jenis, tgl_daftar, status)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def ambilSemuaPerkaraJoin(self):
        aksiCur = self.conn.cursor()
        # Mengambil data join (Perkara + Klien + Advokat) untuk ditampilkan di tabel perkara
        sql = ("SELECT p.id_perkara, p.nomor_perkara, k.nama_klien, a.nama_advokat, p.jenis_perkara, p.tanggal_daftar, p.status_perkara, k.id_klien, a.id_advokat "
               "FROM tbl_perkara p "
               "JOIN tbl_klien k ON p.fk_id_klien = k.id_klien "
               "JOIN tbl_advokat a ON p.fk_id_advokat = a.id_advokat "
               "ORDER BY p.tanggal_daftar DESC")
        aksiCur.execute(sql)
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil

    def ambilIDKlienAdvokat(self):
        """Mengambil data Klien dan Advokat untuk Combobox di form Perkara."""
        aksiCur = self.conn.cursor()

        # Ambil semua Klien (ID dan Nama)
        aksiCur.execute("SELECT id_klien, nama_klien FROM tbl_klien ORDER BY nama_klien ASC")
        klien = aksiCur.fetchall()

        # Ambil semua Advokat (ID dan Nama)
        aksiCur.execute("SELECT id_advokat, nama_advokat FROM tbl_advokat ORDER BY nama_advokat ASC")
        advokat = aksiCur.fetchall()

        aksiCur.close()
        return klien, advokat


    def ubahPerkara(self, id_perkara, id_klien, id_advokat, nomor, jenis, tgl_daftar, status):
        aksiCur = self.conn.cursor()
        sql = ("UPDATE tbl_perkara SET fk_id_klien=%s, fk_id_advokat=%s, nomor_perkara=%s, jenis_perkara=%s, tanggal_daftar=%s, status_perkara=%s "
               "WHERE id_perkara=%s")
        data = (id_klien, id_advokat, nomor, jenis, tgl_daftar, status, id_perkara)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def hapusPerkara(self, id_perkara):
        aksiCur = self.conn.cursor()
        aksiCur.execute("DELETE FROM tbl_perkara WHERE id_perkara=%s", (id_perkara,))
        self.conn.commit()
        aksiCur.close()

    def cariPerkaraJoin(self, keyword):
        """Mencari perkara berdasarkan nomor perkara, nama klien, atau nama advokat."""
        aksiCur = self.conn.cursor()
        keyword_like = f"%{keyword}%"
        sql = ("SELECT p.id_perkara, p.nomor_perkara, k.nama_klien, a.nama_advokat, p.jenis_perkara, p.tanggal_daftar, p.status_perkara, k.id_klien, a.id_advokat "
               "FROM tbl_perkara p "
               "JOIN tbl_klien k ON p.fk_id_klien = k.id_klien "
               "JOIN tbl_advokat a ON p.fk_id_advokat = a.id_advokat "
               "WHERE p.nomor_perkara LIKE %s OR k.nama_klien LIKE %s OR a.nama_advokat LIKE %s "
               "ORDER BY p.tanggal_daftar DESC")
        args = (keyword_like, keyword_like, keyword_like)
        aksiCur.execute(sql, args)
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil


    # =========================================================
    #                    OPERASI JADWAL (tbl_jadwal)
    # =========================================================

    def simpanJadwal(self, id_perkara, tgl_sidang, agenda, lokasi):
        aksiCur = self.conn.cursor()
        sql = "INSERT INTO tbl_jadwal(fk_id_perkara, tanggal_sidang, agenda, lokasi_sidang) VALUES (%s, %s, %s, %s)"
        data = (id_perkara, tgl_sidang, agenda, lokasi)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def ambilJadwalPerkara(self, id_perkara):
        aksiCur = self.conn.cursor()
        # Urutan: ID_Jadwal, Tanggal_Sidang, Agenda, Lokasi_Sidang
        aksiCur.execute("SELECT id_jadwal, tanggal_sidang, agenda, lokasi_sidang FROM tbl_jadwal WHERE fk_id_perkara=%s ORDER BY tanggal_sidang DESC", (id_perkara,))
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil

    def ubahJadwal(self, id_jadwal, tgl_sidang, agenda, lokasi):
        aksiCur = self.conn.cursor()
        sql = "UPDATE tbl_jadwal SET tanggal_sidang=%s, agenda=%s, lokasi_sidang=%s WHERE id_jadwal=%s"
        data = (tgl_sidang, agenda, lokasi, id_jadwal)
        aksiCur.execute(sql, data)
        self.conn.commit()
        aksiCur.close()

    def hapusJadwal(self, id_jadwal):
        aksiCur = self.conn.cursor()
        aksiCur.execute("DELETE FROM tbl_jadwal WHERE id_jadwal=%s", (id_jadwal,))
        self.conn.commit()
        aksiCur.close()

    def cariJadwal(self, id_perkara, keyword):
        """Mencari jadwal berdasarkan agenda atau lokasi sidang untuk perkara tertentu."""
        aksiCur = self.conn.cursor()
        keyword_like = f"%{keyword}%"
        # Urutan: ID_Jadwal, Tanggal_Sidang, Agenda, Lokasi_Sidang
        query = ("SELECT id_jadwal, tanggal_sidang, agenda, lokasi_sidang FROM tbl_jadwal "
                 "WHERE fk_id_perkara = %s AND (agenda LIKE %s OR lokasi_sidang LIKE %s) "
                 "ORDER BY tanggal_sidang DESC")
        args = (id_perkara, keyword_like, keyword_like)
        aksiCur.execute(query, args)
        hasil = aksiCur.fetchall()
        aksiCur.close()
        return hasil
