"""
Halaman Kasir (POS) - Toko Ayah
=================================
Modul penjualan lengkap:
- Search bar + barcode scanner (USB)
- Daftar produk (kiri)
- Keranjang belanja (kanan)
- Total + tombol Bayar (bawah)

Catatan: Implementasi lengkap di Langkah 2
"""

import flet as ft
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, big_search_bar, empty_state,
)


def build_kasir_screen(page: ft.Page, user: dict) -> ft.Container:
    """
    Bangun halaman kasir (POS).
    Implementasi lengkap di Langkah 2.
    """

    content = ft.Column(
        controls=[
            section_header("Kasir (Penjualan)", ft.Icons.POINT_OF_SALE_ROUNDED),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION_ROUNDED, size=80, color=MEDIUM_GRAY),
                        ft.Container(height=12),
                        ft.Text(
                            "🚧 Halaman Kasir",
                            size=FONT_TITLE,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            "Fitur kasir lengkap akan dibangun di Langkah 2.\n"
                            "Termasuk: pencarian produk, barcode scanner,\n"
                            "keranjang belanja, dan pembayaran.",
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
