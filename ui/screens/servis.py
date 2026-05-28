"""
Halaman Servis (Perbaikan) - Toko Ayah
========================================
Modul servis lengkap:
- Daftar order servis dengan filter status
- Buat order servis baru
- Detail servis + update status workflow
- Tambah sparepart + hitung biaya

Catatan: Implementasi lengkap di Langkah 3
"""

import flet as ft
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, empty_state,
)


def build_servis_screen(page: ft.Page, user: dict) -> ft.Container:
    """
    Bangun halaman servis (perbaikan).
    Implementasi lengkap di Langkah 3.
    """

    content = ft.Column(
        controls=[
            section_header("Servis (Perbaikan)", ft.Icons.BUILD_ROUNDED),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=80, color=MEDIUM_GRAY),
                        ft.Container(height=12),
                        ft.Text(
                            "🚧 Halaman Servis",
                            size=FONT_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Fitur servis lengkap akan dibangun di Langkah 3.\n"
                            "Termasuk: daftar servis, buat order baru,\n"
                            "status workflow berwarna, dan manajemen sparepart.",
                            size=FONT_BODY,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=ft.Padding.all(40),
            ),
        ],
        expand=True,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
