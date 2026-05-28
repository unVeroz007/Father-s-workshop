"""
Halaman Pengaturan & Backup - Toko Ayah
=========================================
Modul pengaturan aplikasi:
- Nama Toko & Alamat
- Pengaturan Database (Backup & Restore)
"""

import flet as ft
from core.database import get_settings, update_settings
from core.utils import create_backup, get_backup_list, restore_backup
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, STATUS_RED, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, outline_button, big_text_field, show_error_snackbar, show_success_snackbar, show_confirmation_dialog
)
import os


def build_settings_screen(page: ft.Page, user: dict) -> ft.Container:
    """Bangun halaman pengaturan."""
    
    # State
    settings_data = get_settings()
    backups = []
    
    # Refs
    form_nama = ft.Ref[ft.TextField]()
    form_alamat = ft.Ref[ft.TextField]()
    form_hp = ft.Ref[ft.TextField]()
    backup_list = ft.Ref[ft.Column]()
    
    # ============================================================
    # Handlers Profil Toko
    # ============================================================
    def handle_save_settings(e):
        try:
            success, msg = update_settings(
                nama_toko=form_nama.current.value,
                alamat=form_alamat.current.value,
                no_hp=form_hp.current.value
            )
            if success:
                show_success_snackbar(page, msg)
                # Update top navbar title if necessary
                # Ini bisa dilakukan dengan trigger event, tapi untuk kesederhanaan
                # kita hanya update settings database.
            else:
                show_error_snackbar(page, msg)
        except Exception as e:
            show_error_snackbar(page, f"Error: {e}")
            
    # ============================================================
    # Handlers Backup & Restore
    # ============================================================
    def load_backups():
        nonlocal backups
        backups = get_backup_list()
        _render_backups()
        
    def handle_create_backup(e):
        success, msg = create_backup()
        if success:
            show_success_snackbar(page, msg)
            load_backups()
        else:
            show_error_snackbar(page, msg)
            
    def handle_restore(filepath: str):
        def _confirm(e):
            success, msg = restore_backup(filepath)
            if success:
                show_success_snackbar(page, msg + " Silakan restart aplikasi!")
                page.update()
            else:
                show_error_snackbar(page, msg)
                
        show_confirmation_dialog(
            page,
            "Restore Database?",
            "PERINGATAN: Data saat ini akan ditimpa dengan data dari backup. Apakah Anda yakin?",
            _confirm,
            confirm_text="Ya, Restore Sekarang"
        )

    # ============================================================
    # Renders
    # ============================================================
    def _render_backups():
        backup_list.current.controls.clear()
        if not backups:
            backup_list.current.controls.append(
                ft.Text("Belum ada file backup.", size=FONT_BODY, color=TEXT_SECONDARY)
            )
        else:
            for b in backups[:10]: # Tampilkan 10 terbaru
                import datetime
                dt_str = datetime.datetime.fromtimestamp(b['created']).strftime('%d/%m/%Y %H:%M')
                
                row = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(b['filename'], size=FONT_BODY, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
                                    ft.Text(f"{dt_str} • {b['size_mb']} MB", size=14, color=TEXT_SECONDARY)
                                ],
                                expand=True,
                                spacing=2
                            ),
                            outline_button("Restore", icon=ft.Icons.RESTORE_ROUNDED, on_click=lambda e, path=b['path']: handle_restore(path))
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=ft.Padding.all(12),
                    border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                )
                backup_list.current.controls.append(row)
        page.update()

    # ============================================================
    # UI Layout
    # ============================================================
    
    # 1. Panel Profil Toko
    panel_profil = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.STOREFRONT_ROUNDED, size=32, color=PRIMARY_GREEN),
                        ft.Text("Profil Toko", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=12
                ),
                ft.Divider(color=MEDIUM_GRAY),
                ft.Container(height=8),
                big_text_field("Nama Toko", ref=form_nama, value=settings_data.get('nama_toko', '')),
                big_text_field("Nomor Handphone (Toko)", ref=form_hp, value=settings_data.get('no_hp', '')),
                big_text_field("Alamat Lengkap", ref=form_alamat, value=settings_data.get('alamat', ''), multiline=True, min_lines=3),
                ft.Container(height=16),
                big_button("Simpan Profil", icon=ft.Icons.SAVE_ROUNDED, on_click=handle_save_settings)
            ],
            spacing=12
        ),
        padding=ft.Padding.all(24),
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
        expand=1
    )
    
    # 2. Panel Backup / Restore
    panel_backup = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SECURITY_ROUNDED, size=32, color=PRIMARY_BLUE),
                        ft.Text("Keamanan Data (Backup)", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=12
                ),
                ft.Divider(color=MEDIUM_GRAY),
                ft.Container(height=8),
                ft.Text(
                    "Sangat disarankan untuk melakukan backup data minimal seminggu sekali untuk mencegah kehilangan data.",
                    size=FONT_BODY, color=TEXT_SECONDARY
                ),
                ft.Container(height=16),
                big_button("Buat Backup Sekarang", icon=ft.Icons.BACKUP_ROUNDED, on_click=handle_create_backup),
                
                ft.Container(height=24),
                ft.Text("Riwayat Backup Terakhir", size=FONT_BODY, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column(
                        ref=backup_list,
                        spacing=8,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    bgcolor=WHITE,
                    border=ft.Border.all(1, MEDIUM_GRAY),
                    border_radius=8,
                    padding=ft.Padding.all(8)
                )
            ],
            spacing=12,
            expand=True
        ),
        padding=ft.Padding.all(24),
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
        expand=1
    )

    content = ft.Column(
        controls=[
            section_header("Pengaturan Sistem", ft.Icons.SETTINGS_ROUNDED),
            ft.Container(height=16),
            ft.Row(
                controls=[panel_profil, panel_backup],
                expand=True,
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        expand=True,
    )
    
    # Initial load
    load_backups()

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
