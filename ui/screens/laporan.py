"""
Halaman Laporan - Toko Ayah
=============================
Modul pelaporan dan export data:
- Ringkasan Penjualan
- Ringkasan Servis
- Export ke Excel
"""

import flet as ft
from core.database import (
    get_all_sales, get_all_repair_orders, get_all_products
)
from core.utils import export_to_excel, format_rupiah
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, outline_button, show_error_snackbar, show_success_snackbar
)


def build_laporan_screen(page: ft.Page, user: dict) -> ft.Container:
    """Bangun halaman laporan."""
    
    # ============================================================
    # Handlers Export Excel
    # ============================================================
    def handle_export_penjualan(e):
        try:
            sales = get_all_sales()
            if not sales:
                show_error_snackbar(page, "Belum ada data penjualan.")
                return
            success, msg = export_to_excel(sales, "Laporan_Penjualan.xlsx", "Penjualan")
            if success:
                show_success_snackbar(page, msg)
            else:
                show_error_snackbar(page, msg)
        except Exception as e:
            show_error_snackbar(page, f"Error: {e}")

    def handle_export_servis(e):
        try:
            orders = get_all_repair_orders()
            if not orders:
                show_error_snackbar(page, "Belum ada data servis.")
                return
            success, msg = export_to_excel(orders, "Laporan_Servis.xlsx", "Servis")
            if success:
                show_success_snackbar(page, msg)
            else:
                show_error_snackbar(page, msg)
        except Exception as e:
            show_error_snackbar(page, f"Error: {e}")
            
    def handle_export_stok(e):
        try:
            products = get_all_products()
            if not products:
                show_error_snackbar(page, "Belum ada data produk.")
                return
            success, msg = export_to_excel(products, "Laporan_Stok_Barang.xlsx", "Stok")
            if success:
                show_success_snackbar(page, msg)
            else:
                show_error_snackbar(page, msg)
        except Exception as e:
            show_error_snackbar(page, f"Error: {e}")

    # ============================================================
    # UI Layout
    # ============================================================
    
    # 1. Panel Export Penjualan
    panel_penjualan = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.POINT_OF_SALE_ROUNDED, size=40, color=PRIMARY_BLUE),
                        ft.Text("Penjualan Barang", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=16
                ),
                ft.Text("Download semua rekap transaksi penjualan dari kasir ke dalam format Excel.", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Container(height=16),
                big_button("Export Penjualan", icon=ft.Icons.FILE_DOWNLOAD, on_click=handle_export_penjualan, width=300),
            ],
            spacing=8
        ),
        padding=ft.Padding.all(24),
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
    )
    
    # 2. Panel Export Servis
    panel_servis = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.BUILD_ROUNDED, size=40, color=PRIMARY_GREEN),
                        ft.Text("Order Servis", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=16
                ),
                ft.Text("Download semua data perbaikan perangkat beserta biaya dan status.", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Container(height=16),
                big_button("Export Servis", icon=ft.Icons.FILE_DOWNLOAD, on_click=handle_export_servis, width=300),
            ],
            spacing=8
        ),
        padding=ft.Padding.all(24),
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
    )
    
    # 3. Panel Export Stok
    panel_stok = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY_2_ROUNDED, size=40, color="#F9A825"),
                        ft.Text("Stok Produk & Sparepart", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=16
                ),
                ft.Text("Download laporan sisa stok barang dan sparepart yang ada di toko.", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Container(height=16),
                big_button("Export Stok", icon=ft.Icons.FILE_DOWNLOAD, on_click=handle_export_stok, width=300),
            ],
            spacing=8
        ),
        padding=ft.Padding.all(24),
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
    )

    content = ft.Column(
        controls=[
            section_header("Laporan & Export Data", ft.Icons.ASSESSMENT_ROUNDED),
            ft.Container(height=16),
            ft.Text(
                "Pilih laporan yang ingin didownload. File akan tersimpan di dalam folder 'data/export'.",
                size=FONT_BODY, color=TEXT_SECONDARY
            ),
            ft.Container(height=16),
            ft.Row(
                controls=[
                    ft.Column(controls=[panel_penjualan], expand=True),
                    ft.Column(controls=[panel_servis], expand=True),
                    ft.Column(controls=[panel_stok], expand=True),
                ],
                spacing=24,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        expand=True,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
