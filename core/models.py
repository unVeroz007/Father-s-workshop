"""
Models Module - Toko Ayah
=========================
Dataclass untuk setiap entitas di database.
Digunakan untuk type safety dan kemudahan transfer data antar layer.

Catatan:
- Semua model menggunakan dataclass untuk kesederhanaan
- Optional fields menggunakan default None
- Status servis menggunakan Enum untuk kejelasan
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


# ==============================================================================
# Enums
# ==============================================================================
class RepairStatus(Enum):
    """Status workflow order servis."""
    DITERIMA = "Diterima"
    DIAGNOSA = "Diagnosa"
    MENUNGGU_SPAREPART = "Menunggu Sparepart"
    PERBAIKAN = "Perbaikan"
    SELESAI = "Selesai"
    DIAMBIL = "Diambil"

    @classmethod
    def get_color(cls, status: str) -> str:
        """Kembalikan warna untuk setiap status (sesuai UI Guidelines)."""
        color_map = {
            "Diterima": "#1565C0",              # Biru
            "Diagnosa": "#F9A825",              # Kuning
            "Menunggu Sparepart": "#F9A825",    # Kuning
            "Perbaikan": "#E65100",             # Oranye
            "Selesai": "#2E7D32",               # Hijau
            "Diambil": "#C62828",               # Merah
        }
        return color_map.get(status, "#757575")  # Abu-abu sebagai default

    @classmethod
    def get_next_status(cls, current: str) -> Optional[str]:
        """Kembalikan status berikutnya dalam workflow."""
        order = [s.value for s in cls]
        try:
            idx = order.index(current)
            return order[idx + 1] if idx + 1 < len(order) else None
        except ValueError:
            return None

    @classmethod
    def get_all_statuses(cls) -> list[str]:
        """Kembalikan semua status dalam urutan workflow."""
        return [s.value for s in cls]


class MetodeBayar(Enum):
    """Metode pembayaran yang tersedia."""
    TUNAI = "Tunai"
    TRANSFER = "Transfer"
    QRIS = "QRIS"

    @classmethod
    def get_all(cls) -> list[str]:
        return [m.value for m in cls]


class StockMovementType(Enum):
    """Tipe pergerakan stok."""
    MASUK = "masuk"
    KELUAR = "keluar"
    OPNAME = "opname"


# ==============================================================================
# Dataclasses
# ==============================================================================
@dataclass
class User:
    """Model pengguna aplikasi."""
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    role: str = "admin"
    created_at: Optional[str] = None


@dataclass
class Product:
    """Model produk yang dijual."""
    id: Optional[int] = None
    kode: str = ""
    nama: str = ""
    kategori: str = ""
    merk: str = ""
    tipe: str = ""
    harga_beli: float = 0
    harga_jual: float = 0
    stok: int = 0
    serial: str = ""
    created_at: Optional[str] = None


@dataclass
class SparePart:
    """Model sparepart untuk servis."""
    id: Optional[int] = None
    nama: str = ""
    kompatibel: str = ""
    harga: float = 0
    stok: int = 0
    created_at: Optional[str] = None


@dataclass
class Customer:
    """Model pelanggan."""
    id: Optional[int] = None
    nama: str = ""
    no_hp: str = ""
    alamat: str = ""
    catatan: str = ""
    created_at: Optional[str] = None


@dataclass
class CartItem:
    """Item di keranjang belanja (kasir) - hanya di memori, tidak disimpan."""
    product_id: int = 0
    product_nama: str = ""
    product_kode: str = ""
    qty: int = 1
    harga_satuan: float = 0
    diskon: float = 0

    @property
    def subtotal(self) -> float:
        """Hitung subtotal item."""
        return (self.harga_satuan * self.qty) - self.diskon


@dataclass
class Sale:
    """Model transaksi penjualan."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    user_id: Optional[int] = None
    total: float = 0
    metode_bayar: str = "Tunai"
    created_at: Optional[str] = None
    # Relasi (diisi saat query JOIN)
    customer_nama: str = ""
    items: list = field(default_factory=list)


@dataclass
class SaleItem:
    """Model detail item penjualan."""
    id: Optional[int] = None
    sale_id: int = 0
    product_id: int = 0
    qty: int = 0
    harga_satuan: float = 0
    diskon: float = 0
    subtotal: float = 0
    # Relasi
    product_nama: str = ""
    product_kode: str = ""


@dataclass
class RepairOrder:
    """Model order servis / perbaikan."""
    id: Optional[int] = None
    customer_id: int = 0
    user_id: Optional[int] = None
    device_merk: str = ""
    device_tipe: str = ""
    device_serial: str = ""
    keluhan: str = ""
    status: str = "Diterima"
    estimasi_biaya: float = 0
    total_biaya: float = 0
    tanggal_masuk: Optional[str] = None
    tanggal_selesai: Optional[str] = None
    created_at: Optional[str] = None
    # Relasi
    customer_nama: str = ""
    customer_hp: str = ""
    customer_alamat: str = ""
    items: list = field(default_factory=list)


@dataclass
class RepairOrderItem:
    """Model item sparepart yang digunakan di servis."""
    id: Optional[int] = None
    repair_order_id: int = 0
    spare_part_id: Optional[int] = None
    qty: int = 1
    harga_satuan: float = 0
    keterangan: str = ""
    # Relasi
    spare_part_nama: str = ""


@dataclass
class Settings:
    """Model pengaturan toko."""
    id: int = 1
    nama_toko: str = "Toko Ayah"
    alamat: str = ""
    no_hp: str = ""
    logo_path: str = ""
    ppn_rate: float = 0.11
