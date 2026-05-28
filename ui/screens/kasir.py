"""
Halaman Kasir (POS) - Toko Ayah
=================================
Modul penjualan lengkap:
- Search bar + barcode scanner (USB)
- Daftar produk (kiri)
- Keranjang belanja (kanan)
- Total + tombol Bayar (bawah)
"""

import flet as ft
from core.models import CartItem, MetodeBayar
from core.services import (
    search_product, process_sale, calculate_cart_total
)
from core.database import get_product_by_id, get_sale_by_id
from core.utils import format_rupiah, print_struk
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, LIGHT_GREEN, STATUS_RED, FONT_BODY, FONT_TITLE, FONT_LARGE, FONT_SMALL,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, empty_state,
    show_confirmation_dialog, show_error_snackbar, show_success_snackbar, icon_button_large, big_search_bar
)

def build_kasir_screen(page: ft.Page, user: dict) -> ft.Container:
    """Bangun halaman kasir (POS)."""
    
    # State
    cart_items: list[CartItem] = []
    current_products: list[dict] = []
    
    # Refs
    search_input = ft.Ref[ft.TextField]()
    products_grid = ft.Ref[ft.GridView]()
    cart_list = ft.Ref[ft.Column]()
    total_text = ft.Ref[ft.Text]()
    subtotal_text = ft.Ref[ft.Text]()
    payment_dropdown = ft.Ref[ft.Dropdown]()
    btn_bayar = ft.Ref[ft.ElevatedButton]()
    
    # ============================================================
    # Functions
    # ============================================================
    def load_products(keyword: str = ""):
        """Load produk dari database ke grid."""
        nonlocal current_products
        try:
            current_products = search_product(keyword)
            _render_products()
        except Exception as e:
            show_error_snackbar(page, f"Error: {e}")

    def on_search_change(e):
        """Pencarian biasa (ketik nama/kode)."""
        load_products(e.control.value)

    def on_search_submit(e):
        """
        Khusus untuk Barcode Scanner. 
        Scanner USB meniru keyboard dan menekan 'Enter' setelah scan.
        """
        keyword = e.control.value.strip()
        if not keyword:
            return
            
        hasil = search_product(keyword)
        # Jika hasil pasti 1 (berdasarkan barcode/kode unik), langsung masukkan ke keranjang
        if len(hasil) == 1:
            add_to_cart(hasil[0])
            search_input.current.value = ""
            load_products("")
        else:
            load_products(keyword)
            
        page.run_task(search_input.current.focus)
        page.update()

    def add_to_cart(product: dict):
        """Tambahkan produk ke keranjang atau tambah qty."""
        if product["stok"] <= 0:
            show_error_snackbar(page, f"Stok {product['nama']} habis!")
            return
            
        existing_item = next((item for item in cart_items if item.product_id == product["id"]), None)
        
        if existing_item:
            if existing_item.qty >= product["stok"]:
                show_error_snackbar(page, f"Stok maksimal ({product['stok']})!")
                return
            existing_item.qty += 1
        else:
            new_item = CartItem(
                product_id=product["id"],
                product_nama=product["nama"],
                product_kode=product["kode"],
                qty=1,
                harga_satuan=product["harga_jual"],
                diskon=0
            )
            cart_items.append(new_item)
            
        _update_cart_ui()

    def remove_from_cart(product_id: int):
        """Kurangi qty atau hapus dari keranjang."""
        existing_item = next((item for item in cart_items if item.product_id == product_id), None)
        if existing_item:
            existing_item.qty -= 1
            if existing_item.qty <= 0:
                cart_items.remove(existing_item)
        _update_cart_ui()
        
    def delete_from_cart(product_id: int):
        """Hapus item dari keranjang sepenuhnya."""
        item = next((i for i in cart_items if i.product_id == product_id), None)
        if item:
            cart_items.remove(item)
        _update_cart_ui()

    def _update_cart_ui():
        """Render ulang daftar keranjang dan hitung total."""
        cart_list.current.controls.clear()
        
        if not cart_items:
            cart_list.current.controls.append(
                ft.Container(
                    content=empty_state("Keranjang kosong\n\nSilakan cari atau scan produk", ft.Icons.SHOPPING_CART_OUTLINED),
                    padding=ft.Padding.all(40),
                )
            )
            btn_bayar.current.disabled = True
        else:
            btn_bayar.current.disabled = False
            for item in cart_items:
                cart_list.current.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                # Detail Produk
                                ft.Column(
                                    controls=[
                                        ft.Text(item.product_nama, size=FONT_BODY, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(f"{format_rupiah(item.harga_satuan)} / pcs", size=14, color=TEXT_SECONDARY),
                                    ],
                                    expand=True,
                                    spacing=2,
                                ),
                                # Kontrol Qty
                                ft.Row(
                                    controls=[
                                        icon_button_large(ft.Icons.REMOVE, on_click=lambda e, pid=item.product_id: remove_from_cart(pid), color=STATUS_RED, size=20),
                                        ft.Text(str(item.qty), size=FONT_BODY, weight=ft.FontWeight.BOLD),
                                        icon_button_large(ft.Icons.ADD, on_click=lambda e, pid=item.product_id: _add_by_id(pid), color=PRIMARY_GREEN, size=20),
                                    ],
                                    spacing=8,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                # Subtotal
                                ft.Container(
                                    content=ft.Text(format_rupiah(item.subtotal), size=FONT_BODY, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
                                    width=120,
                                    alignment=ft.Alignment.CENTER_RIGHT
                                ),
                                # Hapus Item
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINED,
                                    icon_color=STATUS_RED,
                                    icon_size=28,
                                    tooltip="Hapus Item",
                                    on_click=lambda e, pid=item.product_id: delete_from_cart(pid)
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.Padding.symmetric(vertical=12, horizontal=16),
                        border=ft.Border(bottom=ft.BorderSide(1, MEDIUM_GRAY))
                    )
                )
                
        # Update Total
        totals = calculate_cart_total(cart_items, ppn_rate=0.0) # PPN 0% untuk lansia
        subtotal_text.current.value = format_rupiah(totals["subtotal"])
        total_text.current.value = format_rupiah(totals["total"])
        
        if search_input.current:
            page.run_task(search_input.current.focus)
            
        page.update()
        
    def _add_by_id(product_id: int):
        product = get_product_by_id(product_id)
        if product:
            add_to_cart(product)

    def handle_checkout(e):
        """Proses pembayaran (Checkout)."""
        if not cart_items:
            show_error_snackbar(page, "Keranjang belanja masih kosong!")
            return
            
        def _confirm_checkout(e):
            metode = payment_dropdown.current.value
            success, msg, sale_id = process_sale(
                cart_items=cart_items,
                customer_id=None,
                user_id=user.get('id'),
                metode_bayar=metode
            )
            
            if success:
                sale_data = get_sale_by_id(sale_id)
                print_struk(sale_data) # Simpan struk otomatis
                show_success_snackbar(page, f"{msg}. Struk tersimpan di data/export/")
                cart_items.clear()
                _update_cart_ui()
                page.update()
                load_products()
            else:
                show_error_snackbar(page, msg)
                
        # Konfirmasi Transaksi
        totals = calculate_cart_total(cart_items)
        total_str = format_rupiah(totals["total"])
        show_confirmation_dialog(
            page=page,
            title="Selesaikan Transaksi?",
            message=f"Total belanja: {total_str}\nMetode: {payment_dropdown.current.value}\n\nApakah sudah menerima pembayaran?",
            on_confirm=_confirm_checkout,
            confirm_text="Sudah Diterima, Lanjutkan",
        )

    # ============================================================
    # Renders
    # ============================================================
    def _render_products():
        products_grid.current.controls.clear()
        
        if not current_products:
            products_grid.current.controls.append(
                ft.Container(
                    content=empty_state("Produk tidak ditemukan"),
                    padding=ft.Padding.all(40),
                    alignment=ft.Alignment.CENTER
                )
            )
        else:
            for p in current_products:
                stok_color = STATUS_RED if p['stok'] <= 5 else TEXT_SECONDARY
                products_grid.current.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(p['nama'], size=FONT_BODY, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(p.get('kode') or '-', size=14, color=TEXT_SECONDARY),
                                ft.Container(expand=True),
                                ft.Row(
                                    controls=[
                                        ft.Text(format_rupiah(p['harga_jual']), size=FONT_BODY, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
                                        ft.Text(f"Stok: {p['stok']}", size=14, color=stok_color, weight=ft.FontWeight.W_500),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                )
                            ]
                        ),
                        bgcolor=WHITE,
                        padding=ft.Padding.all(16),
                        border_radius=BORDER_RADIUS,
                        border=ft.Border.all(1, MEDIUM_GRAY),
                        on_click=lambda e, prod=p: add_to_cart(prod),
                        ink=True,
                        disabled=p['stok'] <= 0,
                        opacity=0.6 if p['stok'] <= 0 else 1.0
                    )
                )
        page.update()

    # ============================================================
    # UI Layout
    # ============================================================
    
    # 1. KIRI: Panel Produk & Pencarian (Scanner USB)
    left_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.QR_CODE_SCANNER, size=28, color=PRIMARY_BLUE),
                        ft.Text("Scan Barcode / Cari Manual", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=12
                ),
                ft.Container(height=8),
                big_search_bar(
                    placeholder="Contoh: Ketik 'Busi' atau Scan dengan Barcode Scanner...",
                    ref=search_input,
                    on_change=on_search_change,
                    on_submit=on_search_submit,
                    autofocus=True,
                ),
                ft.Container(height=12),
                ft.GridView(
                    ref=products_grid,
                    expand=True,
                    runs_count=3,
                    max_extent=260,
                    child_aspect_ratio=1.4,
                    spacing=16,
                    run_spacing=16,
                )
            ]
        ),
        expand=3,
        padding=ft.Padding.only(right=16)
    )
    
    # 2. KANAN: Panel Keranjang & Checkout
    right_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SHOPPING_CART_CHECKOUT, size=28, color=PRIMARY_GREEN),
                        ft.Text("Keranjang", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=12
                ),
                ft.Divider(color=MEDIUM_GRAY, thickness=2),
                
                # Daftar Barang di Keranjang (Scrollable)
                ft.Container(
                    content=ft.Column(
                        ref=cart_list,
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                    bgcolor=WHITE,
                    border_radius=BORDER_RADIUS,
                    border=ft.Border.all(1, MEDIUM_GRAY)
                ),
                
                ft.Container(height=16),
                
                # Panel Rekap (Total)
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text("Subtotal", size=FONT_BODY, color=TEXT_SECONDARY),
                                    ft.Text("Rp 0", ref=subtotal_text, size=FONT_BODY, weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Divider(color=MEDIUM_GRAY),
                            ft.Row(
                                controls=[
                                    ft.Text("TOTAL", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    ft.Text("Rp 0", ref=total_text, size=32, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                        ],
                        spacing=8
                    ),
                    padding=ft.Padding.all(20),
                    bgcolor=LIGHT_GREEN,
                    border_radius=BORDER_RADIUS,
                ),
                
                ft.Container(height=16),
                
                # Dropdown Metode Pembayaran
                ft.Text("Metode Pembayaran:", size=FONT_BODY, weight=ft.FontWeight.W_600),
                ft.Dropdown(
                    ref=payment_dropdown,
                    options=[
                        ft.dropdown.Option(m) for m in MetodeBayar.get_all()
                    ],
                    value=MetodeBayar.TUNAI.value,
                    text_size=FONT_BODY,
                    height=60,
                    content_padding=ft.Padding.symmetric(horizontal=16, vertical=16),
                    border_radius=BORDER_RADIUS,
                    border_color=MEDIUM_GRAY,
                    bgcolor=WHITE,
                ),
                
                ft.Container(height=16),
                
                # Tombol Besar BAYAR
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PAYMENTS_ROUNDED, color=WHITE, size=36),
                            ft.Text("BAYAR TRANSAKSI", size=24, weight=ft.FontWeight.BOLD, color=WHITE)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16
                    ),
                    ref=btn_bayar,
                    on_click=handle_checkout,
                    height=90,
                    disabled=True,
                    style=ft.ButtonStyle(
                        bgcolor={
                            ft.ControlState.DEFAULT: PRIMARY_GREEN,
                            ft.ControlState.DISABLED: ft.Colors.with_opacity(0.3, PRIMARY_GREEN)
                        },
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                    ),
                )
            ]
        ),
        expand=2,
        padding=ft.Padding.only(left=20),
        border=ft.Border(left=ft.BorderSide(1, MEDIUM_GRAY))
    )

    content = ft.Column(
        controls=[
            ft.Row(
                controls=[left_panel, right_panel],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        expand=True,
    )

    # Initial Load
    load_products()
    _update_cart_ui() 

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
