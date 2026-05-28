"""
Main Entry Point - Toko Ayah
==============================
Aplikasi Kasir & Servis Toko Elektronik

Entry point utama yang mengatur:
- Inisialisasi database
- Routing antar halaman
- Sidebar navigation
- Session management (login/logout)

Cara menjalankan:
    python main.py
    atau
    flet run main.py
"""

import flet as ft
from core.database import init_database, seed_default_data
from ui.components.shared import (
    create_sidebar, LIGHT_GRAY, PRIMARY_GREEN, WHITE,
    FONT_BODY, show_success_snackbar,
)
from ui.screens.login import build_login_screen
from ui.screens.dashboard import build_dashboard_screen
from ui.screens.kasir import build_kasir_screen
from ui.screens.servis import build_servis_screen
from ui.screens.laporan import build_laporan_screen
from ui.screens.settings import build_settings_screen


def main(page: ft.Page) -> None:
    """
    Fungsi utama aplikasi Flet.
    Mengatur window, routing, dan state management.
    """
    # ============================================================
    # Konfigurasi Window
    # ============================================================
    page.title = "Toko Ayah - Kasir & Servis Elektronik"
    page.window.width = 1280
    page.window.height = 800
    page.window.min_width = 1024
    page.window.min_height = 700
    # page.window.center()  # Note: async in Flet 0.85+
    page.padding = 0
    page.spacing = 0
    page.bgcolor = LIGHT_GRAY
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=PRIMARY_GREEN,
        font_family="Segoe UI",
    )

    # ============================================================
    # State Management
    # ============================================================
    current_user: dict = {}       # User yang sedang login
    active_screen_index: int = 0  # Index halaman aktif

    # Container utama untuk konten halaman
    content_area = ft.Container(expand=True)
    # Container utama untuk seluruh layout (sidebar + content)
    main_layout = ft.Row(expand=True, spacing=0)

    # ============================================================
    # Inisialisasi Database
    # ============================================================
    try:
        init_database()
        seed_default_data()
    except Exception as e:
        page.add(
            ft.Container(
                content=ft.Text(
                    f"❌ Gagal menginisialisasi database:\n{str(e)}",
                    size=FONT_BODY,
                    color="#C62828",
                ),
                padding=ft.Padding.all(40),
            )
        )
        return

    # ============================================================
    # Navigation Functions
    # ============================================================
    def navigate_to(screen_index: int) -> None:
        """
        Navigasi ke halaman berdasarkan index.
        -1 = Logout (kembali ke login)
        0 = Dashboard
        1 = Kasir
        2 = Servis
        3 = Laporan
        4 = Pengaturan
        """
        nonlocal active_screen_index

        if screen_index == -1:
            # Logout
            handle_logout()
            return

        active_screen_index = screen_index
        _build_main_layout()

    def handle_login_success(user: dict) -> None:
        """Callback saat login berhasil."""
        nonlocal current_user
        current_user = user
        show_success_snackbar(page, f"Selamat datang, {user.get('username', 'Admin')}!")
        navigate_to(0)  # Ke dashboard

    def handle_logout() -> None:
        """Proses logout."""
        nonlocal current_user
        current_user = {}
        _show_login_screen()

    def _show_login_screen() -> None:
        """Tampilkan halaman login."""
        page.controls.clear()
        login_screen = build_login_screen(page, handle_login_success)
        page.add(login_screen)
        page.update()

    def _build_main_layout() -> None:
        """Bangun layout utama (sidebar + konten)."""
        nonlocal main_layout

        # Bangun sidebar
        sidebar = create_sidebar(
            page=page,
            active_index=active_screen_index,
            on_navigate=navigate_to,
        )

        # Bangun konten berdasarkan index aktif
        screen_builders = {
            0: lambda: build_dashboard_screen(page, navigate_to, current_user),
            1: lambda: build_kasir_screen(page, current_user),
            2: lambda: build_servis_screen(page, current_user),
            3: lambda: build_laporan_screen(page, current_user),
            4: lambda: build_settings_screen(page, current_user),
        }

        builder = screen_builders.get(active_screen_index, screen_builders[0])
        content = builder()

        # Susun layout: Sidebar (kiri) + Content (kanan)
        page.controls.clear()
        main_layout = ft.Row(
            controls=[
                sidebar,
                ft.VerticalDivider(width=1, color="#E0E0E0"),
                ft.Container(
                    content=content,
                    expand=True,
                    bgcolor=LIGHT_GRAY,
                ),
            ],
            expand=True,
            spacing=0,
        )
        page.add(main_layout)
        page.update()

    # ============================================================
    # Start: Tampilkan Login Screen
    # ============================================================
    _show_login_screen()


# ==============================================================================
# Entry Point
# ==============================================================================
if __name__ == "__main__":
    ft.app(target=main)
