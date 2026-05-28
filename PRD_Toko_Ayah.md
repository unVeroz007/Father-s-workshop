# PRD - Product Requirements Document
## Aplikasi Kasir & Manajemen Servis Toko Elektronik "Toko Ayah"

**Versi**: 1.0  
**Tanggal**: 28 Mei 2026  
**Pengembang**: [Nama Kamu]  
**Stakeholder Utama**: Ayah (Pensiunan PNS)

---

### 1. Executive Summary

Aplikasi desktop untuk membantu ayah menjalankan toko elektronik + jasa perbaikan (kulkas, mesin cuci, kipas, AC, dll). Aplikasi harus **sangat mudah digunakan** oleh orang tua, lengkap, aman, dan siap dikembangkan ke versi mobile di masa depan.

**Tujuan Utama**:
- Mempercepat proses kasir dan pencatatan servis
- Mengurangi kesalahan hitung dan pencatatan manual
- Memberikan visibilitas performa toko secara real-time (nantinya via HP)
- Biaya pengembangan = Rp 0

---

### 2. User Personas

**Persona Utama: Ayah**
- Usia: 60+ tahun
- Pensiunan PNS
- Tidak terbiasa dengan teknologi rumit
- Butuh UI sangat sederhana, tombol besar, font jelas
- Bahasa Indonesia
- Prioritas: Kemudahan > Fitur canggih

**Persona Sekunder**:
- Kamu (Developer) – butuh kode yang maintainable dan scalable

---

### 3. Functional Requirements

#### 3.1 Master Data
- Kelola Produk (tambah, edit, hapus, cari)
- Kelola Sparepart
- Kelola Pelanggan (nama, no HP, alamat, catatan)
- Kelola User (sederhana, 1 admin utama)

#### 3.2 Modul Kasir (Penjualan)
- Pencarian produk cepat (nama/kode/serial)
- **Barcode Scanner** (USB Scanner)
- Keranjang belanja dengan qty & diskon
- Perhitungan otomatis (subtotal, PPN 11%, total)
- Metode pembayaran: Tunai, Transfer, QRIS
- Cetak struk (PDF + thermal printer)
- Kurangi stok otomatis

#### 3.3 Modul Servis / Perbaikan
- Buat Order Servis baru
- Input detail perangkat (merk, tipe, serial, keluhan)
- Status workflow (Diterima → Diagnosa → Menunggu Sparepart → Perbaikan → Selesai → Diambil)
- Tambah sparepart yang digunakan + biaya jasa
- Total biaya otomatis
- Riwayat servis per pelanggan
- **Notifikasi WA** ke pelanggan

#### 3.4 Laporan & Analitik
- Laporan Penjualan harian/bulanan
- Laporan Servis
- Laporan Stok
- **Export ke Excel**
- Dashboard statistik sederhana (total hari ini, top produk, dll)

#### 3.5 Fitur Pendukung
- Backup otomatis harian
- Pengaturan toko (nama, alamat, kontak, logo)
- Login sederhana

---

### 4. Non-Functional Requirements

- **Usability**: UI sangat sederhana, tombol besar (≥70px), font ≥18px, konfirmasi setiap aksi
- **Performance**: Respons cepat (<1 detik untuk transaksi)
- **Security**: Password hash, validasi input, backup otomatis
- **Maintainability**: Kode modular, komentar jelas, struktur rapi
- **Scalability**: Desain modular agar mudah upgrade ke PocketBase + Mobile nanti

---

### 5. Tech Stack

- **Frontend**: Flet (Python)
- **Database**: SQLite (lokal)
- **Library Tambahan**:
  - pandas + openpyxl (Export Excel)
  - pywhatkit (Notifikasi WA)
- **Packaging**: PyInstaller (.exe)

---

### 6. Future Roadmap (Fase 2)

- Upgrade ke **PocketBase** sebagai backend
- Buat versi **Flet Web** atau **Flutter Mobile**
- Real-time sync ke HP ayah
- Multi-user (kasir + admin)
- Hosting opsional (untuk akses dari mana saja)

---

### 7. Success Metrics

- Ayah bisa menggunakan aplikasi tanpa bantuan setelah 2-3 hari training
- Waktu proses transaksi kasir < 30 detik
- Tidak ada kesalahan stok atau hitung dalam 1 bulan pertama
- Backup berjalan otomatis setiap hari

---

**Dokumen ini dibuat untuk memastikan AI coding agent (Antigravity / Cursor / Claude) memahami semua kebutuhan dengan sempurna.**

---

*End of PRD v1.0*