"""
Database Module - Toko Ayah
===========================
Mengelola koneksi SQLite dan inisialisasi semua tabel.
Semua query dasar (CRUD) ada di sini.

Desain:
- Menggunakan sqlite3.Row agar bisa akses kolom dengan nama
- Semua tabel punya created_at untuk tracking
- Index pada kolom yang sering dicari
- Siap di-migrasi ke PocketBase di masa depan
"""

import sqlite3
import hashlib
import os
from typing import Optional, Any
from datetime import datetime


# ==============================================================================
# Path database - relatif terhadap folder proyek
# ==============================================================================
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
DB_PATH: str = os.path.join(DATA_DIR, "toko.db")


def _ensure_data_dir() -> None:
    """Pastikan folder 'data/' ada."""
    os.makedirs(DATA_DIR, exist_ok=True)


# ==============================================================================
# Koneksi Database
# ==============================================================================
def get_connection() -> sqlite3.Connection:
    """
    Buat dan kembalikan koneksi ke database SQLite.
    Menggunakan row_factory = sqlite3.Row agar kolom bisa diakses by name.
    """
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")        # Write-Ahead Logging
    conn.execute("PRAGMA foreign_keys=ON")          # Enforce foreign keys
    return conn


# ==============================================================================
# Inisialisasi Tabel
# ==============================================================================
def init_database() -> None:
    """
    Buat semua tabel yang dibutuhkan jika belum ada.
    Urutan: users → products → spare_parts → customers → sales →
            sale_items → repair_orders → repair_order_items →
            stock_movements → settings
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ------------------------------------------------------------------
        # 1. users - Pengguna aplikasi
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ------------------------------------------------------------------
        # 2. products - Produk yang dijual
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
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
            )
        """)

        # ------------------------------------------------------------------
        # 3. spare_parts - Sparepart untuk servis
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spare_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                kompatibel TEXT,
                harga REAL NOT NULL,
                stok INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ------------------------------------------------------------------
        # 4. customers - Data pelanggan
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT NOT NULL,
                no_hp TEXT,
                alamat TEXT,
                catatan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ------------------------------------------------------------------
        # 5. sales - Transaksi penjualan (header)
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                user_id INTEGER,
                total REAL NOT NULL,
                metode_bayar TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ------------------------------------------------------------------
        # 6. sale_items - Detail item penjualan
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                qty INTEGER NOT NULL,
                harga_satuan REAL NOT NULL,
                diskon REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        """)

        # ------------------------------------------------------------------
        # 7. repair_orders - Order servis / perbaikan
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                user_id INTEGER,
                device_merk TEXT,
                device_tipe TEXT,
                device_serial TEXT,
                keluhan TEXT,
                status TEXT DEFAULT 'Diterima',
                estimasi_biaya REAL,
                total_biaya REAL,
                tanggal_masuk DATE,
                tanggal_selesai DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # ------------------------------------------------------------------
        # 8. repair_order_items - Sparepart yang digunakan di servis
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_order_id INTEGER NOT NULL,
                spare_part_id INTEGER,
                qty INTEGER DEFAULT 1,
                harga_satuan REAL,
                keterangan TEXT,
                FOREIGN KEY (repair_order_id) REFERENCES repair_orders(id),
                FOREIGN KEY (spare_part_id) REFERENCES spare_parts(id)
            )
        """)

        # ------------------------------------------------------------------
        # 9. stock_movements - Riwayat pergerakan stok
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                spare_part_id INTEGER,
                tipe TEXT,
                qty INTEGER NOT NULL,
                keterangan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ------------------------------------------------------------------
        # 10. settings - Pengaturan toko
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY DEFAULT 1,
                nama_toko TEXT,
                alamat TEXT,
                no_hp TEXT,
                logo_path TEXT,
                ppn_rate REAL DEFAULT 0.11
            )
        """)

        # ------------------------------------------------------------------
        # INDEX - untuk pencarian cepat
        # ------------------------------------------------------------------
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_nama 
            ON products(nama)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_products_kode 
            ON products(kode)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customers_nama 
            ON customers(nama)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_customers_no_hp 
            ON customers(no_hp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_repair_orders_status 
            ON repair_orders(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sales_created_at 
            ON sales(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_spare_parts_nama 
            ON spare_parts(nama)
        """)

        conn.commit()
        print("[OK] Database berhasil diinisialisasi!")

    except sqlite3.Error as e:
        print(f"[ERROR] Gagal menginisialisasi database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


# ==============================================================================
# Seed Data - Data Awal
# ==============================================================================
def seed_default_data() -> None:
    """
    Masukkan data default jika tabel masih kosong.
    - 1 user admin default
    - 1 setting toko default
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Cek apakah sudah ada user
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        user_count = cursor.fetchone()["cnt"]

        if user_count == 0:
            # Buat user admin default (password: admin123)
            hashed_pw = hash_password("admin123")
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", hashed_pw, "admin")
            )
            print("[OK] User admin default dibuat (username: admin, password: admin123)")

        # Cek apakah settings sudah ada
        cursor.execute("SELECT COUNT(*) as cnt FROM settings")
        settings_count = cursor.fetchone()["cnt"]

        if settings_count == 0:
            cursor.execute("""
                INSERT INTO settings (nama_toko, alamat, no_hp, ppn_rate) 
                VALUES (?, ?, ?, ?)
            """, ("Toko Ayah", "Jl. Contoh No. 1", "08123456789", 0.11))
            print("[OK] Pengaturan toko default dibuat")

        conn.commit()

    except sqlite3.Error as e:
        print(f"[ERROR] Gagal membuat data awal: {e}")
        conn.rollback()
    finally:
        conn.close()


# ==============================================================================
# Helper Functions
# ==============================================================================
def hash_password(password: str) -> str:
    """Hash password menggunakan SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verifikasi password terhadap hash."""
    return hash_password(password) == hashed


# ==============================================================================
# CRUD Operations - Generic
# ==============================================================================
def execute_query(
    query: str,
    params: tuple = (),
    fetch_one: bool = False,
    fetch_all: bool = False
) -> Any:
    """
    Eksekusi query SQL dengan parameter.
    
    Args:
        query: String SQL query
        params: Tuple parameter untuk query
        fetch_one: Jika True, kembalikan satu baris
        fetch_all: Jika True, kembalikan semua baris
    
    Returns:
        Hasil query atau lastrowid untuk INSERT
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)

        if fetch_one:
            result = cursor.fetchone()
            return dict(result) if result else None
        elif fetch_all:
            results = cursor.fetchall()
            return [dict(row) for row in results]
        else:
            conn.commit()
            return cursor.lastrowid

    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()


