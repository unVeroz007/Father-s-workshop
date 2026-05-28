# Database Schema - Toko Ayah

**Database**: SQLite  
**File**: `data/toko.db`

---

### ERD (Entity Relationship Diagram) - Text Version

```
users (1) ---- (many) sales
users (1) ---- (many) repair_orders

products (1) ---- (many) sale_items
products (1) ---- (many) repair_order_items
products (1) ---- (many) stock_movements

customers (1) ---- (many) sales
customers (1) ---- (many) repair_orders

spare_parts (1) ---- (many) repair_order_items
```

---

### Tabel Lengkap + SQL

#### 1. users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,           -- hashed
    role TEXT DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. products
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode TEXT UNIQUE,
    nama TEXT NOT NULL,
    kategori TEXT,
    merk TEXT,
    tipe TEXT,
    harga_beli REAL DEFAULT 0,
    harga_jual REAL NOT NULL,
    stok INTEGER DEFAULT 0,
    serial TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. spare_parts
```sql
CREATE TABLE spare_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    kompatibel TEXT,                  -- merk/tipe yang cocok
    harga REAL NOT NULL,
    stok INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. customers
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT NOT NULL,
    no_hp TEXT,
    alamat TEXT,
    catatan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. sales
```sql
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    total REAL NOT NULL,
    metode_bayar TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### 6. sale_items
```sql
CREATE TABLE sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty INTEGER NOT NULL,
    harga_satuan REAL NOT NULL,
    diskon REAL DEFAULT 0,
    subtotal REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

#### 7. repair_orders
```sql
CREATE TABLE repair_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    device_merk TEXT,
    device_tipe TEXT,
    device_serial TEXT,
    keluhan TEXT,
    status TEXT DEFAULT 'Diterima',   -- Diterima, Diagnosa, Menunggu Sparepart, Perbaikan, Selesai, Diambil
    estimasi_biaya REAL,
    total_biaya REAL,
    tanggal_masuk DATE,
    tanggal_selesai DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

#### 8. repair_order_items
```sql
CREATE TABLE repair_order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_order_id INTEGER NOT NULL,
    spare_part_id INTEGER,
    qty INTEGER DEFAULT 1,
    harga_satuan REAL,
    keterangan TEXT,
    FOREIGN KEY (repair_order_id) REFERENCES repair_orders(id),
    FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id)
);
```

#### 9. stock_movements
```sql
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    spare_part_id INTEGER,
    tipe TEXT,                        -- 'masuk', 'keluar', 'opname'
    qty INTEGER NOT NULL,
    keterangan TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 10. settings
```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    nama_toko TEXT,
    alamat TEXT,
    no_hp TEXT,
    logo_path TEXT,
    ppn_rate REAL DEFAULT 0.11
);
```

---

### Catatan Penting untuk AI

- Gunakan `row_factory = sqlite3.Row` agar bisa akses kolom dengan nama
- Semua tabel punya `created_at` untuk tracking
- Status servis menggunakan string yang jelas (bisa dibuat enum nanti)
- Siapkan index pada kolom yang sering dicari (nama produk, no_hp pelanggan)

---

*Schema ini sudah dirancang agar mudah di-migrasi ke PocketBase nanti.*