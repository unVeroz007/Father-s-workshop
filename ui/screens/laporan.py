"""
Halaman Laporan - Toko Ayah
=============================
Menampilkan laporan:
- Penjualan harian/bulanan
- Servis
- Stok
- Export ke Excel

Catatan: Implementasi lengkap di Langkah 5
"""

import flet as ft
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, empty_state,
)


def build_laporan_screen(page: ft.Page, user: dict) -> ft.Container:
    """
    Bangun halaman laporan.
    Implementasi lengkap di Langkah 5.
    """

    content = ft.Column(
        controls=[
            section_header("Laporan", ft.Icons.ASSESSMENT_ROUNDED),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=80, color=MEDIUM_GRAY),
                        ft.Container(height=12),
                        ft.Text(
                            "🚧 Halaman Laporan",
                            size=FONT_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Fitur laporan akan dibangun di Langkah 5.\n"
                            "Termasuk: laporan penjualan, servis,\n"
                            "stok, dan export ke Excel.",
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
