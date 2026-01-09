"""
ChwiliTranslate - Gerçek Zamanlı Ekran OCR ve Çeviri Uygulaması
Ana giriş noktası
"""

import sys
import threading
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QAction
from pynput import keyboard

from src.ui.main_window import MainWindow
from src.ui.components.ocr_control import OCRControlPanel
from src.ui.components.translation_panel import TranslationPanel
from src.ui.components.overlay_settings import OverlaySettingsPanel
from src.ui.components.settings_panel import SettingsPanel
from src.ui.components.status_bar import StatusBar
from src.ui.components.region_selector_overlay import RegionSelectorOverlay
from src.ui.components.hotkey_panel import HotkeyPanel

from src.app_controller import ApplicationController
from src.utils.hotkey_manager import HotkeyManager
from src.ocr.engine import OCREngine
from src.ocr.region_selector import RegionSelector
from src.translate.engine import TranslationEngine
from src.translate.cache import CacheManager
from src.overlay.overlay_window import OverlayWindow
from src.utils.config import ConfigManager
from src.utils.logger import logger


class DashboardPage(QWidget):
    """Ana sayfa dashboard"""
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_GREEN = "#22c55e"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self, status_bar: StatusBar):
        super().__init__()
        self.status_bar = status_bar
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("ChwiliTranslate")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.ACCENT_PURPLE};")
        layout.addWidget(title)
        
        subtitle = QLabel("Gerçek Zamanlı Ekran OCR ve Çeviri")
        subtitle.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Status bar'ı ekle
        layout.addWidget(self.status_bar)
        
        layout.addSpacing(20)
        
        # Hızlı erişim kartları
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)
        
        # OCR kartı
        ocr_card = self._create_quick_card(
            "📷", "OCR Durumu", "Bölge seçilmedi", self.ACCENT_PURPLE
        )
        self._ocr_status_label = ocr_card.findChild(QLabel, "statusLabel")
        cards_layout.addWidget(ocr_card)
        
        # Çeviri kartı
        trans_card = self._create_quick_card(
            "🌐", "Çeviri", "Hazır", self.ACCENT_VIOLET
        )
        self._trans_status_label = trans_card.findChild(QLabel, "statusLabel")
        cards_layout.addWidget(trans_card)
        
        # Cache kartı
        cache_card = self._create_quick_card(
            "💾", "Cache", "Aktif", "#d946ef"
        )
        self._cache_status_label = cache_card.findChild(QLabel, "statusLabel")
        cards_layout.addWidget(cache_card)
        
        layout.addLayout(cards_layout)
        
        layout.addSpacing(20)
        
        # Kullanım bilgisi
        info_card = QFrame()
        info_card.setObjectName("infoCard")
        info_layout = QVBoxLayout(info_card)
        
        info_title = QLabel("🚀 Hızlı Başlangıç")
        info_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        info_layout.addWidget(info_title)
        
        steps = [
            "1. Sol menüden 📷 OCR Control'e gidin",
            "2. 'Bölge Seç' butonuna tıklayın ve ekranda bir alan seçin",
            "3. 🌐 Translation'dan çeviri sağlayıcısını seçin",
            "4. START butonuna basın!"
        ]
        
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px; padding: 5px 0;")
            info_layout.addWidget(step_label)
        
        layout.addWidget(info_card)
        
        # Önbellek bilgi kartı
        cache_info_card = QFrame()
        cache_info_card.setObjectName("infoCard")
        cache_info_layout = QVBoxLayout(cache_info_card)
        
        cache_info_title = QLabel("💡 Önbellek Hakkında")
        cache_info_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        cache_info_layout.addWidget(cache_info_title)
        
        cache_tips = [
            "• Önbellek, aynı metinlerin tekrar çevrilmesini önler",
            "• API kullanımını azaltır ve hızı artırır",
            "• Çeviri sağlayıcısı değiştirdiğinizde temizlemeniz önerilir",
            "• Yanlış çeviriler varsa temizleyip yeniden deneyin"
        ]
        
        for tip in cache_tips:
            tip_label = QLabel(tip)
            tip_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 12px; padding: 2px 0;")
            cache_info_layout.addWidget(tip_label)
        
        layout.addWidget(cache_info_card)
        
        layout.addStretch()
    
    def _create_quick_card(self, icon: str, title: str, status: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("quickCard")
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        # Icon ve başlık
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Durum
        status_label = QLabel(status)
        status_label.setObjectName("statusLabel")
        status_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(status_label)
        
        return card
    
    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
            #quickCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 10, 32, 0.95), stop:1 rgba(12, 6, 20, 0.95));
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 15px;
                padding: 15px;
            }}
            #infoCard {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18, 8, 28, 0.95), stop:1 rgba(10, 5, 18, 0.95));
                border: 1px solid rgba(168, 85, 247, 0.15);
                border-radius: 15px;
                padding: 20px;
            }}
        """)
    
    def set_ocr_status(self, text: str) -> None:
        if self._ocr_status_label:
            self._ocr_status_label.setText(text)
    
    def set_translation_status(self, text: str) -> None:
        if self._trans_status_label:
            self._trans_status_label.setText(text)


class ChwiliTranslateApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        # Windows taskbar ikonu için AppUserModelID ayarla
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ChwiliTranslate.App.1.0")
        except:
            pass
        
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ChwiliTranslate")
        
        # Uygulama ikonunu ayarla (taskbar için)
        import os
        icon_path = os.path.join(os.path.dirname(__file__), "assets", "icons", "app_icon.ico")
        if os.path.exists(icon_path):
            app_icon = QIcon(icon_path)
            self.app.setWindowIcon(app_icon)
        
        # Bileşenleri başlat
        self._init_components()
        
        # UI'ı oluştur
        self._init_ui()
        
        # Bağlantıları kur
        self._connect_signals()
        
        logger.info("ChwiliTranslate başlatıldı")
    
    def _init_components(self) -> None:
        """Backend bileşenlerini başlatır"""
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()
        
        self.cache_manager = CacheManager()
        self.translation_engine = TranslationEngine(self.cache_manager)
        self.ocr_engine = OCREngine()
        self.region_selector = RegionSelector()
        self.overlay_window = OverlayWindow()
        
        self.app_controller = ApplicationController()
        self.app_controller.set_ocr_engine(self.ocr_engine)
        self.app_controller.set_translation_engine(self.translation_engine)
        self.app_controller.set_cache_manager(self.cache_manager)
        self.app_controller.set_region_selector(self.region_selector)
        self.app_controller.set_overlay_window(self.overlay_window)
        
        # Region selector overlay
        self.region_overlay = RegionSelectorOverlay()
        
        # Hotkey manager
        self.hotkey_manager = HotkeyManager()
        
        # Global F9 hotkey için pynput listener
        self._setup_global_hotkey()
        
        # Kaydedilmiş API anahtarlarını yükle
        self._load_saved_api_keys()
        
        # Kaydedilmiş bölgeleri yükle
        self._load_saved_regions()
    
    def _load_saved_api_keys(self) -> None:
        """Kaydedilmiş API anahtarlarını yükler"""
        from src.translate.providers import TranslationProvider
        provider_map = {
            "chatgpt": TranslationProvider.CHATGPT,
            "gemini": TranslationProvider.GEMINI,
            "google": TranslationProvider.GOOGLE,
            "deepl": TranslationProvider.DEEPL
        }
        
        api_keys = self.config.translation.api_keys
        for name, key in api_keys.items():
            if key and name in provider_map:
                self.translation_engine.set_api_key(provider_map[name], key)
                logger.info(f"{name} API anahtarı yüklendi")
    
    def _load_saved_regions(self) -> None:
        """Kaydedilmiş OCR bölgelerini yükler"""
        from src.ocr.region_selector import Region
        
        regions_data = self.config.regions.regions
        if regions_data:
            regions = []
            for r in regions_data:
                region = Region.from_dict(r)
                regions.append(region)
            self.region_selector.set_regions(regions)
            logger.info(f"Kaydedilmiş bölgeler yüklendi: {len(regions)} bölge")
    
    def _save_regions(self) -> None:
        """OCR bölgelerini kaydeder"""
        regions = self.region_selector.get_regions()
        regions_data = [r.to_dict() for r in regions]
        self.config_manager.update_regions(regions_data)
    
    def _setup_global_hotkey(self) -> None:
        """Global F9 hotkey için pynput listener başlatır"""
        self._f9_pressed = False
        
        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    self._f9_pressed = True
            except:
                pass
        
        # Listener'ı ayrı thread'de başlat
        self._keyboard_listener = keyboard.Listener(on_press=on_press)
        self._keyboard_listener.daemon = True
        self._keyboard_listener.start()
    
    def _check_global_hotkey(self) -> None:
        """Global hotkey kontrolü (timer ile)"""
        if self._f9_pressed:
            self._f9_pressed = False
            self._toggle_window()
    
    def _toggle_window(self) -> None:
        """Pencereyi gizle/göster"""
        if self.main_window.isVisible():
            self.main_window.hide()
            logger.info("Uygulama gizlendi (F9)")
        else:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
            logger.info("Uygulama gösterildi (F9)")
    
    def _load_exclusion_areas(self) -> None:
        """Kaydedilmiş hariç tutulan alanları yükler"""
        areas = self.config.system.exclusion_areas
        if areas:
            self.settings_panel.set_exclusion_areas(areas)
            self.app_controller.set_exclusion_areas(areas)
            logger.info(f"Hariç tutulan alanlar yüklendi: {len(areas)} alan")
    
    def _load_overlay_settings(self) -> None:
        """Kaydedilmiş overlay ayarlarını yükler"""
        overlay = self.config.overlay
        
        # Panel ayarlarını yükle
        self.overlay_panel.set_opacity(overlay.opacity)
        self.overlay_panel.set_font_size(overlay.font_size)
        self.overlay_panel.set_font_family(overlay.font_family)
        self.overlay_panel.set_position(overlay.position.x, overlay.position.y)
        self.overlay_panel.set_blur_enabled(overlay.background_blur)
        self.overlay_panel.set_glow_enabled(overlay.glow_effect)
        self.overlay_panel.set_shadow_enabled(overlay.text_shadow)
        self.overlay_panel.set_bold_enabled(overlay.bold)
        self.overlay_panel.set_italic_enabled(overlay.italic)
        self.overlay_panel.set_text_color(overlay.text_color)
        self.overlay_panel.set_bg_color(overlay.bg_color)
        self.overlay_panel.set_glow_color(overlay.glow_color)
        
        # Overlay window'a uygula
        self.overlay_window.set_opacity(overlay.opacity)
        self.overlay_window.set_font_size(overlay.font_size)
        self.overlay_window.set_font_family(overlay.font_family)
        self.overlay_window.set_position(overlay.position.x, overlay.position.y)
        self.overlay_window.set_background_blur(overlay.background_blur)
        self.overlay_window.set_glow_effect(overlay.glow_effect)
        self.overlay_window.set_text_shadow(overlay.text_shadow)
        self.overlay_window.set_bold(overlay.bold)
        self.overlay_window.set_italic(overlay.italic)
        self.overlay_window.set_text_color(overlay.text_color)
        self.overlay_window.set_bg_color(overlay.bg_color)
        self.overlay_window.set_glow_color(overlay.glow_color)
        
        logger.info("Overlay ayarları yüklendi")
    
    def _init_ui(self) -> None:
        """UI bileşenlerini oluşturur"""
        self.main_window = MainWindow()
        
        # Status bar
        self.status_bar = StatusBar()
        
        # GPU durumunu kontrol et ve status bar'a aktar
        gpu_available = self.ocr_engine._check_gpu()
        gpu_enabled = self.ocr_engine.is_gpu_enabled()
        self.status_bar.set_gpu_status(gpu_enabled, gpu_available)
        
        # Dashboard (Ana Sayfa)
        self.dashboard = DashboardPage(self.status_bar)
        
        # Panelleri oluştur
        self.ocr_panel = OCRControlPanel()
        self.translation_panel = TranslationPanel()
        self.overlay_panel = OverlaySettingsPanel()
        self.settings_panel = SettingsPanel()
        self.hotkey_panel = HotkeyPanel(self.hotkey_manager)
        
        # Panelleri ana pencereye ekle
        self.main_window.set_page_widget(0, self.dashboard)
        self.main_window.set_page_widget(1, self.ocr_panel)
        self.main_window.set_page_widget(2, self.translation_panel)
        self.main_window.set_page_widget(3, self.overlay_panel)
        self.main_window.set_page_widget(4, self.settings_panel)
        self.main_window.set_page_widget(5, self.hotkey_panel)
        
        # Kaydedilmiş API anahtarlarını panel'e yükle
        self.translation_panel.set_api_keys(self.config.translation.api_keys)
        
        # Kaydedilmiş hariç tutulan alanları yükle
        self._load_exclusion_areas()
        
        # Kaydedilmiş overlay ayarlarını yükle
        self._load_overlay_settings()
        
        # Kaydedilmiş bölgeleri UI'a yükle
        self._update_regions_ui()
        
        # Sistem tepsisi oluştur
        self._setup_system_tray()
        
        # Başlangıçta anasayfayı göster
        self.main_window.set_page(0)
    
    def _setup_system_tray(self) -> None:
        """Sistem tepsisi ikonunu oluşturur"""
        self.tray_icon = QSystemTrayIcon(self.main_window)
        
        # İkon dosyasını yükle
        import os
        base_path = os.path.join(os.path.dirname(__file__), "assets", "icons")
        ico_path = os.path.join(base_path, "app_icon.ico")
        png_path = os.path.join(base_path, "app_icon.png")
        
        if os.path.exists(ico_path):
            app_icon = QIcon(ico_path)
        elif os.path.exists(png_path):
            app_icon = QIcon(png_path)
        else:
            # Fallback - basit ikon oluştur
            from PyQt6.QtGui import QPixmap, QPainter, QColor
            pixmap = QPixmap(32, 32)
            pixmap.fill(QColor(0, 212, 255))
            painter = QPainter(pixmap)
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "CT")
            painter.end()
            app_icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(app_icon)
        self.tray_icon.setToolTip("ChwiliTranslate")
        
        # Ana pencereye de ikonu ekle
        self.main_window.setWindowIcon(app_icon)
        
        # Tray menüsü
        tray_menu = QMenu()
        
        show_action = QAction("Göster", self.main_window)
        show_action.triggered.connect(self._show_from_tray)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Çıkış", self.main_window)
        quit_action.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()
    
    def _on_tray_activated(self, reason) -> None:
        """Tray ikonuna tıklandığında"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_from_tray()
    
    def _show_from_tray(self) -> None:
        """Uygulamayı tray'den geri getirir"""
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()
    
    def _quit_app(self) -> None:
        """Uygulamayı kapatır"""
        self.app_controller.stop()
        self.tray_icon.hide()
        self.app.quit()


    
    def _connect_signals(self) -> None:
        """Sinyal bağlantılarını kurar"""
        # Status bar
        self.status_bar.start_clicked.connect(self._on_start)
        self.status_bar.stop_clicked.connect(self._on_stop)
        
        # App controller
        self.app_controller.on_state_changed(self._on_state_changed)
        self.app_controller.on_text_detected(self._on_text_detected)
        self.app_controller.on_translation_complete(self._on_translation_complete)
        
        # Overlay window - sürükleme ile konum değişikliği
        self.overlay_window.on_position_changed(self._on_overlay_dragged)
        
        # OCR panel - Bölge Seç butonu
        self.ocr_panel.select_region_clicked.connect(self._on_select_region)
        self.ocr_panel.add_region_clicked.connect(self._on_add_region)
        self.ocr_panel.edit_region_clicked.connect(self._on_edit_region)
        self.ocr_panel.remove_region_clicked.connect(self._on_remove_region)
        self.ocr_panel.region_enabled_changed.connect(self._on_region_enabled_changed)
        self.ocr_panel.region_name_changed.connect(self._on_region_name_changed)
        self.ocr_panel.speed_changed.connect(
            lambda s: self.ocr_engine.set_speed(s.lower())
        )
        self.ocr_panel.gpu_changed.connect(self._on_gpu_changed)
        
        # Region selector overlay
        self.region_overlay.region_selected.connect(self._on_region_selected)
        self.region_overlay.selection_cancelled.connect(self._on_region_cancelled)
        
        # Translation panel
        self.translation_panel.provider_changed.connect(self._on_provider_changed)
        self.translation_panel.api_keys_updated.connect(self._on_api_keys_updated)
        self.translation_panel.source_lang_changed.connect(self._on_source_lang_changed)
        self.translation_panel.target_lang_changed.connect(self._on_target_lang_changed)
        
        # Settings panel
        self.settings_panel.cache_changed.connect(self.cache_manager.set_enabled)
        self.settings_panel.clear_cache_clicked.connect(self.cache_manager.clear)
        self.settings_panel.add_exclusion_clicked.connect(self._on_add_exclusion_area)
        self.settings_panel.exclusion_areas_changed.connect(self._on_exclusion_areas_changed)
        
        # Overlay panel
        self.overlay_panel.opacity_changed.connect(self._on_overlay_opacity_changed)
        self.overlay_panel.font_size_changed.connect(self._on_overlay_font_size_changed)
        self.overlay_panel.font_family_changed.connect(self._on_overlay_font_family_changed)
        self.overlay_panel.position_changed.connect(self._on_overlay_position_changed)
        self.overlay_panel.blur_changed.connect(self._on_overlay_blur_changed)
        self.overlay_panel.glow_changed.connect(self._on_overlay_glow_changed)
        self.overlay_panel.bold_changed.connect(self._on_bold_changed)
        self.overlay_panel.italic_changed.connect(self._on_italic_changed)
        self.overlay_panel.shadow_changed.connect(self._on_shadow_changed)
        self.overlay_panel.text_color_changed.connect(self._on_overlay_text_color_changed)
        self.overlay_panel.bg_color_changed.connect(self._on_overlay_bg_color_changed)
        self.overlay_panel.glow_color_changed.connect(self._on_overlay_glow_color_changed)
        
        # FPS güncelleme timer'ı
        from PyQt6.QtCore import QTimer
        self._fps_timer = QTimer()
        self._fps_timer.timeout.connect(self._update_fps)
        self._fps_timer.start(500)  # Her 500ms'de güncelle
        
        # Canlı önizleme timer'ı
        self._preview_timer = QTimer()
        self._preview_timer.timeout.connect(self._update_preview)
        self._preview_timer.start(1000)  # Her 1 saniyede güncelle
        
        # Cache sayısı güncelleme timer'ı
        self._cache_timer = QTimer()
        self._cache_timer.timeout.connect(self._update_cache_info)
        self._cache_timer.start(2000)  # Her 2 saniyede güncelle
        
        # Global hotkey timer'ı (F9 için)
        self._hotkey_timer = QTimer()
        self._hotkey_timer.timeout.connect(self._check_global_hotkey)
        self._hotkey_timer.start(100)  # Her 100ms'de kontrol et
        
        # Hotkey manager'ı ana pencereye bağla
        self.hotkey_manager.set_widget(self.main_window)
        self._register_hotkey_callbacks()
    
    def _update_fps(self) -> None:
        """FPS değerini günceller"""
        fps = self.app_controller.get_fps()
        self.status_bar.set_fps(fps)
    
    def _update_preview(self) -> None:
        """Canlı önizlemeyi günceller"""
        from src.app_controller import AppState
        if self.app_controller.get_state() != AppState.RUNNING:
            return
        
        region = self.region_selector.get_current_region()
        if not region:
            return
        
        try:
            preview_data = self.region_selector.capture_region(region)
            self.ocr_panel.set_preview_image(preview_data)
        except Exception:
            pass
    
    def _update_cache_info(self) -> None:
        """Cache bilgisini günceller"""
        try:
            stats = self.cache_manager.get_stats()
            count = stats.get("total_entries", 0)
            self.settings_panel.set_cache_info(count)
        except Exception:
            pass
    
    def _register_hotkey_callbacks(self) -> None:
        """Hotkey callback'lerini kaydeder"""
        # Genel
        self.hotkey_manager.register_callback("toggle_ocr", self._hotkey_toggle_ocr)
        self.hotkey_manager.register_callback("toggle_app", self._hotkey_toggle_app)
        self.hotkey_manager.register_callback("select_region", self._hotkey_select_region)
        self.hotkey_manager.register_callback("toggle_settings", self._hotkey_toggle_settings)
        self.hotkey_manager.register_callback("clear_cache", self._hotkey_clear_cache)
        
        # OCR & Çeviri
        self.hotkey_manager.register_callback("instant_ocr", self._hotkey_instant_ocr)
        self.hotkey_manager.register_callback("retranslate", self._hotkey_retranslate)
        self.hotkey_manager.register_callback("restart_ocr", self._hotkey_restart_ocr)
        
        # Overlay
        self.hotkey_manager.register_callback("font_size_up", self._hotkey_font_size_up)
        self.hotkey_manager.register_callback("font_size_down", self._hotkey_font_size_down)
        self.hotkey_manager.register_callback("opacity_up", self._hotkey_opacity_up)
        self.hotkey_manager.register_callback("opacity_down", self._hotkey_opacity_down)
        
        # Uygulama
        self.hotkey_manager.register_callback("quit_app", self._hotkey_quit_app)
    
    def _hotkey_toggle_ocr(self) -> None:
        """F8 - OCR Başlat/Durdur"""
        from src.app_controller import AppState
        if self.app_controller.get_state() == AppState.RUNNING:
            self._on_stop()
        else:
            self._on_start()
    
    def _hotkey_toggle_app(self) -> None:
        """F9 - Uygulamayı Gizle/Göster (sistem tepsisine)"""
        if self.main_window.isVisible():
            self.main_window.hide()
            logger.info("Uygulama sistem tepsisine gizlendi")
        else:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()
            logger.info("Uygulama geri getirildi")
    
    def _hotkey_select_region(self) -> None:
        """F10 - OCR Bölgesi Seç"""
        self._on_select_region()
    
    def _hotkey_toggle_settings(self) -> None:
        """F11 - Ayarlar Paneli"""
        current = self.main_window.get_current_page()
        if current == 4:
            self.main_window.set_page(0)
        else:
            self.main_window.set_page(4)
    
    def _hotkey_clear_cache(self) -> None:
        """F12 - Cache Temizle"""
        self.cache_manager.clear()
        logger.info("Cache temizlendi (kısayol)")
    
    def _hotkey_instant_ocr(self) -> None:
        """Ctrl+Shift+O - Anlık OCR"""
        region = self.region_selector.get_current_region()
        if region:
            try:
                image_data = self.region_selector.capture_region(region)
                text = self.ocr_engine.recognize(image_data)
                if text:
                    result = self.translation_engine.translate(text)
                    if result:
                        self.overlay_window.set_text(result.translated_text)
                        self.overlay_window.show_overlay()
            except Exception as e:
                logger.error(f"Anlık OCR hatası: {e}")
    
    def _hotkey_retranslate(self) -> None:
        """Ctrl+Shift+T - Yeniden Çevir"""
        # Son metni yeniden çevir
        pass
    
    def _hotkey_restart_ocr(self) -> None:
        """Ctrl+Shift+R - OCR Yeniden Başlat"""
        from src.app_controller import AppState
        if self.app_controller.get_state() == AppState.RUNNING:
            self._on_stop()
            self._on_start()
    
    def _hotkey_font_size_up(self) -> None:
        """Ctrl+Shift+Up - Yazı Boyutu Artır"""
        current = self.config.overlay.font_size
        new_size = min(current + 2, 72)
        self._on_overlay_font_size_changed(new_size)
        self.overlay_panel.set_font_size(new_size)
    
    def _hotkey_font_size_down(self) -> None:
        """Ctrl+Shift+Down - Yazı Boyutu Azalt"""
        current = self.config.overlay.font_size
        new_size = max(current - 2, 8)
        self._on_overlay_font_size_changed(new_size)
        self.overlay_panel.set_font_size(new_size)
    
    def _hotkey_opacity_up(self) -> None:
        """Ctrl+Shift+Right - Opaklık Artır"""
        current = self.config.overlay.opacity
        new_val = min(current + 0.1, 1.0)
        self._on_overlay_opacity_changed(new_val)
        self.overlay_panel.set_opacity(new_val)
    
    def _hotkey_opacity_down(self) -> None:
        """Ctrl+Shift+Left - Opaklık Azalt"""
        current = self.config.overlay.opacity
        new_val = max(current - 0.1, 0.1)
        self._on_overlay_opacity_changed(new_val)
        self.overlay_panel.set_opacity(new_val)
    
    def _hotkey_quit_app(self) -> None:
        """Ctrl+Shift+Q - Uygulamayı Kapat"""
        self._quit_app()
    
    def _on_text_detected(self, text: str) -> None:
        """Metin algılandığında"""
        logger.info(f"OCR algıladı: {text[:50]}...")
    
    def _on_translation_complete(self, result) -> None:
        """Çeviri tamamlandığında"""
        if result:
            logger.info(f"Çeviri: {result.translated_text[:50]}...")
            self.dashboard.set_translation_status("Çevrildi")
    
    def _on_source_lang_changed(self, lang: str) -> None:
        """Kaynak dil değiştiğinde"""
        self.translation_engine.set_languages(lang, self.translation_panel.get_target_language())
    
    def _on_target_lang_changed(self, lang: str) -> None:
        """Hedef dil değiştiğinde"""
        self.translation_engine.set_languages(self.translation_panel.get_source_language(), lang)
    
    def _on_bold_changed(self, enabled: bool) -> None:
        """Kalın yazı değiştiğinde"""
        self.overlay_window.set_bold(enabled)
        self.config.overlay.bold = enabled
        self.config_manager.save(self.config)
    
    def _on_italic_changed(self, enabled: bool) -> None:
        """İtalik yazı değiştiğinde"""
        self.overlay_window.set_italic(enabled)
        self.config.overlay.italic = enabled
        self.config_manager.save(self.config)
    
    def _on_shadow_changed(self, enabled: bool) -> None:
        """Yazı gölgesi değiştiğinde"""
        self.overlay_window.set_text_shadow(enabled)
        self.config.overlay.text_shadow = enabled
        self.config_manager.save(self.config)
    
    def _on_overlay_opacity_changed(self, value: float) -> None:
        """Overlay saydamlık değiştiğinde"""
        self.overlay_window.set_opacity(value)
        self.config.overlay.opacity = value
        self.config_manager.save(self.config)
    
    def _on_overlay_font_size_changed(self, size: int) -> None:
        """Overlay font boyutu değiştiğinde"""
        self.overlay_window.set_font_size(size)
        self.config.overlay.font_size = size
        self.config_manager.save(self.config)
    
    def _on_overlay_font_family_changed(self, family: str) -> None:
        """Overlay font ailesi değiştiğinde"""
        self.overlay_window.set_font_family(family)
        self.config.overlay.font_family = family
        self.config_manager.save(self.config)
    
    def _on_overlay_position_changed(self, x: int, y: int) -> None:
        """Overlay konumu değiştiğinde (panel'den)"""
        self.overlay_window.set_position(x, y)
        self.config.overlay.position.x = x
        self.config.overlay.position.y = y
        self.config_manager.save(self.config)
    
    def _on_overlay_dragged(self, x: int, y: int) -> None:
        """Overlay sürüklendiğinde (mouse ile)"""
        self.config.overlay.position.x = x
        self.config.overlay.position.y = y
        self.config_manager.save(self.config)
        # Panel'deki konum değerlerini de güncelle
        self.overlay_panel.set_position(x, y)
        logger.info(f"Overlay konumu kaydedildi: {x}, {y}")
    
    def _on_overlay_blur_changed(self, enabled: bool) -> None:
        """Overlay arka plan değiştiğinde"""
        self.overlay_window.set_background_blur(enabled)
        self.config.overlay.background_blur = enabled
        self.config_manager.save(self.config)
    
    def _on_overlay_glow_changed(self, enabled: bool) -> None:
        """Overlay glow efekti değiştiğinde"""
        self.overlay_window.set_glow_effect(enabled)
        self.config.overlay.glow_effect = enabled
        self.config_manager.save(self.config)
    
    def _on_overlay_text_color_changed(self, color: str) -> None:
        """Overlay yazı rengi değiştiğinde"""
        self.overlay_window.set_text_color(color)
        self.config.overlay.text_color = color
        self.config_manager.save(self.config)
    
    def _on_overlay_bg_color_changed(self, color: str) -> None:
        """Overlay arka plan rengi değiştiğinde"""
        self.overlay_window.set_bg_color(color)
        self.config.overlay.bg_color = color
        self.config_manager.save(self.config)
    
    def _on_overlay_glow_color_changed(self, color: str) -> None:
        """Overlay glow rengi değiştiğinde"""
        self.overlay_window.set_glow_color(color)
        self.config.overlay.glow_color = color
        self.config_manager.save(self.config)
    
    def _on_add_exclusion_area(self) -> None:
        """Hariç tutulan alan ekle butonuna tıklandığında"""
        logger.info("Hariç tutulan alan seçimi başlatılıyor...")
        self._selecting_exclusion = True
        self.main_window.hide()
        self.region_overlay.start_selection()
    
    def _on_exclusion_areas_changed(self, areas: list) -> None:
        """Hariç tutulan alanlar değiştiğinde"""
        self.app_controller.set_exclusion_areas(areas)
        # Config'e kaydet
        self.config.system.exclusion_areas = areas
        self.config_manager.save(self.config)
        logger.info(f"Hariç tutulan alanlar kaydedildi: {len(areas)} alan")
    
    def _on_select_region(self) -> None:
        """Bölge seç butonuna tıklandığında (yeni bölge ekle)"""
        logger.info("Bölge seçimi başlatılıyor...")
        self._selecting_exclusion = False
        self._editing_region_index = -1  # Yeni bölge
        self.main_window.hide()
        # Hariç tutulan alanları overlay'e gönder
        self.region_overlay.set_exclusion_areas(self.settings_panel.get_exclusion_areas())
        self.region_overlay.start_selection()
    
    def _on_add_region(self) -> None:
        """Yeni OCR bölgesi ekle"""
        if not self.region_selector.can_add_region():
            logger.warning("Maksimum bölge sayısına ulaşıldı")
            return
        self._on_select_region()
    
    def _on_edit_region(self, index: int) -> None:
        """Mevcut bölgeyi düzenle"""
        logger.info(f"Bölge düzenleniyor: {index}")
        self._selecting_exclusion = False
        self._editing_region_index = index
        self.main_window.hide()
        self.region_overlay.set_exclusion_areas(self.settings_panel.get_exclusion_areas())
        self.region_overlay.start_selection()
    
    def _on_remove_region(self, index: int) -> None:
        """Bölgeyi sil"""
        if self.region_selector.remove_region(index):
            logger.info(f"Bölge silindi: {index}")
            self._update_regions_ui()
    
    def _on_region_enabled_changed(self, index: int, enabled: bool) -> None:
        """Bölge aktifliği değişti"""
        self.region_selector.set_region_enabled(index, enabled)
        self._save_regions()
        logger.info(f"Bölge {index} aktiflik: {enabled}")
    
    def _on_region_name_changed(self, index: int, name: str) -> None:
        """Bölge ismi değişti"""
        regions = self.region_selector.get_regions()
        if 0 <= index < len(regions):
            regions[index].name = name
            self.region_selector.set_regions(regions)
            self._save_regions()
            logger.info(f"Bölge {index} ismi değişti: {name}")
    
    def _update_regions_ui(self) -> None:
        """Bölge listesini UI'da güncelle ve kaydet"""
        regions = self.region_selector.get_regions()
        self.ocr_panel.set_regions(regions)
        
        # Bölgeleri kaydet
        self._save_regions()
        
        # Dashboard'u güncelle
        enabled_count = len(self.region_selector.get_enabled_regions())
        if enabled_count > 0:
            self.dashboard.set_ocr_status(f"{enabled_count} bölge aktif")
        else:
            self.dashboard.set_ocr_status("Bölge seçilmedi")
    
    def _on_region_selected(self, x: int, y: int, w: int, h: int) -> None:
        """Bölge seçildiğinde"""
        logger.info(f"Bölge seçildi: {x}, {y}, {w}x{h}")
        
        # Hariç tutulan alan mı yoksa OCR bölgesi mi?
        if getattr(self, '_selecting_exclusion', False):
            # Hariç tutulan alan ekleniyor
            self.settings_panel.add_exclusion_area(x, y, w, h)
            self._selecting_exclusion = False
            self.main_window.show()
            return
        
        # OCR bölgesi seçildi
        from src.ocr.region_selector import Region
        editing_index = getattr(self, '_editing_region_index', -1)
        
        if editing_index >= 0:
            # Mevcut bölgeyi güncelle
            region = Region(x=x, y=y, width=w, height=h, name=f"Bölge {editing_index + 1}")
            regions = self.region_selector.get_regions()
            if editing_index < len(regions):
                regions[editing_index] = region
                self.region_selector.set_regions(regions)
        else:
            # Yeni bölge ekle
            region = Region(x=x, y=y, width=w, height=h)
            self.region_selector.add_region(region)
        
        self._editing_region_index = -1
        self._update_regions_ui()
        
        # Önizleme al
        try:
            preview_data = self.region_selector.capture_region(region)
            self.ocr_panel.set_preview_image(preview_data)
        except Exception as e:
            logger.error(f"Önizleme hatası: {e}")
        
        self.main_window.show()
        
        self.main_window.show()
    
    def _on_region_cancelled(self) -> None:
        """Bölge seçimi iptal edildiğinde"""
        logger.info("Bölge seçimi iptal edildi")
        self.main_window.show()
    
    def _on_start(self) -> None:
        """START butonuna tıklandığında"""
        # Bölge seçilmiş mi kontrol et
        region = self.region_selector.get_current_region()
        if not region:
            self._show_warning_dialog(
                "OCR Bölgesi Gerekli",
                "Başlamadan önce bir OCR bölgesi seçmelisiniz.",
                "📷 OCR Control sayfasından 'Bölge Seç' butonuna tıklayın."
            )
            return
        
        self.app_controller.start()
        self.overlay_window.show_overlay()
        logger.info("OCR döngüsü başlatıldı")
    
    def _show_warning_dialog(self, title: str, message: str, hint: str) -> None:
        """Özel uyarı dialogu gösterir"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        from PyQt6.QtCore import Qt
        
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("ChwiliTranslate")
        dialog.setFixedSize(400, 200)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Başlık
        title_label = QLabel(f"⚠️ {title}")
        title_label.setStyleSheet("color: #fbbf24; font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Mesaj
        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        # İpucu
        hint_label = QLabel(hint)
        hint_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        hint_label.setWordWrap(True)
        layout.addWidget(hint_label)
        
        layout.addStretch()
        
        # Tamam butonu
        ok_btn = QPushButton("Tamam")
        ok_btn.setFixedHeight(40)
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)
        
        # Dialog stili
        dialog.setStyleSheet("""
            QDialog {
                background-color: #0f0f1a;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
            }
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00b8e6;
            }
        """)
        
        dialog.exec()
    
    def _on_stop(self) -> None:
        """STOP butonuna tıklandığında"""
        self.app_controller.stop()
        self.overlay_window.hide_overlay()
        logger.info("OCR döngüsü durduruldu")
    
    def _on_state_changed(self, state) -> None:
        """Uygulama durumu değiştiğinde"""
        from src.app_controller import AppState
        self.status_bar.set_running(state == AppState.RUNNING)
    
    def _on_gpu_changed(self, enabled: bool) -> None:
        """GPU ayarı değiştiğinde"""
        self.ocr_engine.enable_gpu(enabled)
        gpu_available = self.ocr_engine._check_gpu()
        self.status_bar.set_gpu_status(enabled, gpu_available)
    
    def _on_provider_changed(self, provider: str) -> None:
        """Çeviri sağlayıcısı değiştiğinde"""
        from src.translate.providers import TranslationProvider
        provider_map = {
            "chatgpt": TranslationProvider.CHATGPT,
            "gemini": TranslationProvider.GEMINI,
            "google": TranslationProvider.GOOGLE,
            "deepl": TranslationProvider.DEEPL
        }
        if provider in provider_map:
            self.translation_engine.set_provider(provider_map[provider])
            logger.info(f"Çeviri sağlayıcısı değişti: {provider}")
    
    def _on_api_keys_updated(self, keys: dict) -> None:
        """API anahtarları güncellendiğinde"""
        from src.translate.providers import TranslationProvider
        provider_map = {
            "chatgpt": TranslationProvider.CHATGPT,
            "gemini": TranslationProvider.GEMINI,
            "google": TranslationProvider.GOOGLE,
            "deepl": TranslationProvider.DEEPL
        }
        for name, key in keys.items():
            if key and name in provider_map:
                self.translation_engine.set_api_key(provider_map[name], key)
        
        # Config'e kaydet
        self.config.translation.api_keys = keys
        self.config_manager.save(self.config)
        logger.info("API anahtarları kaydedildi")
    
    def run(self) -> int:
        """Uygulamayı çalıştırır"""
        self.main_window.show()
        return self.app.exec()


def main():
    """Ana fonksiyon"""
    app = ChwiliTranslateApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
