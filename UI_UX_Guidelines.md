# UI/UX Guidelines - Toko Ayah
## Khusus untuk Pengguna Lansia (60+ tahun)

**Versi**: 1.0  
**Tanggal**: 28 Mei 2026

---

### 1. Prinsip Utama

- **Simplicity First**: Semakin sedikit tombol dan menu, semakin baik
- **Large & Clear**: Semua elemen interaktif harus besar dan jelas
- **Zero Confusion**: Tidak boleh ada istilah teknis
- **Forgiving**: Selalu ada tombol "Batal" dan konfirmasi sebelum aksi penting
- **Bahasa Indonesia 100%**

---

### 2. Spesifikasi Visual

| Elemen              | Spesifikasi                          | Alasan |
|---------------------|--------------------------------------|--------|
| **Font Size**       | Minimal 18px (body), 24px (judul)   | Mudah dibaca |
| **Tombol**          | Minimal 70px tinggi, 200px lebar    | Mudah ditekan |
| **Spacing**         | Padding minimal 20px antar elemen   | Tidak crowded |
| **Warna**           | Hijau (#2E7D32) + Biru (#1565C0)    | Tenang & profesional |
| **Background**      | Putih atau abu muda                 | Kontras tinggi |
| **Mode**            | Light mode default                  | Lebih nyaman untuk lansia |

---

### 3. Navigasi

**Rekomendasi**: **Sidebar Kiri** (bukan tab atas)

Menu Utama (hanya 5):
1. **Dashboard** (Beranda)
2. **Kasir** (Penjualan)
3. **Servis** (Perbaikan)
4. **Laporan**
5. **Pengaturan**

Setiap menu harus punya **icon besar** + teks jelas.

---

### 4. Pattern UI yang Wajib

#### 4.1 Konfirmasi Dialog
Setiap aksi penting harus muncul dialog:
- "Yakin ingin menyelesaikan transaksi ini?"
- Tombol: **Ya, Lanjutkan** (hijau) | **Batal** (abu)

#### 4.2 Search Bar
- Sangat besar
- Placeholder: "Ketik nama produk atau scan barcode..."
- Hasil muncul otomatis saat mengetik

#### 4.3 Tabel
- Font besar
- Baris minimal 50px tinggi
- Warna selang-seling (putih & abu muda)
- Tombol aksi di ujung kanan

---

### 5. Halaman Penting & Spesifikasi

#### Dashboard
- 4 kartu besar di atas (Penjualan Hari Ini, Servis Aktif, Stok Rendah, Total Bulan Ini)
- Grafik sederhana (opsional)
- Tombol cepat: "Mulai Kasir" & "Buat Servis Baru"

#### Halaman Kasir
- Bagian kiri: Daftar produk + search + barcode
- Bagian kanan: Keranjang belanja
- Bagian bawah: Total + tombol Bayar (sangat besar)

#### Halaman Servis
- Form input besar
- Status ditampilkan dengan **warna**:
  - Biru = Diterima
  - Kuning = Diagnosa / Menunggu Sparepart
  - Hijau = Selesai
  - Merah = Diambil

---

### 6. Aksesibilitas

- Hindari warna merah-hijau untuk status penting (gunakan ikon + teks juga)
- Semua tombol harus bisa diakses dengan keyboard
- Pesan error harus jelas dan ramah ("Stok tidak cukup" bukan "Error 404")

---

### 7. Testing Checklist untuk Ayah

- [ ] Bisa menyelesaikan 1 transaksi kasir tanpa bantuan
- [ ] Bisa membuat 1 order servis tanpa bantuan
- [ ] Bisa membaca laporan harian
- [ ] Tidak bingung saat ada error

---

*Dokumen ini wajib dibaca oleh AI coding agent agar menghasilkan UI yang benar-benar ramah lansia.*