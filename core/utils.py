"""
Utils Module - Toko Ayah
========================
Fungsi-fungsi utilitas yang digunakan di seluruh aplikasi.

Isi:
- Format rupiah
- Backup otomatis
- Export Excel (placeholder, diimplementasikan di Langkah 4)
- Kirim WA (placeholder, diimplementasikan di Langkah 4)
"""

import os
import shutil
from datetime import datetime
from typing import Optional


# ==============================================================================
# Path Constants
# ==============================================================================
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
BACKUP_DIR: str = os.path.join(DATA_DIR, "backup")
EXPORT_DIR: str = os.path.join(DATA_DIR, "export")


# ==============================================================================
# Format Helpers
# ==============================================================================
def format_rupiah(amount: float) -> str:
    """
    Format angka menjadi format Rupiah Indonesia.
    Contoh: 1500000 → "Rp 1.500.000"
    """
    if amount is None:
        return "Rp 0"
    try:
        # Format dengan separator titik (Indonesia)
        formatted = f"{abs(amount):,.0f}".replace(",", ".")
        prefix = "-" if amount < 0 else ""
        return f"{prefix}Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"


def format_tanggal(date_str: Optional[str], format_output: str = "%d/%m/%Y") -> str:
    """
    Format tanggal dari format database ke format Indonesia.
    Contoh: "2026-05-28" → "28/05/2026"
    """
    if not date_str:
        return "-"
    try:
        # Coba berbagai format input
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
            try:
                dt = datetime.strptime(str(date_str), fmt)
                return dt.strftime(format_output)
            except ValueError:
                continue
        return str(date_str)
    except Exception:
        return str(date_str)


def format_datetime(date_str: Optional[str]) -> str:
    """Format tanggal + waktu. Contoh: '28/05/2026 14:30'."""
    return format_tanggal(date_str, "%d/%m/%Y %H:%M")


# ==============================================================================
# Backup
# ==============================================================================
def create_backup() -> tuple[bool, str]:
    """
    Buat backup database ke folder backup.
    Format nama: toko_backup_YYYYMMDD_HHMMSS.db
    
    Returns:
        (success, message_or_path)
    """
    try:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        db_path = os.path.join(DATA_DIR, "toko.db")
        if not os.path.exists(db_path):
            return False, "File database tidak ditemukan!"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"toko_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(db_path, backup_path)
        
        # Hapus backup lama (simpan 30 terakhir)
        _cleanup_old_backups(keep=30)
        
        return True, f"Backup berhasil: {backup_filename}"
    
    except Exception as e:
        return False, f"Gagal membuat backup: {str(e)}"


def _cleanup_old_backups(keep: int = 30) -> None:
    """Hapus file backup lama, simpan hanya sejumlah 'keep' terbaru."""
    if not os.path.exists(BACKUP_DIR):
        return
    
    backups = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("toko_backup_")],
        reverse=True
    )
    
    for old_backup in backups[keep:]:
        try:
            os.remove(os.path.join(BACKUP_DIR, old_backup))
        except OSError:
            pass


def get_backup_list() -> list[dict]:
    """Ambil daftar file backup yang ada."""
    if not os.path.exists(BACKUP_DIR):
        return []
    
    backups = []
    for f in sorted(os.listdir(BACKUP_DIR), reverse=True):
        if f.startswith("toko_backup_"):
            filepath = os.path.join(BACKUP_DIR, f)
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            backups.append({
                "filename": f,
                "path": filepath,
                "size_mb": round(size_mb, 2),
                "created": os.path.getmtime(filepath)
            })
    return backups


def restore_backup(backup_path: str) -> tuple[bool, str]:
    """
    Restore database dari file backup.
    
    Returns:
        (success, message)
    """
    try:
        if not os.path.exists(backup_path):
            return False, "File backup tidak ditemukan!"
        
        db_path = os.path.join(DATA_DIR, "toko.db")
        
        # Backup current sebelum restore
        create_backup()
        
        shutil.copy2(backup_path, db_path)
        return True, "Database berhasil di-restore!"
    
    except Exception as e:
        return False, f"Gagal restore: {str(e)}"


# ==============================================================================
# Export Excel (Placeholder - implementasi di Langkah 4)
# ==============================================================================
def export_to_excel(data: list[dict], filename: str, sheet_name: str = "Data") -> tuple[bool, str]:
    """
    Export data ke file Excel.
    Implementasi lengkap di Langkah 4 menggunakan pandas + openpyxl.
    """
    try:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        filepath = os.path.join(EXPORT_DIR, filename)
        
        # Placeholder - akan diimplementasikan penuh di Langkah 4
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_excel(filepath, sheet_name=sheet_name, index=False)
        
        return True, f"Data berhasil di-export: {filename}"
    except ImportError:
        return False, "Library pandas belum terinstall. Jalankan: pip install pandas openpyxl"
    except Exception as e:
        return False, f"Gagal export: {str(e)}"


# ==============================================================================
# WhatsApp Notification (Placeholder - implementasi di Langkah 4)
# ==============================================================================
def send_wa_notification(phone: str, message: str) -> tuple[bool, str]:
    """
    Kirim notifikasi WhatsApp ke pelanggan.
    Implementasi lengkap di Langkah 4 menggunakan pywhatkit.
    """
    try:
        # Placeholder - implementasi lengkap di Langkah 4
        # import pywhatkit
        # pywhatkit.sendwhatmsg_instantly(phone, message)
        return True, f"Pesan akan dikirim ke {phone}"
    except Exception as e:
        return False, f"Gagal kirim WA: {str(e)}"
