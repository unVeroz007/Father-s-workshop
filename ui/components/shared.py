"""
UI Components - Toko Ayah
==========================
Komponen UI yang bisa digunakan ulang di seluruh aplikasi.
Semua komponen sudah disesuaikan untuk pengguna lansia:
- Tombol besar (min 70px tinggi)
- Font besar (min 18px)
- Warna yang tenang dan kontras tinggi
- Spacing yang lapang
"""

import flet as ft
from typing import Optional, Callable


# ==============================================================================
# Konstanta Warna (sesuai UI Guidelines)
# ==============================================================================
PRIMARY_GREEN = "#2E7D32"       # Hijau utama
PRIMARY_BLUE = "#1565C0"        # Biru utama
LIGHT_GREEN = "#E8F5E9"        # Hijau muda (background)
LIGHT_BLUE = "#E3F2FD"         # Biru muda (background)
WHITE = "#FFFFFF"
LIGHT_GRAY = "#F5F5F5"         # Abu muda
MEDIUM_GRAY = "#E0E0E0"        # Abu sedang
DARK_GRAY = "#424242"          # Abu gelap (teks)
TEXT_PRIMARY = "#212121"        # Teks utama
TEXT_SECONDARY = "#757575"      # Teks sekunder

# Warna status servis
STATUS_BLUE = "#1565C0"         # Diterima
STATUS_YELLOW = "#F9A825"       # Diagnosa / Menunggu Sparepart
STATUS_ORANGE = "#E65100"       # Perbaikan
STATUS_GREEN = "#2E7D32"        # Selesai
STATUS_RED = "#C62828"          # Diambil

# Warna sidebar
SIDEBAR_BG = "#1B5E20"         # Hijau gelap
SIDEBAR_ACTIVE = "#2E7D32"     # Hijau aktif
SIDEBAR_HOVER = "#388E3C"      # Hijau hover
SIDEBAR_TEXT = "#FFFFFF"        # Putih


# ==============================================================================
# Ukuran (sesuai UI Guidelines)
# ==============================================================================
FONT_BODY = 18
FONT_TITLE = 24
FONT_SUBTITLE = 20
FONT_SMALL = 16
FONT_LARGE = 28
BUTTON_HEIGHT = 70
BUTTON_MIN_WIDTH = 200
ROW_HEIGHT = 50
SPACING = 20
PADDING = 20
BORDER_RADIUS = 12


# ==============================================================================
# Tombol Besar (Reusable)
# ==============================================================================
def big_button(
    text: str,
    on_click: Optional[Callable] = None,
    icon: Optional[str] = None,
    color: str = PRIMARY_GREEN,
    text_color: str = WHITE,
    width: Optional[int] = None,
    height: int = BUTTON_HEIGHT,
    expand: bool = False,
    disabled: bool = False,
    tooltip: str = "",
) -> ft.ElevatedButton:
    """
    Tombol besar yang mudah ditekan untuk pengguna lansia.
    Minimal 70px tinggi sesuai UI Guidelines.
    """
    return ft.ElevatedButton(
        text,
        icon=icon,
        on_click=on_click,
        width=width or BUTTON_MIN_WIDTH,
        height=height,
        expand=expand,
        disabled=disabled,
        tooltip=tooltip,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.with_opacity(0.15, color) if disabled else color,
            color=text_color,
            text_style=ft.TextStyle(size=FONT_BODY, weight=ft.FontWeight.W_600),
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            elevation=2,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        ),
    )


def outline_button(
    text: str,
    on_click: Optional[Callable] = None,
    icon: Optional[str] = None,
    color: str = DARK_GRAY,
    width: Optional[int] = None,
    height: int = BUTTON_HEIGHT,
    expand: bool = False,
) -> ft.OutlinedButton:
    """Tombol outline (untuk aksi sekunder seperti Batal)."""
    return ft.OutlinedButton(
        text,
        icon=icon,
        on_click=on_click,
        width=width or BUTTON_MIN_WIDTH,
        height=height,
        expand=expand,
        style=ft.ButtonStyle(
            color=color,
            text_style=ft.TextStyle(size=FONT_BODY, weight=ft.FontWeight.W_500),
            shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
            side=ft.BorderSide(width=2, color=MEDIUM_GRAY),
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
        ),
    )


