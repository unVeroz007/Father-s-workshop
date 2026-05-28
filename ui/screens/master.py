"""
Halaman Data Master - Toko Ayah
=================================
Modul CRUD untuk:
- Produk
- Sparepart
- Pelanggan
"""

import flet as ft
from core.database import (
    get_all_products, add_product, update_product, delete_product,
    get_all_spare_parts, add_spare_part, update_spare_part, delete_spare_part,
    get_all_customers, add_customer, update_customer, delete_customer
)
from core.utils import format_rupiah
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, STATUS_RED, FONT_BODY, FONT_TITLE, FONT_LARGE,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, big_button, outline_button, big_text_field,
    show_confirmation_dialog, show_error_snackbar, show_success_snackbar, empty_state
)


def build_master_screen(page: ft.Page, user: dict) -> ft.Container:
    
    # ============================================================
    # VIEW: PRODUK
    # ============================================================
    def _build_produk_tab():
        products = []
        product_list = ft.Ref[ft.Column]()
        search_input = ft.Ref[ft.TextField]()
        
        form_nama = ft.Ref[ft.TextField]()
        form_kode = ft.Ref[ft.TextField]()
        form_harga_beli = ft.Ref[ft.TextField]()
        form_harga_jual = ft.Ref[ft.TextField]()
        form_stok = ft.Ref[ft.TextField]()
        
        def load_data(keyword=""):
            nonlocal products
            try:
                products = get_all_products(keyword)
                product_list.current.controls.clear()
                if not products:
                    product_list.current.controls.append(ft.Container(content=empty_state("Tidak ada produk"), padding=20))
                else:
                    for p in products:
                        product_list.current.controls.append(
                            ft.Container(
                                content=ft.Row([
                                    ft.Text(p['kode'] or "-", expand=1, size=FONT_BODY),
                                    ft.Text(p['nama'], expand=3, size=FONT_BODY, weight=ft.FontWeight.BOLD),
                                    ft.Text(format_rupiah(p['harga_jual']), expand=2, size=FONT_BODY, color=PRIMARY_BLUE),
                                    ft.Text(str(p['stok']), expand=1, size=FONT_BODY, color=STATUS_RED if p['stok']<=0 else PRIMARY_GREEN),
                                    ft.Row([
                                        ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=PRIMARY_BLUE, on_click=lambda e, prod=p: open_form(prod)),
                                        ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=STATUS_RED, on_click=lambda e, prod=p: handle_delete(prod)),
                                    ], expand=1, alignment=ft.MainAxisAlignment.END)
                                ]),
                                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                                border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                            )
                        )
                page.update()
            except Exception as e:
                show_error_snackbar(page, str(e))

        def open_form(product=None):
            is_edit = product is not None
            def submit(e):
                nama = form_nama.current.value
                kode = form_kode.current.value
                if not nama or not form_harga_jual.current.value:
                    show_error_snackbar(page, "Nama dan Harga Jual wajib!")
                    return
                try:
                    hb = float(form_harga_beli.current.value) if form_harga_beli.current.value else 0.0
                    hj = float(form_harga_jual.current.value)
                    st = int(form_stok.current.value) if form_stok.current.value else 0
                except ValueError:
                    show_error_snackbar(page, "Input angka tidak valid!")
                    return
                
                if is_edit:
                    success, msg = update_product(product['id'], nama=nama, kode=kode, harga_beli=hb, harga_jual=hj, stok=st)
                else:
                    success, msg, _ = add_product(nama=nama, kode=kode, harga_beli=hb, harga_jual=hj, stok=st)
                
                if success:
                    show_success_snackbar(page, msg)
                    dialog.open = False
                    load_data(search_input.current.value)
                else:
                    show_error_snackbar(page, msg)

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Edit Produk" if is_edit else "Tambah Produk", size=FONT_TITLE, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=400,
                    content=ft.Column([
                        ft.Text("Gunakan Scanner pada Barcode", color=TEXT_SECONDARY),
                        big_text_field("Kode/Barcode", ref=form_kode, value=product['kode'] if is_edit else ""),
                        big_text_field("Nama", ref=form_nama, value=product['nama'] if is_edit else ""),
                        big_text_field("Harga Beli", ref=form_harga_beli, value=str(product['harga_beli']) if is_edit else "", keyboard_type=ft.KeyboardType.NUMBER),
                        big_text_field("Harga Jual", ref=form_harga_jual, value=str(product['harga_jual']) if is_edit else "", keyboard_type=ft.KeyboardType.NUMBER),
                        big_text_field("Stok", ref=form_stok, value=str(product['stok']) if is_edit else "0", keyboard_type=ft.KeyboardType.NUMBER),
                    ], spacing=12, scroll=ft.ScrollMode.AUTO)
                ),
                actions=[
                    outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                    big_button("Simpan", on_click=submit),
                ],
                actions_padding=20
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def handle_delete(p):
            def _confirm(e):
                success, msg = delete_product(p['id'])
                if success:
                    show_success_snackbar(page, msg)
                    load_data(search_input.current.value)
            show_confirmation_dialog(page, "Hapus?", f"Hapus {p['nama']}?", _confirm, confirm_color=STATUS_RED)

        layout = ft.Column([
            ft.Row([
                ft.TextField(ref=search_input, hint_text="Cari / Scan Barcode Produk", expand=True, on_change=lambda e: load_data(e.control.value)),
                big_button("Tambah Produk", icon=ft.Icons.ADD, on_click=lambda e: open_form())
            ]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(ref=product_list, spacing=0, scroll=ft.ScrollMode.AUTO),
                expand=True, bgcolor=WHITE, border=ft.Border.all(1, MEDIUM_GRAY), border_radius=8
            )
        ], expand=True, padding=16)
        
        load_data()
        return layout

    # ============================================================
    # VIEW: SPAREPART
    # ============================================================
    def _build_sparepart_tab():
        parts = []
        part_list = ft.Ref[ft.Column]()
        search_input = ft.Ref[ft.TextField]()
        
        form_nama = ft.Ref[ft.TextField]()
        form_harga = ft.Ref[ft.TextField]()
        form_stok = ft.Ref[ft.TextField]()
        
        def load_data(keyword=""):
            nonlocal parts
            parts = get_all_spare_parts(keyword)
            part_list.current.controls.clear()
            for p in parts:
                part_list.current.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(p['nama'], expand=3, size=FONT_BODY, weight=ft.FontWeight.BOLD),
                            ft.Text(format_rupiah(p['harga']), expand=2, size=FONT_BODY, color=PRIMARY_BLUE),
                            ft.Text(str(p['stok']), expand=1, size=FONT_BODY, color=STATUS_RED if p['stok']<=0 else PRIMARY_GREEN),
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=PRIMARY_BLUE, on_click=lambda e, part=p: open_form(part)),
                                ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=STATUS_RED, on_click=lambda e, part=p: handle_delete(part)),
                            ], expand=1, alignment=ft.MainAxisAlignment.END)
                        ]),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                    )
                )
            page.update()

        def open_form(part=None):
            is_edit = part is not None
            def submit(e):
                try:
                    hj = float(form_harga.current.value)
                    st = int(form_stok.current.value)
                except:
                    show_error_snackbar(page, "Angka tidak valid")
                    return
                if is_edit:
                    success, msg = update_spare_part(part['id'], nama=form_nama.current.value, harga=hj, stok=st)
                else:
                    success, msg, _ = add_spare_part(nama=form_nama.current.value, harga=hj, stok=st)
                if success:
                    dialog.open = False
                    load_data(search_input.current.value)
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Sparepart", size=FONT_TITLE, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=400,
                    content=ft.Column([
                        big_text_field("Nama Sparepart", ref=form_nama, value=part['nama'] if is_edit else ""),
                        big_text_field("Harga", ref=form_harga, value=str(part['harga']) if is_edit else "", keyboard_type=ft.KeyboardType.NUMBER),
                        big_text_field("Stok", ref=form_stok, value=str(part['stok']) if is_edit else "0", keyboard_type=ft.KeyboardType.NUMBER),
                    ], spacing=12)
                ),
                actions=[
                    outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                    big_button("Simpan", on_click=submit),
                ], actions_padding=20
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def handle_delete(p):
            def _c(e):
                delete_spare_part(p['id'])
                load_data(search_input.current.value)
            show_confirmation_dialog(page, "Hapus?", f"Hapus {p['nama']}?", _c, confirm_color=STATUS_RED)

        layout = ft.Column([
            ft.Row([
                ft.TextField(ref=search_input, hint_text="Cari Sparepart...", expand=True, on_change=lambda e: load_data(e.control.value)),
                big_button("Tambah Sparepart", icon=ft.Icons.ADD, on_click=lambda e: open_form())
            ]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(ref=part_list, spacing=0, scroll=ft.ScrollMode.AUTO),
                expand=True, bgcolor=WHITE, border=ft.Border.all(1, MEDIUM_GRAY), border_radius=8
            )
        ], expand=True, padding=16)
        load_data()
        return layout

    # ============================================================
    # VIEW: PELANGGAN
    # ============================================================
    def _build_pelanggan_tab():
        custs = []
        cust_list = ft.Ref[ft.Column]()
        search_input = ft.Ref[ft.TextField]()
        
        form_nama = ft.Ref[ft.TextField]()
        form_hp = ft.Ref[ft.TextField]()
        form_alamat = ft.Ref[ft.TextField]()
        
        def load_data(keyword=""):
            nonlocal custs
            custs = get_all_customers(keyword)
            cust_list.current.controls.clear()
            for p in custs:
                cust_list.current.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(p['nama'], expand=2, size=FONT_BODY, weight=ft.FontWeight.BOLD),
                            ft.Text(p['no_hp'] or "-", expand=1, size=FONT_BODY),
                            ft.Text(p['alamat'] or "-", expand=2, size=FONT_BODY),
                            ft.Row([
                                ft.IconButton(ft.Icons.EDIT_ROUNDED, icon_color=PRIMARY_BLUE, on_click=lambda e, cust=p: open_form(cust)),
                                ft.IconButton(ft.Icons.DELETE_ROUNDED, icon_color=STATUS_RED, on_click=lambda e, cust=p: handle_delete(cust)),
                            ], expand=1, alignment=ft.MainAxisAlignment.END)
                        ]),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                    )
                )
            page.update()

        def open_form(cust=None):
            is_edit = cust is not None
            def submit(e):
                if is_edit:
                    success, msg = update_customer(cust['id'], nama=form_nama.current.value, no_hp=form_hp.current.value, alamat=form_alamat.current.value)
                else:
                    success, msg, _ = add_customer(nama=form_nama.current.value, no_hp=form_hp.current.value, alamat=form_alamat.current.value)
                if success:
                    dialog.open = False
                    load_data(search_input.current.value)
            
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Pelanggan", size=FONT_TITLE, weight=ft.FontWeight.BOLD),
                content=ft.Container(
                    width=400,
                    content=ft.Column([
                        big_text_field("Nama", ref=form_nama, value=cust['nama'] if is_edit else ""),
                        big_text_field("No HP", ref=form_hp, value=cust['no_hp'] if is_edit else ""),
                        big_text_field("Alamat", ref=form_alamat, value=cust['alamat'] if is_edit else "", multiline=True),
                    ], spacing=12)
                ),
                actions=[
                    outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                    big_button("Simpan", on_click=submit),
                ], actions_padding=20
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        def handle_delete(p):
            def _c(e):
                delete_customer(p['id'])
                load_data(search_input.current.value)
            show_confirmation_dialog(page, "Hapus?", f"Hapus {p['nama']}?", _c, confirm_color=STATUS_RED)

        layout = ft.Column([
            ft.Row([
                ft.TextField(ref=search_input, hint_text="Cari Pelanggan...", expand=True, on_change=lambda e: load_data(e.control.value)),
                big_button("Tambah Pelanggan", icon=ft.Icons.ADD, on_click=lambda e: open_form())
            ]),
            ft.Container(height=8),
            ft.Container(
                content=ft.Column(ref=cust_list, spacing=0, scroll=ft.ScrollMode.AUTO),
                expand=True, bgcolor=WHITE, border=ft.Border.all(1, MEDIUM_GRAY), border_radius=8
            )
        ], expand=True, padding=16)
        load_data()
        return layout

    # ============================================================
    # TABS LAYOUT
    # ============================================================
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Data Produk",
                icon=ft.Icons.INVENTORY_ROUNDED,
                content=_build_produk_tab()
            ),
            ft.Tab(
                text="Data Sparepart",
                icon=ft.Icons.HANDYMAN_ROUNDED,
                content=_build_sparepart_tab()
            ),
            ft.Tab(
                text="Data Pelanggan",
                icon=ft.Icons.PEOPLE_ROUNDED,
                content=_build_pelanggan_tab()
            ),
        ],
        expand=1,
    )

    content = ft.Column(
        controls=[
            section_header("Data Master", ft.Icons.FOLDER_SPECIAL_ROUNDED),
            ft.Container(height=8),
            tabs
        ],
        expand=True,
    )

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
