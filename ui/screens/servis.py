"""
Halaman Servis (Perbaikan) - Toko Ayah
========================================
Modul manajemen servis:
- Daftar servis aktif dengan status warna-warni
- Form terima servis baru
- Detail servis (update status, tambah sparepart, hitung biaya)
"""

import flet as ft
from core.database import (
    get_all_repair_orders, get_repair_order_by_id, get_all_customers, get_all_spare_parts
)
from core.services import (
    create_service_order, advance_repair_status, add_part_to_repair, add_new_customer
)
from core.models import RepairStatus
from core.utils import format_rupiah, send_wa_notification
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GRAY, MEDIUM_GRAY, LIGHT_GREEN, STATUS_RED, FONT_BODY, FONT_TITLE, FONT_LARGE, FONT_SMALL,
    SPACING, PADDING, BORDER_RADIUS,
    section_header, empty_state, big_button, outline_button, big_text_field,
    show_confirmation_dialog, show_error_snackbar, show_success_snackbar, status_badge
)


def build_servis_screen(page: ft.Page, user: dict) -> ft.Container:
    """Bangun halaman manajemen servis."""
    
    # State
    orders: list[dict] = []
    selected_order_id: int | None = None
    selected_order_data: dict | None = None
    
    # Refs
    orders_list = ft.Ref[ft.Column]()
    detail_panel = ft.Ref[ft.Container]()
    
    # Refs untuk form order baru
    form_customer_dropdown = ft.Ref[ft.Dropdown]()
    form_new_customer_name = ft.Ref[ft.TextField]()
    form_merk = ft.Ref[ft.TextField]()
    form_tipe = ft.Ref[ft.TextField]()
    form_keluhan = ft.Ref[ft.TextField]()
    form_estimasi = ft.Ref[ft.TextField]()
    
    # Refs untuk form sparepart
    part_dropdown = ft.Ref[ft.Dropdown]()
    part_qty = ft.Ref[ft.TextField]()
    
    # ============================================================
    # Data Loaders
    # ============================================================
    def load_orders():
        nonlocal orders
        try:
            # Ambil semua order (yang aktif didahulukan)
            all_orders = get_all_repair_orders()
            # Sort: yang belum 'Selesai' atau 'Diambil' di atas
            orders = sorted(
                all_orders, 
                key=lambda x: 1 if x['status'] in ['Selesai', 'Diambil'] else 0
            )
            _render_orders_list()
        except Exception as e:
            show_error_snackbar(page, f"Gagal memuat data servis: {e}")

    def select_order(order_id: int):
        nonlocal selected_order_id, selected_order_data
        selected_order_id = order_id
        try:
            selected_order_data = get_repair_order_by_id(order_id)
            _render_detail_panel()
        except Exception as e:
            show_error_snackbar(page, f"Gagal memuat detail servis: {e}")
            
    # ============================================================
    # Handlers
    # ============================================================
    def open_new_order_dialog(e):
        """Buka modal form order servis baru."""
        # Ambil daftar pelanggan
        customers = get_all_customers()
        options = [ft.dropdown.Option(key=str(c['id']), text=f"{c['nama']} ({c.get('no_hp', '-')})") for c in customers]
        options.insert(0, ft.dropdown.Option(key="NEW", text="+ Pelanggan Baru (Ketik di bawah)"))
        
        def handle_submit(e):
            # Validasi form
            cust_id = form_customer_dropdown.current.value
            new_cust_name = form_new_customer_name.current.value
            
            if not cust_id:
                show_error_snackbar(page, "Pilih pelanggan!")
                return
                
            if cust_id == "NEW":
                if not new_cust_name:
                    show_error_snackbar(page, "Masukkan nama pelanggan baru!")
                    return
                # Buat pelanggan baru
                success, msg, real_cust_id = add_new_customer(nama=new_cust_name)
                if not success:
                    show_error_snackbar(page, msg)
                    return
                cust_id = str(real_cust_id)
                
            keluhan = form_keluhan.current.value
            estimasi = form_estimasi.current.value
            try:
                estimasi_float = float(estimasi) if estimasi else 0.0
            except ValueError:
                estimasi_float = 0.0
                
            success, msg, new_id = create_service_order(
                customer_id=int(cust_id),
                device_merk=form_merk.current.value,
                device_tipe=form_tipe.current.value,
                keluhan=keluhan,
                estimasi_biaya=estimasi_float,
                user_id=user.get('id')
            )
            
            if success:
                show_success_snackbar(page, msg)
                dialog.open = False
                page.update()
                load_orders()
                select_order(new_id)
            else:
                show_error_snackbar(page, msg)
                
        def on_dropdown_change(e):
            form_new_customer_name.current.visible = (form_customer_dropdown.current.value == "NEW")
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Terima Servis Baru", size=FONT_TITLE, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        ft.Text("Pelanggan", size=FONT_BODY, weight=ft.FontWeight.W_600),
                        ft.Dropdown(
                            ref=form_customer_dropdown,
                            options=options,
                            hint_text="Pilih Pelanggan",
                            on_select=on_dropdown_change,
                        ),
                        big_text_field(label="Nama Pelanggan Baru", ref=form_new_customer_name),
                        ft.Divider(),
                        ft.Text("Detail Perangkat", size=FONT_BODY, weight=ft.FontWeight.W_600),
                        big_text_field(label="Merk Perangkat (misal: Samsung)", ref=form_merk),
                        big_text_field(label="Tipe/Model", ref=form_tipe),
                        big_text_field(label="Keluhan / Kerusakan", ref=form_keluhan, multiline=True, min_lines=2),
                        big_text_field(label="Estimasi Biaya (Rp)", ref=form_estimasi, keyboard_type=ft.KeyboardType.NUMBER),
                    ],
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                )
            ),
            actions=[
                outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                big_button("Simpan Order", on_click=handle_submit),
            ],
            actions_padding=ft.Padding.all(20),
        )
        
        page.overlay.append(dialog)
        form_new_customer_name.current.visible = False
        dialog.open = True
        page.update()

    def handle_advance_status(e):
        """Majukan status servis."""
        if not selected_order_id:
            return
            
        def _confirm(e):
            success, msg = advance_repair_status(selected_order_id)
            if success:
                show_success_snackbar(page, msg)
                load_orders()
                select_order(selected_order_id)
            else:
                show_error_snackbar(page, msg)
                
        next_status = RepairStatus.get_next_status(selected_order_data['status'])
        if next_status:
            show_confirmation_dialog(
                page=page,
                title="Update Status Servis",
                message=f"Ubah status menjadi '{next_status}'?",
                on_confirm=_confirm
            )

    def open_add_part_dialog(e):
        """Buka modal untuk tambah sparepart."""
        if not selected_order_id:
            return
            
        parts = get_all_spare_parts()
        options = [ft.dropdown.Option(key=str(p['id']), text=f"{p['nama']} (Stok: {p['stok']} | Rp{p['harga']})") for p in parts]
        
        def handle_submit(e):
            part_id = part_dropdown.current.value
            qty_str = part_qty.current.value
            
            if not part_id:
                show_error_snackbar(page, "Pilih sparepart!")
                return
            try:
                qty = int(qty_str) if qty_str else 1
            except ValueError:
                qty = 1
                
            success, msg = add_part_to_repair(
                repair_order_id=selected_order_id,
                spare_part_id=int(part_id),
                qty=qty
            )
            
            if success:
                show_success_snackbar(page, msg)
                dialog.open = False
                page.update()
                select_order(selected_order_id) # reload detail
            else:
                show_error_snackbar(page, msg)
                
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Tambah Sparepart", size=FONT_TITLE, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=400,
                content=ft.Column(
                    controls=[
                        ft.Dropdown(
                            ref=part_dropdown,
                            options=options,
                            hint_text="Pilih Sparepart",
                        ),
                        big_text_field(label="Jumlah (Qty)", ref=part_qty, value="1", keyboard_type=ft.KeyboardType.NUMBER),
                    ],
                    spacing=16,
                )
            ),
            actions=[
                outline_button("Batal", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
                big_button("Tambahkan", on_click=handle_submit),
            ],
            actions_padding=ft.Padding.all(20),
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ============================================================
    # Renders
    # ============================================================
    def _render_orders_list():
        orders_list.current.controls.clear()
        
        if not orders:
            orders_list.current.controls.append(
                ft.Container(
                    content=empty_state("Belum ada data servis"),
                    padding=ft.Padding.all(40),
                )
            )
        else:
            for order in orders:
                is_selected = order['id'] == selected_order_id
                
                # Card for list
                card = ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(f"#{order['id']}", size=FONT_BODY, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
                                    status_badge(order['status'])
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            ),
                            ft.Text(order.get('customer_nama', 'Unknown'), size=FONT_TITLE, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                            ft.Text(f"{order.get('device_merk', '-')} {order.get('device_tipe', '')}", size=FONT_BODY, color=TEXT_SECONDARY),
                        ],
                        spacing=4
                    ),
                    padding=ft.Padding.all(16),
                    bgcolor=LIGHT_GREEN if is_selected else WHITE,
                    border_radius=BORDER_RADIUS,
                    border=ft.Border.all(2, PRIMARY_GREEN if is_selected else MEDIUM_GRAY),
                    on_click=lambda e, oid=order['id']: select_order(oid),
                    ink=True,
                )
                orders_list.current.controls.append(card)
        page.update()

    def _render_detail_panel():
        if not selected_order_data:
            detail_panel.current.content = ft.Container(
                content=empty_state("Pilih order servis untuk melihat detail", ft.Icons.BUILD_OUTLINED),
                padding=ft.Padding.all(40)
            )
            page.update()
            return
            
        data = selected_order_data
        items = data.get('items', [])
        
        # Buat list items
        items_controls = []
        if not items:
            items_controls.append(ft.Text("Belum ada sparepart yang digunakan.", size=FONT_BODY, color=TEXT_SECONDARY))
        else:
            for item in items:
                items_controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"{item.get('spare_part_nama', 'Item')} (x{item['qty']})", size=FONT_BODY, color=TEXT_PRIMARY),
                            ft.Text(format_rupiah(item['harga_satuan'] * item['qty']), size=FONT_BODY, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
        
        next_status = RepairStatus.get_next_status(data['status'])
        btn_update = big_button(
            text=f"Update ke: {next_status}" if next_status else "Servis Selesai",
            on_click=handle_advance_status,
            disabled=not bool(next_status),
            expand=True
        )
        
        def _handle_wa(e):
            hp = data.get('customer_hp')
            if not hp or hp == '-':
                show_error_snackbar(page, "Nomor HP pelanggan tidak tersedia!")
                return
            msg = f"Halo {data.get('customer_nama')}, servis perangkat {data.get('device_merk')} Anda (Keluhan: {data.get('keluhan')}) telah SELESAI. Total biaya: {format_rupiah(data.get('total_biaya', 0))}. Silakan diambil di Toko Ayah."
            show_success_snackbar(page, "Membuka WhatsApp, mohon tunggu beberapa detik...")
            page.update()
            import threading
            def send():
                success, response = send_wa_notification(hp, msg)
            threading.Thread(target=send, daemon=True).start()

        wa_button = outline_button(
            text="Kirim Notifikasi WA",
            icon=ft.Icons.CHAT_ROUNDED,
            on_click=_handle_wa,
            disabled=(data['status'] != 'Selesai')
        )
                
        detail_panel.current.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(f"Detail Servis #{data['id']}", size=FONT_LARGE, weight=ft.FontWeight.BOLD, color=PRIMARY_BLUE),
                        status_badge(data['status'])
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(color=MEDIUM_GRAY),
                
                # Info Pelanggan & Perangkat
                ft.Text("Pelanggan & Perangkat", size=FONT_TITLE, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ft.Text(f"Nama: {data.get('customer_nama', '-')}", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Text(f"No. HP: {data.get('customer_hp', '-')}", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Text(f"Perangkat: {data.get('device_merk', '-')} {data.get('device_tipe', '')}", size=FONT_BODY, color=TEXT_SECONDARY),
                ft.Container(height=8),
                
                # Keluhan
                ft.Text("Keluhan", size=FONT_TITLE, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ft.Container(
                    content=ft.Text(data.get('keluhan', '-'), size=FONT_BODY, color=TEXT_PRIMARY),
                    bgcolor=LIGHT_GRAY,
                    padding=ft.Padding.all(12),
                    border_radius=8,
                    width=float('inf')
                ),
                ft.Container(height=8),
                
                # Sparepart / Biaya
                ft.Row(
                    controls=[
                        ft.Text("Penggunaan Sparepart", size=FONT_TITLE, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                        icon_button_large(ft.Icons.ADD, on_click=open_add_part_dialog, tooltip="Tambah Sparepart")
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(
                    content=ft.Column(controls=items_controls, spacing=8),
                    padding=ft.Padding.all(16),
                    border=ft.Border.all(1, MEDIUM_GRAY),
                    border_radius=8,
                ),
                
                # Total Biaya
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Text("TOTAL BIAYA", size=FONT_TITLE, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(format_rupiah(data.get('total_biaya', 0)), size=FONT_LARGE, weight=ft.FontWeight.BOLD, color=PRIMARY_GREEN),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                
                ft.Container(expand=True), # Spacer
                
                # Aksi Status & WA
                ft.Row(
                    controls=[btn_update, wa_button],
                )
            ],
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            padding=ft.Padding.all(24)
        )
        page.update()

    # ============================================================
    # UI Layout
    # ============================================================
    
    # KIRI: List Servis
    left_panel = ft.Container(
        content=ft.Column(
            controls=[
                big_button(
                    text="Terima Servis Baru",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=open_new_order_dialog,
                    expand=False,
                    width=400
                ),
                ft.Container(height=16),
                ft.Text("Daftar Servis", size=FONT_TITLE, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                ft.Container(
                    content=ft.Column(
                        ref=orders_list,
                        spacing=12,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                    expand=True,
                )
            ]
        ),
        expand=2,
        padding=ft.Padding.only(right=16)
    )
    
    # KANAN: Detail Servis
    right_panel = ft.Container(
        ref=detail_panel,
        expand=3,
        bgcolor=WHITE,
        border_radius=BORDER_RADIUS,
        border=ft.Border.all(1, MEDIUM_GRAY),
        padding=ft.Padding.all(0) # Padding ditangani di dalam content
    )
    
    content = ft.Column(
        controls=[
            section_header("Manajemen Servis & Perbaikan", ft.Icons.BUILD_ROUNDED),
            ft.Container(height=16),
            ft.Row(
                controls=[left_panel, right_panel],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START
            )
        ],
        expand=True,
    )
    
    # Initial load
    load_orders()
    _render_detail_panel() # Init empty state

    return ft.Container(
        content=content,
        expand=True,
        padding=ft.Padding.all(PADDING + 8),
    )