# ==============================================================================
# User Operations
# ==============================================================================
def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Autentikasi user berdasarkan username dan password.
    
    Returns:
        Dict user jika berhasil, None jika gagal
    """
    hashed = hash_password(password)
    return execute_query(
        "SELECT id, username, role FROM users WHERE username = ? AND password = ?",
        (username, hashed),
        fetch_one=True
    )


# ==============================================================================
# Product Operations
# ==============================================================================
def get_all_products(search: str = "") -> list[dict]:
    """Ambil semua produk, opsional dengan pencarian."""
    if search:
        return execute_query(
            """SELECT * FROM products 
               WHERE nama LIKE ? OR kode LIKE ? OR merk LIKE ?
               ORDER BY nama""",
            (f"%{search}%", f"%{search}%", f"%{search}%"),
            fetch_all=True
        )
    return execute_query(
        "SELECT * FROM products ORDER BY nama",
        fetch_all=True
    )


def get_product_by_id(product_id: int) -> Optional[dict]:
    """Ambil produk berdasarkan ID."""
    return execute_query(
        "SELECT * FROM products WHERE id = ?",
        (product_id,),
        fetch_one=True
    )


def get_product_by_kode(kode: str) -> Optional[dict]:
    """Ambil produk berdasarkan kode/barcode."""
    return execute_query(
        "SELECT * FROM products WHERE kode = ?",
        (kode,),
        fetch_one=True
    )


def add_product(
    nama: str,
    harga_jual: float,
    kode: str = "",
    kategori: str = "",
    merk: str = "",
    tipe: str = "",
    harga_beli: float = 0,
    stok: int = 0,
    serial: str = ""
) -> int:
    """Tambah produk baru. Mengembalikan ID produk."""
    return execute_query(
        """INSERT INTO products 
           (kode, nama, kategori, merk, tipe, harga_beli, harga_jual, stok, serial)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (kode, nama, kategori, merk, tipe, harga_beli, harga_jual, stok, serial)
    )


