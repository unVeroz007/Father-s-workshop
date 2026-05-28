"""
Halaman Login - Toko Ayah
==========================
Halaman pertama yang muncul saat aplikasi dibuka.
Desain sederhana: hanya username + password + tombol masuk.
"""

import flet as ft
from core.database import authenticate_user
from ui.components.shared import (
    PRIMARY_GREEN, PRIMARY_BLUE, WHITE, TEXT_PRIMARY, TEXT_SECONDARY,
    LIGHT_GREEN, FONT_BODY, FONT_TITLE, FONT_LARGE, BORDER_RADIUS,
    big_button, big_text_field, show_error_snackbar, MEDIUM_GRAY,
)


def build_login_screen(page: ft.Page, on_login_success) -> ft.Container:
    """
    Bangun halaman login.
    
    Args:
        page: Flet page object
        on_login_success: Callback saat login berhasil, menerima user dict
    """
    # Refs untuk input fields
    username_field = ft.Ref[ft.TextField]()
    password_field = ft.Ref[ft.TextField]()
    error_text = ft.Ref[ft.Text]()
    login_btn = ft.Ref[ft.ElevatedButton]()

    def handle_login(e):
        """Proses login."""
        username = username_field.current.value.strip() if username_field.current.value else ""
        password = password_field.current.value.strip() if password_field.current.value else ""

        # Validasi input
        if not username:
            _show_error("Masukkan username terlebih dahulu!")
            return
        if not password:
            _show_error("Masukkan password terlebih dahulu!")
            return

        # Loading state
        login_btn.current.disabled = True
        login_btn.current.content = "Memproses..."
        page.update()

        try:
            user = authenticate_user(username, password)
            if user:
                on_login_success(user)
            else:
                _show_error("Username atau password salah!")
                login_btn.current.disabled = False
                login_btn.current.content = "Masuk"
                page.update()
        except Exception as ex:
            _show_error(f"Terjadi kesalahan: {str(ex)}")
            login_btn.current.disabled = False
            login_btn.current.content = "Masuk"
            page.update()

    def _show_error(message: str):
        """Tampilkan pesan error."""
        error_text.current.value = message
        error_text.current.visible = True
        page.update()

    def on_field_change(e):
        """Sembunyikan error saat user mengetik."""
        if error_text.current.visible:
            error_text.current.visible = False
            page.update()

    # ============================================================
    # Layout Login
    # ============================================================
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                # Icon toko
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.STOREFRONT_ROUNDED,
                        size=72,
                        color=PRIMARY_GREEN,
                    ),
                    alignment=ft.Alignment.CENTER,
                ),
                # Judul
                ft.Text(
                    "Toko Ayah",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY_GREEN,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Elektronik & Servis",
                    size=FONT_BODY,
                    color=TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=24),
                # Form
                big_text_field(
                    label="Username",
                    hint_text="Masukkan username",
                    ref=username_field,
                    prefix_icon=ft.Icons.PERSON,
                    on_change=on_field_change,
                ),
                ft.Container(height=8),
                big_text_field(
                    label="Password",
                    hint_text="Masukkan password",
                    ref=password_field,
                    password=True,
                    prefix_icon=ft.Icons.LOCK,
                    on_change=on_field_change,
                ),
                ft.Container(height=4),
                # Error message
                ft.Text(
                    "",
                    ref=error_text,
                    size=FONT_BODY,
                    color="#C62828",
                    visible=False,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=12),
                # Tombol masuk
                ft.ElevatedButton(
                    "Masuk",
                    ref=login_btn,
                    icon=ft.Icons.LOGIN_ROUNDED,
                    on_click=handle_login,
                    width=350,
                    height=70,
                    style=ft.ButtonStyle(
                        bgcolor=PRIMARY_GREEN,
                        color=WHITE,
                        text_style=ft.TextStyle(
                            size=FONT_TITLE,
                            weight=ft.FontWeight.W_600,
                        ),
                        shape=ft.RoundedRectangleBorder(radius=BORDER_RADIUS),
                        elevation=3,
                    ),
                ),
                ft.Container(height=16),
                # Info default login
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "Login pertama kali:",
                                size=14,
                                color=TEXT_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Username: admin  |  Password: admin123",
                                size=14,
                                color=PRIMARY_BLUE,
                                weight=ft.FontWeight.W_500,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=ft.Padding.all(12),
                    border_radius=8,
                    bgcolor=LIGHT_GREEN,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        width=420,
        padding=ft.Padding.all(40),
        border_radius=20,
        bgcolor=WHITE,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    )

    # Container utama dengan background
    return ft.Container(
        content=ft.Column(
            controls=[login_card],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[LIGHT_GREEN, "#E3F2FD", LIGHT_GREEN],
        ),
        alignment=ft.Alignment.CENTER,
    )
