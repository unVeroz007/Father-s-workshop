"""
Halaman Data Produk (Master Data) - Toko Ayah
===============================================
Modul CRUD untuk produk:
- Daftar Produk
- Tambah Produk Baru (dengan fitur Scan Barcode)
- Edit & Hapus Produk
"""

import flet as ft
from core.database import (
    get_all_products, add_product, update_product, delete_product
)
from core.utils import format_rupiah
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, STATUS_RED, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, outline_button, big_text_field,
    show_confirmation_dialog, show_error_snackbar, show_success_snackbar, empty_state
)


def build_produk_screen(page: ft.Page, user: dict) -> ft.Container:
    """Bangun halaman manajemen data produk."""
    
    # State
    products: list[dict] = []
    
    # Refs
    product_list = ft.Ref[ft.Column]()
    search_input = ft.Ref[ft.TextField]()
    
    # Form Refs
    form_nama = ft.Ref[ft.TextField]()
    form_kode = ft.Ref[ft.TextField]()
    form_harga_beli = ft.Ref[ft.TextField]()
    form_harga_jual = ft.Ref[ft.TextField]()
    form_stok = ft.Ref[ft.TextField]()
    
    def load_data(keyword: str = ""):
        nonlocal products
        try:
            products = get_all_products(keyword)
            _render_list()
        except Exception as e:
            show_error_snackbar(page, f"Gagal memuat produk: {e}")

    def on_search(e):
        load_data(search_input.current.value)

    # ============================================================
    # Handlers (Tambah / Edit / Hapus)
    # ============================================================
    def open_form_dialog(product: dict = None):
        """Buka modal form untuk tambah/edit."""
        is_edit = product is not None
        title_text = "Edit Produk" if is_edit else "Tambah Produk Baru"
        
        def handle_submit(e):
            nama = form_nama.current.value
            kode = form_kode.current.value
            
            if not nama or not form_harga_jual.current.value:
                show_error_snackbar(page, "Nama dan Harga Jual wajib diisi!")
                return
                
            try:
                hb = float(form_harga_beli.current.value) if form_harga_beli.current.value else 0.0
                hj = float(form_harga_jual.current.value)
                st = int(form_stok.current.value) if form_stok.current.value else 0
            except ValueError:
                show_error_snackbar(page, "Harga dan Stok harus berupa angka valid!")
                return
                
            if is_edit:
                success, msg = update_product(
                    product_id=product['id'],
                    nama=nama, kode=kode, harga_beli=hb, harga_jual=hj, stok=st
                )
            else:
                success, msg, new_id = add_product(
                    nama=nama, kode=kode, harga_beli=hb, harga_jual=hj, stok=st
                )
                
            if success:
                show_success_snackbar(page, msg)
                dialog.open = False
                page.update()
                load_data(search_input.current.value)
            else:
                show_error_snackbar(page, msg)

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, size=FONT_TITLE, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        ft.Text("Arahkan kursor ke Kode/Barcode lalu gunakan Scanner", size=14, color=TEXT_SECONDARY),
                        big_text_field("Kode / Barcode (Opsional)", ref=form_kode, value=product['kode'] if is_edit else ""),
                        big_text_field("Nama Produk", ref=form_nama, value=product['nama'] if is_edit else ""),
                        ft.Row(
                            controls=[
                                big_text_field("Harga Beli (Modal)", ref=form_harga_beli, value=str(product['harga_beli']) if is_edit else "", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
                                big_text_field("Harga Jual", ref=form_harga_jual, value=str(product['harga_jual']) if is_edit else "", keyboard_type=ft.KeyboardType.NUMBER, expand=True),
                            ],
                            spacing=12
                        ),
                        big_text_field("Stok Awal", ref=form_stok, value=str(product['stok']) if is_edit else "0", keyboard_type=ft.KeyboardType.NUMBER),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                )
            ),
            actions=[
                outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                big_button("Simpan", on_click=handle_submit),
            ],
            actions_padding=ft.Padding.all(20),
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def handle_delete(product: dict):
        def _confirm(e):
            success, msg = delete_product(product['id'])
            if success:
                show_success_snackbar(page, msg)
                load_data(search_input.current.value)
            else:
                show_error_snackbar(page, msg)
                
        show_confirmation_dialog(
            page,
            title="Hapus Produk?",
            message=f"Anda yakin ingin menghapus '{product['nama']}'?",
            on_confirm=_confirm,
            confirm_text="Hapus",
            confirm_color=STATUS_RED
        )

    # ============================================================
    # Renders
    # ============================================================
    def _render_list():
        product_list.current.controls.clear()
        if not products:
            product_list.current.controls.append(
                ft.Container(
                    content=empty_state("Tidak ada produk ditemukan"),
                    padding=ft.Padding.all(40),
                )
            )
        else:
            # Header tabel sederhana
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Kode", size=FONT_BODY, weight=ft.FontWeight.BOLD, expand=1),
                        ft.Text("Nama Produk", size=FONT_BODY, weight=ft.FontWeight.BOLD, expand=3),
                        ft.Text("Harga", size=FONT_BODY, weight=ft.FontWeight.BOLD, expand=2),
                        ft.Text("Stok", size=FONT_BODY, weight=ft.FontWeight.BOLD, expand=1),
                        ft.Text("Aksi", size=FONT_BODY, weight=ft.FontWeight.BOLD, expand=1, text_align=ft.TextAlign.RIGHT),
                    ],
                ),
                padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                bgcolor=LIGHT_GRAY,
                border_radius=BORDER_RADIUS
            )
            product_list.current.controls.append(header)
            
            for p in products:
                row = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(p['kode'] or "-", size=FONT_BODY, color=TEXT_SECONDARY, expand=1),
                            ft.Text(p['nama'], size=FONT_BODY, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY, expand=3),
                            ft.Text(format_rupiah(p['harga_jual']), size=FONT_BODY, color=PRIMARY_BLUE, expand=2),
                            ft.Text(str(p['stok']), size=FONT_BODY, weight=ft.FontWeight.BOLD, color=STATUS_RED if p['stok'] <= 0 else PRIMARY_GREEN, expand=1),
                            ft.Row(
                                controls=[
                                    ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=PRIMARY_BLUE, on_click=lambda e, prod=p: open_form_dialog(prod), tooltip="Edit"),
                                    ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=STATUS_RED, on_click=lambda e, prod=p: handle_delete(prod), tooltip="Hapus"),
                                ],
                                expand=1,
                                alignment=ft.MainAxisAlignment.END
                            )
                        ],
                    ),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                )
                product_list.current.controls.append(row)
                
        page.update()

    # ============================================================
    # UI Layout
    # ============================================================
    content = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    section_header("Data Produk (Master)", ft.Icons.INVENTORY_ROUNDED),
                    big_button("Tambah Produk", icon=ft.Icons.ADD_ROUNDED, on_click=lambda e: open_form_dialog())
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Container(height=16),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SEARCH_ROUNDED, color=TEXT_SECONDARY),
                    ft.TextField(
                        ref=search_input,
                        hint_text="Cari berdasarkan nama atau scan barcode...",
                        on_change=on_search,
                        expand=True,
                        border_color=MEDIUM_GRAY,
                        focused_border_color=PRIMARY_BLUE,
                        text_size=FONT_BODY
                    )
                ]
            ),
            ft.Container(height=16),
            ft.Container(
                content=ft.Column(
                    ref=product_list,
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
        expand=True,
    )
    
    load_data()

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