def update_product(product_id: int, **kwargs) -> None:
    """Update produk berdasarkan field yang diberikan."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = tuple(kwargs.values()) + (product_id,)
    execute_query(f"UPDATE products SET {fields} WHERE id = ?", values)


def delete_product(product_id: int) -> None:
    """Hapus produk berdasarkan ID."""
    execute_query("DELETE FROM products WHERE id = ?", (product_id,))


def update_product_stock(product_id: int, qty_change: int, keterangan: str = "") -> None:
    """
    Update stok produk dan catat ke stock_movements.
    qty_change positif = stok masuk, negatif = stok keluar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE products SET stok = stok + ? WHERE id = ?",
            (qty_change, product_id)
        )
        tipe = "masuk" if qty_change > 0 else "keluar"
        cursor.execute(
            """INSERT INTO stock_movements 
               (product_id, tipe, qty, keterangan) 
               VALUES (?, ?, ?, ?)""",
            (product_id, tipe, abs(qty_change), keterangan)
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Gagal update stok: {e}")
    finally:
        conn.close()


# ==============================================================================
# Spare Parts Operations
# ==============================================================================
def get_all_spare_parts(search: str = "") -> list[dict]:
    """Ambil semua sparepart, opsional dengan pencarian."""
    if search:
        return execute_query(
            """SELECT * FROM spare_parts 
               WHERE nama LIKE ? OR kompatibel LIKE ?
               ORDER BY nama""",
            (f"%{search}%", f"%{search}%"),
            fetch_all=True
        )
    return execute_query(
        "SELECT * FROM spare_parts ORDER BY nama",
        fetch_all=True
    )


def get_spare_part_by_id(part_id: int) -> Optional[dict]:
    """Ambil sparepart berdasarkan ID."""
    return execute_query(
        "SELECT * FROM spare_parts WHERE id = ?",
        (part_id,),
        fetch_one=True
    )


def add_spare_part(
    nama: str,
    harga: float,
    kompatibel: str = "",
    stok: int = 0
) -> int:
    """Tambah sparepart baru."""
    return execute_query(
        """INSERT INTO spare_parts (nama, kompatibel, harga, stok)
           VALUES (?, ?, ?, ?)""",
        (nama, kompatibel, harga, stok)
    )


def update_spare_part(part_id: int, **kwargs) -> None:
    """Update sparepart berdasarkan field yang diberikan."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = tuple(kwargs.values()) + (part_id,)
    execute_query(f"UPDATE spare_parts SET {fields} WHERE id = ?", values)


def delete_spare_part(part_id: int) -> None:
    """Hapus sparepart berdasarkan ID."""
    execute_query("DELETE FROM spare_parts WHERE id = ?", (part_id,))


def update_spare_part_stock(part_id: int, qty_change: int, keterangan: str = "") -> None:
    """Update stok sparepart dan catat ke stock_movements."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE spare_parts SET stok = stok + ? WHERE id = ?",
            (qty_change, part_id)
        )
        tipe = "masuk" if qty_change > 0 else "keluar"
        cursor.execute(
            """INSERT INTO stock_movements 
               (spare_part_id, tipe, qty, keterangan) 
               VALUES (?, ?, ?, ?)""",
            (part_id, tipe, abs(qty_change), keterangan)
        )
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Gagal update stok sparepart: {e}")
    finally:
        conn.close()


# ==============================================================================
# Customer Operations
# ==============================================================================
def get_all_customers(search: str = "") -> list[dict]:
    """Ambil semua pelanggan, opsional dengan pencarian."""
    if search:
        return execute_query(
            """SELECT * FROM customers 
               WHERE nama LIKE ? OR no_hp LIKE ?
               ORDER BY nama""",
            (f"%{search}%", f"%{search}%"),
            fetch_all=True
        )
    return execute_query(
        "SELECT * FROM customers ORDER BY nama",
        fetch_all=True
    )


def get_customer_by_id(customer_id: int) -> Optional[dict]:
    """Ambil pelanggan berdasarkan ID."""
    return execute_query(
        "SELECT * FROM customers WHERE id = ?",
        (customer_id,),
        fetch_one=True
    )


def add_customer(
    nama: str,
    no_hp: str = "",
    alamat: str = "",
    catatan: str = ""
) -> int:
    """Tambah pelanggan baru."""
    return execute_query(
        """INSERT INTO customers (nama, no_hp, alamat, catatan)
           VALUES (?, ?, ?, ?)""",
        (nama, no_hp, alamat, catatan)
    )


