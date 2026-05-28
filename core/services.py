"""
Services Module - Toko Ayah
============================
Semua logika bisnis ada di sini.
Layer ini menjadi penghubung antara UI dan Database.

Tanggung jawab:
- Proses kasir (validasi, hitung total, simpan transaksi)
- Proses servis (buat order, update status, hitung biaya)
- Pencarian produk/pelanggan
- Statistik dashboard
"""

from typing import Optional
from core import database as db
from core.models import CartItem, RepairStatus, MetodeBayar


# ==============================================================================
# Kasir / Penjualan
# ==============================================================================
def search_product(keyword: str) -> list[dict]:
    """
    Cari produk berdasarkan nama, kode, atau merk.
    Digunakan oleh search bar dan barcode scanner.
    """
    return db.get_all_products(search=keyword)


def search_product_by_barcode(barcode: str) -> Optional[dict]:
    """
    Cari produk berdasarkan barcode/kode.
    Digunakan oleh barcode scanner (USB).
    """
    return db.get_product_by_kode(barcode)


def validate_cart(cart_items: list[CartItem]) -> tuple[bool, str]:
    """
    Validasi keranjang sebelum transaksi.
    
    Returns:
        (is_valid, pesan_error)
    """
    if not cart_items:
        return False, "Keranjang masih kosong!"

    for item in cart_items:
        product = db.get_product_by_id(item.product_id)
        if not product:
            return False, f"Produk '{item.product_nama}' tidak ditemukan!"
        if product["stok"] < item.qty:
            return (
                False,
                f"Stok '{item.product_nama}' tidak cukup! "
                f"(Tersedia: {product['stok']}, Diminta: {item.qty})"
            )
        if item.qty <= 0:
            return False, f"Jumlah '{item.product_nama}' harus lebih dari 0!"

    return True, ""


def calculate_cart_total(cart_items: list[CartItem], ppn_rate: float = 0.0) -> dict:
    """
    Hitung total keranjang dengan PPN.
    
    Returns:
        {subtotal, ppn, total}
    """
    subtotal = sum(item.subtotal for item in cart_items)
    ppn = subtotal * ppn_rate
    total = subtotal + ppn
    return {
        "subtotal": subtotal,
        "ppn": ppn,
        "total": total
    }


def process_sale(
    cart_items: list[CartItem],
    customer_id: Optional[int] = None,
    user_id: Optional[int] = None,
    metode_bayar: str = "Tunai"
) -> tuple[bool, str, Optional[int]]:
    """
    Proses transaksi penjualan lengkap.
    
    Returns:
        (success, message, sale_id)
    """
    # Validasi
    is_valid, error_msg = validate_cart(cart_items)
    if not is_valid:
        return False, error_msg, None

    try:
        # Konversi CartItem ke dict untuk database
        items_dict = [
            {
                "product_id": item.product_id,
                "qty": item.qty,
                "harga_satuan": item.harga_satuan,
                "diskon": item.diskon,
            }
            for item in cart_items
        ]

        sale_id = db.create_sale(
            items=items_dict,
            customer_id=customer_id,
            user_id=user_id,
            metode_bayar=metode_bayar
        )

        return True, "Transaksi berhasil disimpan!", sale_id

    except Exception as e:
        return False, f"Gagal menyimpan transaksi: {str(e)}", None


# ==============================================================================
# Servis / Perbaikan
# ==============================================================================
def create_service_order(
    customer_id: int,
    device_merk: str = "",
    device_tipe: str = "",
    device_serial: str = "",
    keluhan: str = "",
    estimasi_biaya: float = 0,
    user_id: Optional[int] = None
) -> tuple[bool, str, Optional[int]]:
    """
    Buat order servis baru.
    
    Returns:
        (success, message, order_id)
    """
    if not customer_id:
        return False, "Pelanggan harus dipilih!", None
    if not keluhan.strip():
        return False, "Keluhan tidak boleh kosong!", None

    try:
        order_id = db.create_repair_order(
            customer_id=customer_id,
            device_merk=device_merk,
            device_tipe=device_tipe,
            device_serial=device_serial,
            keluhan=keluhan,
            estimasi_biaya=estimasi_biaya,
            user_id=user_id
        )
        return True, f"Order servis #{order_id} berhasil dibuat!", order_id

    except Exception as e:
        return False, f"Gagal membuat order servis: {str(e)}", None


def advance_repair_status(order_id: int) -> tuple[bool, str]:
    """
    Majukan status servis ke tahap berikutnya.
    
    Returns:
        (success, message)
    """
    order = db.get_repair_order_by_id(order_id)
    if not order:
        return False, "Order servis tidak ditemukan!"

    current_status = order["status"]
    next_status = RepairStatus.get_next_status(current_status)

    if not next_status:
        return False, f"Status '{current_status}' sudah tahap terakhir!"

    try:
        db.update_repair_status(order_id, next_status)
        return True, f"Status berubah: {current_status} → {next_status}"
    except Exception as e:
        return False, f"Gagal update status: {str(e)}"


def set_repair_status(order_id: int, new_status: str) -> tuple[bool, str]:
    """
    Set status servis langsung ke status tertentu.
    
    Returns:
        (success, message)
    """
    valid_statuses = RepairStatus.get_all_statuses()
    if new_status not in valid_statuses:
        return False, f"Status '{new_status}' tidak valid!"

    try:
        db.update_repair_status(order_id, new_status)
        return True, f"Status berubah menjadi: {new_status}"
    except Exception as e:
        return False, f"Gagal update status: {str(e)}"


