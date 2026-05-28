"""
Halaman Dashboard - Toko Ayah
==============================
Halaman utama setelah login.
Menampilkan:
- 4 kartu statistik besar
- Tombol cepat: "Mulai Kasir" & "Buat Servis Baru"
- Daftar stok rendah (jika ada)
"""

import flet as ft
from core.services import get_dashboard_stats
from core.utils import format_rupiah
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, STATUS_YELLOW, STATUS_RED,
    FONT_BODY, FONT_TITLE, FONT_SUBTITLE, FONT_LARGE, FONT_SMALL,
    SPACING, PADDING, BORDER_RADIUS,
    stat_card, big_button, section_header, empty_state,
)


def build_dashboard_screen(page: ft.Page, on_navigate, user: dict) -> ft.Container:
    """
    Bangun halaman dashboard.
    
    Args:
        page: Flet page object
        on_navigate: Callback navigasi ke halaman lain
        user: Dict user yang sedang login
    """

    def refresh_data(e=None):
        """Refresh statistik dashboard."""
        try:
            stats = get_dashboard_stats()
            _update_stats(stats)
        except Exception as ex:
            print(f"Error refresh dashboard: {ex}")

    def _update_stats(stats: dict):
        """Update tampilan kartu statistik."""
        card_penjualan.content.controls[1].value = format_rupiah(
            stats.get("penjualan_hari_ini", 0)
        )
        card_penjualan.content.controls[2].value = (
            f"{stats.get('transaksi_hari_ini', 0)} transaksi"
        )

        card_servis.content.controls[1].value = str(
            stats.get("servis_aktif", 0)
        )

        card_stok.content.controls[1].value = str(
            stats.get("stok_rendah", 0)
        )
        # Warna merah jika ada stok rendah
        stok_count = stats.get("stok_rendah", 0)
        card_stok.content.controls[1].color = STATUS_RED if stok_count > 0 else TEXT_PRIMARY

        card_bulan.content.controls[1].value = format_rupiah(
            stats.get("penjualan_bulan_ini", 0)
        )
        card_bulan.content.controls[2].value = (
            f"{stats.get('transaksi_bulan_ini', 0)} transaksi"
        )

        # Update daftar stok rendah
        low_stock = stats.get("produk_stok_rendah", [])
        _update_low_stock_list(low_stock)

        page.update()

    def _update_low_stock_list(products: list):
        """Update daftar produk stok rendah."""
        low_stock_container.controls.clear()
        if not products:
            low_stock_container.controls.append(
                ft.Text(
                    "✅ Semua stok aman!",
                    size=FONT_BODY,
                    color=PRIMARY_GREEN,
                )
            )
        else:
            for p in products[:10]:  # Maksimal 10 item
                low_stock_container.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.WARNING_ROUNDED,
                                    color=STATUS_YELLOW,
                                    size=20,
                                ),
                                ft.Text(
                                    p.get("nama", "-"),
                                    size=FONT_BODY,
                                    color=TEXT_PRIMARY,
                                    expand=True,
                                ),
                                ft.Text(
                                    f"Sisa: {p.get('stok', 0)}",
                                    size=FONT_BODY,
                                    color=STATUS_RED,
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ],
                        ),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                        border_radius=8,
                        bgcolor=WHITE,
                        border=ft.Border.all(1, MEDIUM_GRAY),
                    )
                )

    # ============================================================
    # Kartu Statistik
    # ============================================================
    card_penjualan = stat_card(
        title="Penjualan Hari Ini",
        value="Rp 0",
        icon=ft.Icons.PAYMENTS_ROUNDED,
        color=PRIMARY_GREEN,
        subtitle="0 transaksi",
    )

    card_servis = stat_card(
        title="Servis Aktif",
        value="0",
        icon=ft.Icons.BUILD_ROUNDED,
        color=PRIMARY_BLUE,
        subtitle="sedang dikerjakan",
    )

    card_stok = stat_card(
        title="Stok Rendah",
        value="0",
        icon=ft.Icons.INVENTORY_ROUNDED,
        color=STATUS_YELLOW,
        subtitle="produk perlu restok",
    )

    card_bulan = stat_card(
        title="Total Bulan Ini",
        value="Rp 0",
        icon=ft.Icons.CALENDAR_MONTH_ROUNDED,
        color=PRIMARY_GREEN,
        subtitle="0 transaksi",
    )

    # Container stok rendah
    low_stock_container = ft.Column(spacing=8)

    # ============================================================
    # Layout Dashboard
    # ============================================================
    content = ft.Column(
        controls=[
            # Header
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                f"Selamat Datang, {user.get('username', 'Admin')}! 👋",
                                size=FONT_LARGE,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY,
                            ),
                            ft.Text(
                                "Berikut ringkasan toko hari ini",
                                size=FONT_BODY,
                                color=TEXT_SECONDARY,
                            ),
                        ],
                        spacing=4,
                    ),
                    ft.Container(expand=True),
                    big_button(
                        text="Refresh",
                        icon=ft.Icons.REFRESH_ROUNDED,
                        on_click=refresh_data,
                        color=PRIMARY_BLUE,
                        width=150,
                        height=50,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),

            ft.Container(height=12),

            # 4 Kartu Statistik
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=card_penjualan,
                        col={"sm": 12, "md": 6, "lg": 3},
                    ),
                    ft.Container(
                        content=card_servis,
                        col={"sm": 12, "md": 6, "lg": 3},
                    ),
                    ft.Container(
                        content=card_stok,
                        col={"sm": 12, "md": 6, "lg": 3},
                    ),
                    ft.Container(
                        content=card_bulan,
                        col={"sm": 12, "md": 6, "lg": 3},
                    ),
                ],
                spacing=SPACING,
                run_spacing=SPACING,
            ),

            ft.Container(height=20),

            # Tombol Cepat
            section_header("Aksi Cepat", ft.Icons.FLASH_ON_ROUNDED),
            ft.Container(height=8),
            ft.Row(
                controls=[
                    big_button(
                        text="Mulai Kasir",
                        icon=ft.Icons.POINT_OF_SALE_ROUNDED,
                        on_click=lambda e: on_navigate(1),  # Index kasir = 1
                        color=PRIMARY_GREEN,
                        width=280,
                        height=80,
                    ),
                    big_button(
                        text="Buat Servis Baru",
                        icon=ft.Icons.BUILD_ROUNDED,
                        on_click=lambda e: on_navigate(2),  # Index servis = 2
                        color=PRIMARY_BLUE,
                        width=280,
                        height=80,
                    ),
                ],
                spacing=SPACING,
                wrap=True,
            ),

            ft.Container(height=20),

            # Stok Rendah
            section_header("Peringatan Stok Rendah", ft.Icons.WARNING_ROUNDED),
            ft.Container(height=8),
            ft.Container(
                content=low_stock_container,
                padding=ft.Padding.all(16),
                border_radius=BORDER_RADIUS,
                bgcolor=LIGHT_GRAY,
                border=ft.Border.all(1, MEDIUM_GRAY),
            ),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
    )

    # Load data saat pertama kali
    refresh_data()

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