def icon_button_large(
    icon: str,
    on_click: Optional[Callable] = None,
    tooltip: str = "",
    color: str = PRIMARY_GREEN,
    size: int = 32,
) -> ft.IconButton:
    """Tombol ikon yang besar dan mudah ditekan."""
    return ft.IconButton(
        icon=icon,
        on_click=on_click,
        tooltip=tooltip,
        icon_color=color,
        icon_size=size,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.all(12),
        ),
    )


# ==============================================================================
# Dialog Konfirmasi
# ==============================================================================
def show_confirmation_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm: Callable,
    confirm_text: str = "Ya, Lanjutkan",
    cancel_text: str = "Batal",
    confirm_color: str = PRIMARY_GREEN,
) -> None:
    """
    Tampilkan dialog konfirmasi sebelum aksi penting.
    Sesuai UI Guidelines: "Yakin?" sebelum setiap aksi penting.
    """
    def close_dialog(e):
        dialog.open = False
        page.update()

    def confirm_action(e):
        dialog.open = False
        page.update()
        on_confirm(e)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(
            title,
            size=FONT_TITLE,
            weight=ft.FontWeight.BOLD,
            color=TEXT_PRIMARY,
        ),
        content=ft.Text(
            message,
            size=FONT_BODY,
            color=DARK_GRAY,
        ),
        actions=[
            outline_button(
                text=cancel_text,
                on_click=close_dialog,
                width=180,
                height=55,
            ),
            big_button(
                text=confirm_text,
                on_click=confirm_action,
                color=confirm_color,
                width=200,
                height=55,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=16),
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()


def show_success_snackbar(page: ft.Page, message: str) -> None:
    """Tampilkan pesan sukses (snackbar hijau)."""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, size=FONT_BODY, color=WHITE),
        bgcolor=PRIMARY_GREEN,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


def show_error_snackbar(page: ft.Page, message: str) -> None:
    """Tampilkan pesan error (snackbar merah)."""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, size=FONT_BODY, color=WHITE),
        bgcolor=STATUS_RED,
        duration=4000,
    )
    page.snack_bar.open = True
    page.update()


def show_info_snackbar(page: ft.Page, message: str) -> None:
    """Tampilkan pesan info (snackbar biru)."""
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message, size=FONT_BODY, color=WHITE),
        bgcolor=PRIMARY_BLUE,
        duration=3000,
    )
    page.snack_bar.open = True
    page.update()


# ==============================================================================
# Search Bar Besar
# ==============================================================================
def big_search_bar(
    placeholder: str = "Ketik untuk mencari...",
    on_change: Optional[Callable] = None,
    on_submit: Optional[Callable] = None,
    width: Optional[int] = None,
    autofocus: bool = False,
    ref: Optional[ft.Ref] = None,
) -> ft.TextField:
    """
    Search bar yang besar dan jelas untuk pengguna lansia.
    """
    return ft.TextField(
        hint_text=placeholder,
        on_change=on_change,
        on_submit=on_submit,
        width=width,
        height=60,
        ref=ref,
        autofocus=autofocus,
        text_size=FONT_BODY,
        hint_style=ft.TextStyle(size=FONT_SMALL, color=TEXT_SECONDARY),
        prefix_icon=ft.Icons.SEARCH,
        border_radius=BORDER_RADIUS,
        border_color=MEDIUM_GRAY,
        focused_border_color=PRIMARY_BLUE,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=16),
    )