def add_part_to_repair(
    repair_order_id: int,
    spare_part_id: Optional[int] = None,
    qty: int = 1,
    harga_satuan: float = 0,
    keterangan: str = ""
) -> tuple[bool, str]:
    """
    Tambah sparepart ke order servis + update stok.
    
    Returns:
        (success, message)
    """
    try:
        # Jika ada spare_part_id, cek stok
        if spare_part_id:
            part = db.get_spare_part_by_id(spare_part_id)
            if not part:
                return False, "Sparepart tidak ditemukan!"
            if part["stok"] < qty:
                return (
                    False,
                    f"Stok sparepart '{part['nama']}' tidak cukup! "
                    f"(Tersedia: {part['stok']}, Diminta: {qty})"
                )
            # Gunakan harga dari sparepart jika tidak diset manual
            if harga_satuan == 0:
                harga_satuan = part["harga"]

        db.add_repair_order_item(
            repair_order_id=repair_order_id,
            spare_part_id=spare_part_id,
            qty=qty,
            harga_satuan=harga_satuan,
            keterangan=keterangan
        )

        # Kurangi stok sparepart jika ada
        if spare_part_id:
            db.update_spare_part_stock(
                spare_part_id, -qty,
                keterangan=f"Servis #{repair_order_id}"
            )

        # Update total biaya order
        _recalculate_repair_total(repair_order_id)

        return True, "Sparepart berhasil ditambahkan!"

    except Exception as e:
        return False, f"Gagal menambah sparepart: {str(e)}"


def _recalculate_repair_total(repair_order_id: int) -> None:
    """Hitung ulang total biaya servis dari semua items."""
    order = db.get_repair_order_by_id(repair_order_id)
    if order and order.get("items"):
        total = sum(
            (item.get("harga_satuan", 0) or 0) * (item.get("qty", 1) or 1)
            for item in order["items"]
        )
        db.execute_query(
            "UPDATE repair_orders SET total_biaya = ? WHERE id = ?",
            (total, repair_order_id)
        )


# ==============================================================================
# Master Data
# ==============================================================================
def add_new_product(
    nama: str,
    harga_jual: float,
    kode: str = "",
    kategori: str = "",
    merk: str = "",
    tipe: str = "",
    harga_beli: float = 0,
    stok: int = 0,
    serial: str = ""
) -> tuple[bool, str, Optional[int]]:
    """
    Tambah produk baru dengan validasi.
    
    Returns:
        (success, message, product_id)
    """
    if not nama.strip():
        return False, "Nama produk tidak boleh kosong!", None
    if harga_jual <= 0:
        return False, "Harga jual harus lebih dari 0!", None

    try:
        product_id = db.add_product(
            nama=nama, harga_jual=harga_jual, kode=kode,
            kategori=kategori, merk=merk, tipe=tipe,
            harga_beli=harga_beli, stok=stok, serial=serial
        )
        return True, f"Produk '{nama}' berhasil ditambahkan!", product_id
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return False, f"Kode produk '{kode}' sudah digunakan!", None
        return False, f"Gagal menambah produk: {str(e)}", None


def add_new_customer(
    nama: str,
    no_hp: str = "",
    alamat: str = "",
    catatan: str = ""
) -> tuple[bool, str, Optional[int]]:
    """
    Tambah pelanggan baru dengan validasi.
    
    Returns:
        (success, message, customer_id)
    """
    if not nama.strip():
        return False, "Nama pelanggan tidak boleh kosong!", None

    try:
        customer_id = db.add_customer(
            nama=nama, no_hp=no_hp,
            alamat=alamat, catatan=catatan
        )
        return True, f"Pelanggan '{nama}' berhasil ditambahkan!", customer_id
    except Exception as e:
        return False, f"Gagal menambah pelanggan: {str(e)}", None


def add_new_spare_part(
    nama: str,
    harga: float,
    kompatibel: str = "",
    stok: int = 0
) -> tuple[bool, str, Optional[int]]:
    """
    Tambah sparepart baru dengan validasi.
    
    Returns:
        (success, message, part_id)
    """
    if not nama.strip():
        return False, "Nama sparepart tidak boleh kosong!", None
    if harga <= 0:
        return False, "Harga harus lebih dari 0!", None

    try:
        part_id = db.add_spare_part(
            nama=nama, harga=harga,
            kompatibel=kompatibel, stok=stok
        )
        return True, f"Sparepart '{nama}' berhasil ditambahkan!", part_id
    except Exception as e:
        return False, f"Gagal menambah sparepart: {str(e)}", None


# ==============================================================================
# Dashboard
# ==============================================================================
def get_dashboard_stats() -> dict:
    """
    Ambil statistik untuk dashboard.
    
    Returns:
        Dict berisi ringkasan penjualan, servis aktif, stok rendah
    """
    today = db.get_sales_summary_today()
    month = db.get_sales_summary_month()
    active_repairs = db.get_active_repairs_count()
    low_stock = db.get_low_stock_products(threshold=5)

    return {
        "penjualan_hari_ini": today.get("total_penjualan", 0),
        "transaksi_hari_ini": today.get("jumlah_transaksi", 0),
        "penjualan_bulan_ini": month.get("total_penjualan", 0),
        "transaksi_bulan_ini": month.get("jumlah_transaksi", 0),
        "servis_aktif": active_repairs,
        "stok_rendah": len(low_stock),
        "produk_stok_rendah": low_stock,
    }
