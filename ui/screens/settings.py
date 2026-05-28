"""
Halaman Pengaturan - Toko Ayah
================================
Pengaturan:
- Informasi toko (nama, alamat, kontak)
- Backup database
- Ubah password

Catatan: Implementasi lengkap di Langkah 5
"""

import flet as ft
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, empty_state,
)


def build_settings_screen(page: ft.Page, user: dict) -> ft.Container:
    """
    Bangun halaman pengaturan.
    Implementasi lengkap di Langkah 5.
    """

    content = ft.Column(
        controls=[
            section_header("Pengaturan", ft.Icons.SETTINGS_ROUNDED),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=80, color=MEDIUM_GRAY),
                        ft.Container(height=12),
                        ft.Text(
                            "🚧 Halaman Pengaturan",
                            size=FONT_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Fitur pengaturan akan dibangun di Langkah 5.\n"
                            "Termasuk: info toko, backup database,\n"
                            "dan ubah password.",
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
