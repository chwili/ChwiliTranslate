"""
Overlay Window for ChwiliTranslate
Click-through overlay penceresi
"""

from dataclasses import dataclass, field
from typing import Optional
import sys


@dataclass
class OverlayConfig:
    """Overlay konfigürasyonu"""
    opacity: float = 0.85
    font_size: int = 24
    font_family: str = "Segoe UI"
    background_enabled: bool = True
    glow_effect: bool = False
    position_x: int = 100
    position_y: int = 100
    text_color: str = "#ffffff"
    bg_color: str = "#000000"
    glow_color: str = "#00d4ff"


class OverlayWindow:
    """Sürüklenebilir overlay penceresi"""
    
    def __init__(self, config: Optional[OverlayConfig] = None):
        self._config = config or OverlayConfig()
        self._text = ""
        self._visible = False
        self._widget = None
        self._pyqt_available = False
        self._bold = False
        self._italic = False
        self._text_shadow = True
        self._bg_enabled = True
        self._glow_enabled = False
        self._text_color = "#ffffff"
        self._bg_color = "#000000"
        self._glow_color = "#00d4ff"
        self._pending_text = None  # Thread-safe text update
        self._position_changed_callback = None  # Konum değişikliği callback'i
        
        try:
            from PyQt6.QtWidgets import QWidget
            self._pyqt_available = True
        except ImportError:
            self._pyqt_available = False
    
    def on_position_changed(self, callback) -> None:
        """Konum değişikliği callback'i ayarlar"""
        self._position_changed_callback = callback
    
    def _ensure_widget(self) -> None:
        if not self._pyqt_available or self._widget is not None:
            return
        
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
        from PyQt6.QtCore import Qt, QPoint, QTimer
        from PyQt6.QtGui import QFont, QFontMetrics
        
        app = QApplication.instance()
        if app is None:
            return
        
        parent = self
        
        class DraggableOverlay(QWidget):
            def __init__(self, overlay_parent):
                super().__init__()
                self._overlay = overlay_parent
                self._drag_pos = None
                
                # Timer for thread-safe text updates
                self._update_timer = QTimer(self)
                self._update_timer.timeout.connect(self._check_pending_text)
                self._update_timer.start(50)  # Check every 50ms
            
            def _check_pending_text(self):
                if self._overlay._pending_text is not None:
                    text = self._overlay._pending_text
                    self._overlay._pending_text = None
                    self._overlay._do_set_text(text)
            
            def mousePressEvent(self, event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            
            def mouseMoveEvent(self, event):
                if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
                    new_pos = event.globalPosition().toPoint() - self._drag_pos
                    self.move(new_pos)
                    self._overlay._config.position_x = new_pos.x()
                    self._overlay._config.position_y = new_pos.y()
            
            def mouseReleaseEvent(self, event):
                self._drag_pos = None
                # Sürükleme bittiğinde callback'i çağır
                if self._overlay._position_changed_callback:
                    self._overlay._position_changed_callback(
                        self._overlay._config.position_x,
                        self._overlay._config.position_y
                    )
        
        self._widget = DraggableOverlay(self)
        self._widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self._widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._widget.setCursor(Qt.CursorShape.SizeAllCursor)
        
        self._label = QLabel()
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        self._widget.setLayout(layout)
        
        self._apply_style()
    
    def _apply_style(self) -> None:
        if not self._widget or not hasattr(self, '_label'):
            return
        
        from PyQt6.QtGui import QFont
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        
        font = QFont(self._config.font_family, self._config.font_size)
        font.setBold(self._bold)
        font.setItalic(self._italic)
        self._label.setFont(font)
        
        # Arka plan stili
        if self._bg_enabled:
            # Hex rengi rgba'ya çevir
            bg_color = QColor(self._bg_color)
            bg = f"background: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, 0.75); border-radius: 12px; padding: 15px;"
        else:
            bg = "background: transparent; padding: 5px;"
        
        self._label.setStyleSheet(f"""
            QLabel {{
                color: {self._text_color};
                {bg}
            }}
        """)
        
        # Efekt seçimi: Glow > Shadow > None
        if self._glow_enabled:
            # Neon glow efekti
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(20)
            glow.setColor(QColor(self._glow_color))
            glow.setOffset(0, 0)
            self._label.setGraphicsEffect(glow)
        elif self._text_shadow:
            # Normal gölge
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 200))
            shadow.setOffset(2, 2)
            self._label.setGraphicsEffect(shadow)
        else:
            self._label.setGraphicsEffect(None)
        
        self._widget.setWindowOpacity(self._config.opacity)
        self._adjust_size()
    
    def _adjust_size(self) -> None:
        """Pencere boyutunu yazıya göre ayarla"""
        if not self._widget or not self._label:
            return
        
        from PyQt6.QtGui import QFontMetrics
        from PyQt6.QtCore import QSize
        
        fm = QFontMetrics(self._label.font())
        text = self._text or "Çeviri bekleniyor..."
        
        # Maksimum genişlik
        max_width = 800
        
        # Metin boyutunu hesapla
        rect = fm.boundingRect(0, 0, max_width, 0, 
            self._label.alignment() | 0x1000,  # WordWrap
            text)
        
        padding = 40 if self._bg_enabled else 20
        width = min(rect.width() + padding, max_width)
        height = rect.height() + padding
        
        self._widget.setFixedSize(width, height)
        self._widget.move(self._config.position_x, self._config.position_y)
    
    # Ayar metodları
    def set_opacity(self, opacity: float) -> None:
        self._config.opacity = max(0.1, min(1.0, opacity))
        if self._widget:
            self._widget.setWindowOpacity(self._config.opacity)
    
    def get_opacity(self) -> float:
        return self._config.opacity
    
    def set_font_size(self, size: int) -> None:
        self._config.font_size = max(10, min(72, size))
        self._apply_style()
    
    def get_font_size(self) -> int:
        return self._config.font_size
    
    def set_font_family(self, family: str) -> None:
        self._config.font_family = family
        self._apply_style()
    
    def get_font_family(self) -> str:
        return self._config.font_family
    
    def set_position(self, x: int, y: int) -> None:
        self._config.position_x = x
        self._config.position_y = y
        if self._widget:
            self._widget.move(x, y)
    
    def get_position(self) -> tuple:
        return (self._config.position_x, self._config.position_y)
    
    def set_background_blur(self, enabled: bool) -> None:
        self._bg_enabled = enabled
        self._apply_style()
    
    def get_background_blur(self) -> bool:
        return self._bg_enabled
    
    def set_glow_effect(self, enabled: bool) -> None:
        self._glow_enabled = enabled
        self._config.glow_effect = enabled
        self._apply_style()
    
    def set_text_color(self, color: str) -> None:
        self._text_color = color
        self._config.text_color = color
        self._apply_style()
    
    def set_bg_color(self, color: str) -> None:
        self._bg_color = color
        self._config.bg_color = color
        self._apply_style()
    
    def set_glow_color(self, color: str) -> None:
        self._glow_color = color
        self._config.glow_color = color
        self._apply_style()
    
    def set_bold(self, enabled: bool) -> None:
        self._bold = enabled
        self._apply_style()
    
    def set_italic(self, enabled: bool) -> None:
        self._italic = enabled
        self._apply_style()
    
    def set_text_shadow(self, enabled: bool) -> None:
        self._text_shadow = enabled
        self._apply_style()
    
    def set_text(self, text: str) -> None:
        """Thread-safe text update"""
        self._text = text
        self._pending_text = text  # Timer will pick this up
    
    def _do_set_text(self, text: str) -> None:
        """Actually update the text (called from UI thread)"""
        if self._widget and hasattr(self, '_label'):
            self._label.setText(text)
            self._adjust_size()
    
    def get_text(self) -> str:
        return self._text
    
    def show_overlay(self) -> None:
        self._visible = True
        self._ensure_widget()
        if self._widget:
            self._widget.show()
    
    def hide_overlay(self) -> None:
        self._visible = False
        if self._widget:
            self._widget.hide()
    
    def is_visible(self) -> bool:
        return self._visible
    
    def get_config(self) -> OverlayConfig:
        return OverlayConfig(
            opacity=self._config.opacity,
            font_size=self._config.font_size,
            font_family=self._config.font_family,
            background_enabled=self._bg_enabled,
            glow_effect=self._glow_enabled,
            position_x=self._config.position_x,
            position_y=self._config.position_y,
            text_color=self._text_color,
            bg_color=self._bg_color,
            glow_color=self._glow_color
        )