def update_customer(customer_id: int, **kwargs) -> None:
    """Update pelanggan berdasarkan field yang diberikan."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = tuple(kwargs.values()) + (customer_id,)
    execute_query(f"UPDATE customers SET {fields} WHERE id = ?", values)


def delete_customer(customer_id: int) -> None:
    """Hapus pelanggan berdasarkan ID."""
    execute_query("DELETE FROM customers WHERE id = ?", (customer_id,))


# ==============================================================================
# Sales Operations
# ==============================================================================
def create_sale(
    items: list[dict],
    customer_id: Optional[int] = None,
    user_id: Optional[int] = None,
    metode_bayar: str = "Tunai"
) -> int:
    """
    Buat transaksi penjualan baru (header + items + update stok).
    
    Args:
        items: List of dict {product_id, qty, harga_satuan, diskon}
        customer_id: ID pelanggan (opsional)
        user_id: ID user kasir
        metode_bayar: Tunai / Transfer / QRIS
    
    Returns:
        ID transaksi yang baru dibuat
    """
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Hitung total
        total = sum(
            (item["harga_satuan"] * item["qty"]) - item.get("diskon", 0)
            for item in items
        )

        # Insert header sale
        cursor.execute(
            """INSERT INTO sales (customer_id, user_id, total, metode_bayar)
               VALUES (?, ?, ?, ?)""",
            (customer_id, user_id, total, metode_bayar)
        )
        sale_id = cursor.lastrowid

        # Insert detail items + update stok
        for item in items:
            subtotal = (item["harga_satuan"] * item["qty"]) - item.get("diskon", 0)
            cursor.execute(
                """INSERT INTO sale_items 
                   (sale_id, product_id, qty, harga_satuan, diskon, subtotal)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (sale_id, item["product_id"], item["qty"],
                 item["harga_satuan"], item.get("diskon", 0), subtotal)
            )
            # Kurangi stok produk
            cursor.execute(
                "UPDATE products SET stok = stok - ? WHERE id = ?",
                (item["qty"], item["product_id"])
            )
            # Catat pergerakan stok
            cursor.execute(
                """INSERT INTO stock_movements 
                   (product_id, tipe, qty, keterangan)
                   VALUES (?, 'keluar', ?, ?)""",
                (item["product_id"], item["qty"], f"Penjualan #{sale_id}")
            )

        conn.commit()
        return sale_id

    except sqlite3.Error as e:
        conn.rollback()
        raise Exception(f"Gagal membuat transaksi: {e}")
    finally:
        conn.close()


def get_sale_by_id(sale_id: int) -> Optional[dict]:
    """Ambil transaksi beserta detail items."""
    sale = execute_query(
        """SELECT s.*, c.nama as customer_nama 
           FROM sales s 
           LEFT JOIN customers c ON s.customer_id = c.id
           WHERE s.id = ?""",
        (sale_id,),
        fetch_one=True
    )
    if sale:
        sale["items"] = execute_query(
            """SELECT si.*, p.nama as product_nama, p.kode as product_kode
               FROM sale_items si
               JOIN products p ON si.product_id = p.id
               WHERE si.sale_id = ?""",
            (sale_id,),
            fetch_all=True
        )
    return sale


def get_all_sales() -> list[dict]:
    """Ambil semua data transaksi penjualan (untuk laporan)."""
    return execute_query(
        """SELECT s.*, c.nama as customer_nama, u.username
           FROM sales s
           LEFT JOIN customers c ON s.customer_id = c.id
           LEFT JOIN users u ON s.user_id = u.id
           ORDER BY s.created_at DESC""",
        fetch_all=True
    )


def get_sales_today() -> list[dict]:
    """Ambil semua transaksi hari ini."""
    return execute_query(
        """SELECT s.*, c.nama as customer_nama 
           FROM sales s
           LEFT JOIN customers c ON s.customer_id = c.id
           WHERE DATE(s.created_at) = DATE('now', 'localtime')
           ORDER BY s.created_at DESC""",
        fetch_all=True
    )


def get_sales_summary_today() -> dict:
    """Ambil ringkasan penjualan hari ini."""
    result = execute_query(
        """SELECT COUNT(*) as jumlah_transaksi, 
                  COALESCE(SUM(total), 0) as total_penjualan
           FROM sales 
           WHERE DATE(created_at) = DATE('now', 'localtime')""",
        fetch_one=True
    )
    return result or {"jumlah_transaksi": 0, "total_penjualan": 0}


def get_sales_summary_month() -> dict:
    """Ambil ringkasan penjualan bulan ini."""
    result = execute_query(
        """SELECT COUNT(*) as jumlah_transaksi,
                  COALESCE(SUM(total), 0) as total_penjualan
           FROM sales
           WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')""",
        fetch_one=True
    )
    return result or {"jumlah_transaksi": 0, "total_penjualan": 0}