# ==============================================================================
# Input Field Besar
# ==============================================================================
def big_text_field(
    label: str,
    value: str = "",
    hint_text: str = "",
    on_change: Optional[Callable] = None,
    width: Optional[int] = None,
    multiline: bool = False,
    min_lines: int = 1,
    max_lines: int = 1,
    keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT,
    read_only: bool = False,
    expand: bool = False,
    ref: Optional[ft.Ref] = None,
    password: bool = False,
    prefix_icon: Optional[str] = None,
) -> ft.TextField:
    """Input field yang besar dan jelas."""
    return ft.TextField(
        label=label,
        value=value,
        hint_text=hint_text,
        on_change=on_change,
        width=width,
        ref=ref,
        expand=expand,
        text_size=FONT_BODY,
        label_style=ft.TextStyle(size=FONT_SMALL, color=TEXT_SECONDARY),
        hint_style=ft.TextStyle(size=FONT_SMALL, color=TEXT_SECONDARY),
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines if not multiline else 5,
        keyboard_type=keyboard_type,
        read_only=read_only,
        password=password,
        can_reveal_password=password,
        prefix_icon=prefix_icon,
        border_radius=BORDER_RADIUS,
        border_color=MEDIUM_GRAY,
        focused_border_color=PRIMARY_BLUE,
        content_padding=ft.Padding.symmetric(horizontal=20, vertical=16),
    )


# ==============================================================================
# Kartu Statistik (untuk Dashboard)
# ==============================================================================
def stat_card(
    title: str,
    value: str,
    icon: str,
    color: str = PRIMARY_GREEN,
    subtitle: str = "",
    width: int = 250,
) -> ft.Container:
    """
    Kartu statistik besar untuk dashboard.
    Menampilkan satu angka penting dengan ikon dan judul.
    """
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(icon, color=color, size=36),
                        ft.Text(
                            title,
                            size=FONT_SMALL,
                            color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    value,
                    size=FONT_LARGE,
                    weight=ft.FontWeight.BOLD,
                    color=TEXT_PRIMARY,
                ),
                ft.Text(
                    subtitle,
                    size=14,
                    color=TEXT_SECONDARY,
                    visible=bool(subtitle),
                ),
            ],
            spacing=8,
        ),
        width=width,
        padding=ft.Padding.all(PADDING),
        border_radius=BORDER_RADIUS,
        bgcolor=WHITE,
        border=ft.Border.all(1, MEDIUM_GRAY),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )


# ==============================================================================
# Status Badge (untuk Servis)
# ==============================================================================
def status_badge(status: str) -> ft.Container:
    """Badge warna-warni untuk status servis."""
    from core.models import RepairStatus
    color = RepairStatus.get_color(status)

    return ft.Container(
        content=ft.Text(
            status,
            size=14,
            weight=ft.FontWeight.W_600,
            color=WHITE,
        ),
        bgcolor=color,
        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
        border_radius=20,
    )


# ==============================================================================
# Section Header
# ==============================================================================
def section_header(title: str, icon: Optional[str] = None) -> ft.Row:
    """Header untuk setiap bagian/section dalam halaman."""
    controls = []
    if icon:
        controls.append(ft.Icon(icon, color=PRIMARY_GREEN, size=28))
    controls.append(
        ft.Text(
            title,
            size=FONT_TITLE,
            weight=ft.FontWeight.BOLD,
            color=TEXT_PRIMARY,
        )
    )
    return ft.Row(controls=controls, spacing=12)


# ==============================================================================
# Empty State
# ==============================================================================
def empty_state(
    message: str = "Belum ada data",
    icon: str = ft.Icons.INBOX_OUTLINED,
) -> ft.Container:
    """Tampilan saat data kosong."""
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(icon, size=64, color=MEDIUM_GRAY),
                ft.Text(
                    message,
                    size=FONT_BODY,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment.CENTER,
        padding=ft.Padding.all(40),
    )


