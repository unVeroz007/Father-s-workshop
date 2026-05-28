# Technical Architecture Document
## Aplikasi Toko Ayah (Desktop)

**Versi**: 1.0  
**Tanggal**: 28 Mei 2026

---

### 1. Architecture Overview

**Pattern**: Modular Monolith (Desktop App)

**Komponen Utama**:
- **UI Layer** (Flet) → Screens & Components
- **Business Logic Layer** → core/ (models, services)
- **Data Layer** → SQLite via core/database.py
- **Utility Layer** → Backup, Export, WA Notification

---

### 2. Folder Structure (Final)

```
toko-ayah/
├── main.py                    # Entry point + routing
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── database.py            # Koneksi & init DB
│   ├── models.py              # Class untuk setiap tabel
│   ├── services.py            # Business logic (kasir, servis, laporan)
│   └── utils.py               # Backup, format rupiah, WA helper
├── ui/
│   ├── components/            # Reusable components (tombol besar, tabel, dll)
│   └── screens/
│       ├── login.py
│       ├── dashboard.py
│       ├── kasir.py
│       ├── servis.py
│       ├── laporan.py
│       └── settings.py
├── assets/
├── data/
│   └── toko.db
└── docs/
```

---

### 3. Module Responsibility

| Module          | Tanggung Jawab |
|-----------------|----------------|
| `core/database.py` | Koneksi SQLite, init tabel, query dasar |
| `core/models.py`   | Class Product, Customer, RepairOrder, dll |
| `core/services.py` | Logika bisnis (proses kasir, update stok, hitung total servis) |
| `core/utils.py`    | Export Excel, Kirim WA, Backup otomatis |
| `ui/screens/`      | Setiap halaman aplikasi (UI) |
| `ui/components/`   | Tombol besar, Search Bar, Confirmation Dialog |

---

### 4. Data Flow (Contoh Kasir)

1. User buka halaman Kasir
2. Ketik / scan barcode → panggil `services.search_product()`
3. Tambah ke keranjang → update UI
4. Klik Bayar → `services.process_sale()` → kurangi stok + simpan transaksi
5. Cetak struk + (opsional) kirim WA

---

### 5. Design Principles

- **Single Responsibility**: Setiap file punya satu tanggung jawab jelas
- **Separation of Concerns**: UI terpisah dari Business Logic
- **Easy to Extend**: Mudah ditambahkan fitur baru atau diubah ke PocketBase nanti
- **Error Handling**: Semua aksi penting punya try-except + pesan ramah

---

### 6. Future Migration Path (ke PocketBase)

- Ganti `core/database.py` dengan client PocketBase
- UI layer hampir tidak berubah
- Tambah real-time listener di layar yang membutuhkan (misal Daftar Servis)

---

*Dokumen ini membantu AI memahami struktur kode yang rapi dan scalable.*