# ==============================================================================
# Repair Order Operations
# ==============================================================================
def create_repair_order(
    customer_id: int,
    device_merk: str = "",
    device_tipe: str = "",
    device_serial: str = "",
    keluhan: str = "",
    estimasi_biaya: float = 0,
    user_id: Optional[int] = None
) -> int:
    """Buat order servis baru."""
    return execute_query(
        """INSERT INTO repair_orders 
           (customer_id, user_id, device_merk, device_tipe, device_serial, 
            keluhan, status, estimasi_biaya, tanggal_masuk)
           VALUES (?, ?, ?, ?, ?, ?, 'Diterima', ?, DATE('now', 'localtime'))""",
        (customer_id, user_id, device_merk, device_tipe, device_serial,
         keluhan, estimasi_biaya)
    )


def get_all_repair_orders(status_filter: str = "") -> list[dict]:
    """Ambil semua order servis, opsional filter status."""
    if status_filter:
        return execute_query(
            """SELECT ro.*, c.nama as customer_nama, c.no_hp as customer_hp
               FROM repair_orders ro
               JOIN customers c ON ro.customer_id = c.id
               WHERE ro.status = ?
               ORDER BY ro.created_at DESC""",
            (status_filter,),
            fetch_all=True
        )
    return execute_query(
        """SELECT ro.*, c.nama as customer_nama, c.no_hp as customer_hp
           FROM repair_orders ro
           JOIN customers c ON ro.customer_id = c.id
           ORDER BY ro.created_at DESC""",
        fetch_all=True
    )


def get_repair_order_by_id(order_id: int) -> Optional[dict]:
    """Ambil detail order servis beserta items."""
    order = execute_query(
        """SELECT ro.*, c.nama as customer_nama, c.no_hp as customer_hp, c.alamat as customer_alamat
           FROM repair_orders ro
           JOIN customers c ON ro.customer_id = c.id
           WHERE ro.id = ?""",
        (order_id,),
        fetch_one=True
    )
    if order:
        order["items"] = execute_query(
            """SELECT roi.*, sp.nama as spare_part_nama
               FROM repair_order_items roi
               LEFT JOIN spare_parts sp ON roi.spare_part_id = sp.id
               WHERE roi.repair_order_id = ?""",
            (order_id,),
            fetch_all=True
        )
    return order


def update_repair_status(order_id: int, new_status: str) -> None:
    """Update status order servis."""
    updates = {"status": new_status}
    if new_status == "Selesai":
        updates["tanggal_selesai"] = datetime.now().strftime("%Y-%m-%d")
    
    fields = ", ".join(f"{k} = ?" for k in updates.keys())
    values = tuple(updates.values()) + (order_id,)
    execute_query(f"UPDATE repair_orders SET {fields} WHERE id = ?", values)


def add_repair_order_item(
    repair_order_id: int,
    spare_part_id: Optional[int] = None,
    qty: int = 1,
    harga_satuan: float = 0,
    keterangan: str = ""
) -> int:
    """Tambah item sparepart ke order servis."""
    return execute_query(
        """INSERT INTO repair_order_items 
           (repair_order_id, spare_part_id, qty, harga_satuan, keterangan)
           VALUES (?, ?, ?, ?, ?)""",
        (repair_order_id, spare_part_id, qty, harga_satuan, keterangan)
    )


def get_active_repairs_count() -> int:
    """Hitung jumlah servis yang masih aktif (belum Diambil)."""
    result = execute_query(
        """SELECT COUNT(*) as cnt FROM repair_orders 
           WHERE status NOT IN ('Diambil', 'Selesai')""",
        fetch_one=True
    )
    return result["cnt"] if result else 0


# ==============================================================================
# Settings Operations
# ==============================================================================
def get_settings() -> Optional[dict]:
    """Ambil pengaturan toko."""
    return execute_query(
        "SELECT * FROM settings WHERE id = 1",
        fetch_one=True
    )


def update_settings(**kwargs) -> None:
    """Update pengaturan toko."""
    if not kwargs:
        return
    fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
    values = tuple(kwargs.values()) + (1,)
    execute_query(f"UPDATE settings SET {fields} WHERE id = ?", values)


# ==============================================================================
# Dashboard Statistics
# ==============================================================================
def get_low_stock_products(threshold: int = 5) -> list[dict]:
    """Ambil produk dengan stok rendah."""
    return execute_query(
        "SELECT * FROM products WHERE stok <= ? ORDER BY stok ASC",
        (threshold,),
        fetch_all=True
    )


def get_low_stock_spare_parts(threshold: int = 3) -> list[dict]:
    """Ambil sparepart dengan stok rendah."""
    return execute_query(
        "SELECT * FROM spare_parts WHERE stok <= ? ORDER BY stok ASC",
        (threshold,),
        fetch_all=True
    )