# ==============================================================================
# Sidebar Navigation
# ==============================================================================
def create_sidebar(
    page: ft.Page,
    active_index: int,
    on_navigate: Callable,
) -> ft.Container:
    """
    Sidebar navigasi kiri dengan 5 menu utama.
    Sesuai UI Guidelines: icon besar + teks jelas.
    """
    menu_items = [
        {"icon": ft.Icons.DASHBOARD_ROUNDED, "label": "Dashboard", "index": 0},
        {"icon": ft.Icons.POINT_OF_SALE_ROUNDED, "label": "Kasir", "index": 1},
        {"icon": ft.Icons.BUILD_ROUNDED, "label": "Servis", "index": 2},
        {"icon": ft.Icons.ASSESSMENT_ROUNDED, "label": "Laporan", "index": 3},
        {"icon": ft.Icons.INVENTORY_ROUNDED, "label": "Data Produk", "index": 4},
        {"icon": ft.Icons.SETTINGS_ROUNDED, "label": "Pengaturan", "index": 5},
    ]

    def create_menu_item(item: dict) -> ft.Container:
        is_active = item["index"] == active_index
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        item["icon"],
                        color=WHITE,
                        size=28,
                    ),
                    ft.Text(
                        item["label"],
                        size=FONT_BODY,
                        color=WHITE,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400,
                    ),
                ],
                spacing=16,
            ),
            padding=ft.Padding.symmetric(horizontal=20, vertical=16),
            border_radius=BORDER_RADIUS,
            bgcolor=SIDEBAR_ACTIVE if is_active else ft.Colors.TRANSPARENT,
            on_click=lambda e, idx=item["index"]: on_navigate(idx),
            on_hover=lambda e: _on_menu_hover(e, is_active),
            ink=True,
        )

    return ft.Container(
        content=ft.Column(
            controls=[
                # Header toko
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.STOREFRONT_ROUNDED, color=WHITE, size=40),
                            ft.Text(
                                "Toko Ayah",
                                size=FONT_TITLE,
                                weight=ft.FontWeight.BOLD,
                                color=WHITE,
                            ),
                            ft.Text(
                                "Elektronik & Servis",
                                size=14,
                                color=ft.Colors.with_opacity(0.7, WHITE),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=ft.Padding.symmetric(vertical=24, horizontal=16),
                ),
                ft.Divider(color=ft.Colors.with_opacity(0.2, WHITE), height=1),
                ft.Container(height=12),
                # Menu items
                *[create_menu_item(item) for item in menu_items],
                # Spacer
                ft.Container(expand=True),
                # Logout button at bottom
                ft.Divider(color=ft.Colors.with_opacity(0.2, WHITE), height=1),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=WHITE, size=24),
                            ft.Text(
                                "Keluar",
                                size=FONT_BODY,
                                color=WHITE,
                            ),
                        ],
                        spacing=16,
                    ),
                    padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                    border_radius=BORDER_RADIUS,
                    on_click=lambda e: _handle_logout(page, on_navigate),
                    ink=True,
                ),
                ft.Container(height=8),
            ],
            spacing=4,
        ),
        width=240,
        bgcolor=SIDEBAR_BG,
        border_radius=ft.BorderRadius.only(
            top_right=BORDER_RADIUS,
            bottom_right=BORDER_RADIUS,
        ),
        padding=ft.Padding.symmetric(horizontal=8, vertical=8),
    )


def _on_menu_hover(e: ft.ControlEvent, is_active: bool) -> None:
    """Handle hover effect pada menu sidebar."""
    if not is_active:
        e.control.bgcolor = SIDEBAR_HOVER if e.data == "true" else ft.Colors.TRANSPARENT
        e.control.update()


def _handle_logout(page: ft.Page, on_navigate: Callable) -> None:
    """Handle logout dengan konfirmasi."""
    show_confirmation_dialog(
        page=page,
        title="Keluar dari Aplikasi",
        message="Yakin ingin keluar?",
        on_confirm=lambda e: on_navigate(-1),  # -1 = logout
        confirm_text="Ya, Keluar",
        confirm_color=STATUS_RED,
    )
