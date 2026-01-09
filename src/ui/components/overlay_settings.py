"""
Overlay Settings Panel for ChwiliTranslate
Overlay görünüm ayarları
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QSpinBox, QComboBox, QFrame, QCheckBox, QPushButton,
    QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor


class ColorButton(QPushButton):
    """Renk seçici buton"""
    color_changed = pyqtSignal(str)
    
    def __init__(self, initial_color: str = "#ffffff"):
        super().__init__()
        self._color = initial_color
        self.setFixedSize(40, 30)
        self._update_style()
        self.clicked.connect(self._pick_color)
    
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self._color};
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border-color: #00d4ff;
            }}
        """)
    
    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Renk Seç")
        if color.isValid():
            self._color = color.name()
            self._update_style()
            self.color_changed.emit(self._color)
    
    def get_color(self) -> str:
        return self._color
    
    def set_color(self, color: str):
        self._color = color
        self._update_style()


class OverlaySettingsPanel(QWidget):
    """Overlay ayarları paneli"""
    
    # Sinyaller
    opacity_changed = pyqtSignal(float)
    font_size_changed = pyqtSignal(int)
    font_family_changed = pyqtSignal(str)
    position_changed = pyqtSignal(int, int)
    blur_changed = pyqtSignal(bool)
    glow_changed = pyqtSignal(bool)
    bold_changed = pyqtSignal(bool)
    italic_changed = pyqtSignal(bool)
    shadow_changed = pyqtSignal(bool)
    text_color_changed = pyqtSignal(str)
    bg_color_changed = pyqtSignal(str)
    glow_color_changed = pyqtSignal(str)
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    FONTS = ["Segoe UI", "Arial", "Roboto", "Noto Sans", "Consolas", "Tahoma"]
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title = QLabel("Overlay")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Görünüm kartı
        appearance_card = self._create_appearance_card()
        layout.addWidget(appearance_card)
        
        # Renkler kartı
        colors_card = self._create_colors_card()
        layout.addWidget(colors_card)
        
        # Efektler kartı
        effects_card = self._create_effects_card()
        layout.addWidget(effects_card)
        
        layout.addStretch()
    
    def _create_appearance_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("🎨 Görünüm")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Opacity
        opacity_layout = QVBoxLayout()
        opacity_header = QHBoxLayout()
        opacity_label = QLabel("Saydamlık:")
        self._opacity_value = QLabel("85%")
        opacity_header.addWidget(opacity_label)
        opacity_header.addWidget(self._opacity_value)
        opacity_layout.addLayout(opacity_header)
        
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(10, 100)
        self._opacity_slider.setValue(85)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_layout.addWidget(self._opacity_slider)
        layout.addLayout(opacity_layout)
        
        # Font size
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("Yazı Boyutu:")
        self._font_size_spin = QSpinBox()
        self._font_size_spin.setRange(8, 72)
        self._font_size_spin.setValue(16)
        self._font_size_spin.valueChanged.connect(self.font_size_changed.emit)
        font_size_layout.addWidget(font_size_label)
        font_size_layout.addWidget(self._font_size_spin)
        font_size_layout.addStretch()
        layout.addLayout(font_size_layout)
        
        # Font family
        font_family_layout = QHBoxLayout()
        font_family_label = QLabel("Yazı Tipi:")
        self._font_combo = QComboBox()
        self._font_combo.addItems(self.FONTS)
        self._font_combo.currentTextChanged.connect(self.font_family_changed.emit)
        font_family_layout.addWidget(font_family_label)
        font_family_layout.addWidget(self._font_combo, 1)
        layout.addLayout(font_family_layout)
        
        # Position
        pos_layout = QHBoxLayout()
        pos_label = QLabel("Konum:")
        self._pos_x_spin = QSpinBox()
        self._pos_x_spin.setRange(0, 4000)
        self._pos_x_spin.setValue(100)
        self._pos_x_spin.setPrefix("X: ")
        self._pos_y_spin = QSpinBox()
        self._pos_y_spin.setRange(0, 4000)
        self._pos_y_spin.setValue(100)
        self._pos_y_spin.setPrefix("Y: ")
        self._pos_x_spin.valueChanged.connect(self._on_position_changed)
        self._pos_y_spin.valueChanged.connect(self._on_position_changed)
        pos_layout.addWidget(pos_label)
        pos_layout.addWidget(self._pos_x_spin)
        pos_layout.addWidget(self._pos_y_spin)
        pos_layout.addStretch()
        layout.addLayout(pos_layout)
        
        return card
    
    def _create_colors_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("🎨 Renkler")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Yazı rengi
        text_color_layout = QHBoxLayout()
        text_color_label = QLabel("Yazı Rengi:")
        self._text_color_btn = ColorButton("#ffffff")
        self._text_color_btn.color_changed.connect(self.text_color_changed.emit)
        text_color_layout.addWidget(text_color_label)
        text_color_layout.addWidget(self._text_color_btn)
        text_color_layout.addStretch()
        layout.addLayout(text_color_layout)
        
        # Arka plan rengi
        bg_color_layout = QHBoxLayout()
        bg_color_label = QLabel("Arka Plan Rengi:")
        self._bg_color_btn = ColorButton("#000000")
        self._bg_color_btn.color_changed.connect(self.bg_color_changed.emit)
        bg_color_layout.addWidget(bg_color_label)
        bg_color_layout.addWidget(self._bg_color_btn)
        bg_color_layout.addStretch()
        layout.addLayout(bg_color_layout)
        
        # Glow rengi
        glow_color_layout = QHBoxLayout()
        glow_color_label = QLabel("Glow Rengi:")
        self._glow_color_btn = ColorButton("#00d4ff")
        self._glow_color_btn.color_changed.connect(self.glow_color_changed.emit)
        glow_color_layout.addWidget(glow_color_label)
        glow_color_layout.addWidget(self._glow_color_btn)
        glow_color_layout.addStretch()
        layout.addLayout(glow_color_layout)
        
        return card

    
    def _create_effects_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("✨ Efektler")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        self._bg_checkbox = QCheckBox("Arka Plan (Kutu)")
        self._bg_checkbox.setChecked(True)
        self._bg_checkbox.toggled.connect(self.blur_changed.emit)
        layout.addWidget(self._bg_checkbox)
        
        self._glow_checkbox = QCheckBox("Neon Glow Efekti")
        self._glow_checkbox.setChecked(False)
        self._glow_checkbox.toggled.connect(self.glow_changed.emit)
        layout.addWidget(self._glow_checkbox)
        
        self._shadow_checkbox = QCheckBox("Yazı Gölgesi")
        self._shadow_checkbox.setChecked(True)
        self._shadow_checkbox.toggled.connect(self.shadow_changed.emit)
        layout.addWidget(self._shadow_checkbox)
        
        # Yazı stilleri
        style_header = QLabel("📝 Yazı Stili")
        style_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(style_header)
        
        style_layout = QHBoxLayout()
        
        self._bold_checkbox = QCheckBox("Kalın")
        self._bold_checkbox.setChecked(False)
        self._bold_checkbox.toggled.connect(self.bold_changed.emit)
        style_layout.addWidget(self._bold_checkbox)
        
        self._italic_checkbox = QCheckBox("İtalik")
        self._italic_checkbox.setChecked(False)
        self._italic_checkbox.toggled.connect(self.italic_changed.emit)
        style_layout.addWidget(self._italic_checkbox)
        
        style_layout.addStretch()
        layout.addLayout(style_layout)
        
        return card
    
    def _on_opacity_changed(self, value: int) -> None:
        self._opacity_value.setText(f"{value}%")
        self.opacity_changed.emit(value / 100.0)
    
    def _on_position_changed(self) -> None:
        self.position_changed.emit(self._pos_x_spin.value(), self._pos_y_spin.value())
    
    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QLabel {{ 
                color: {self.TEXT_PRIMARY}; 
                background: transparent;
                border: none;
            }}
            #card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(20, 10, 32, 0.95),
                    stop:1 rgba(10, 5, 18, 0.95));
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 15px;
                padding: 15px;
            }}
            QSlider::groove:horizontal {{
                background: rgba(168, 85, 247, 0.15);
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c084fc, stop:1 #a855f7);
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }}
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a855f7, stop:1 #8b5cf6);
                border-radius: 3px;
            }}
            QSpinBox, QComboBox {{
                background: rgba(35, 18, 55, 0.7);
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 8px;
                padding: 6px;
                color: {self.TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(15, 8, 25, 0.98);
                border: 1px solid rgba(168, 85, 247, 0.25);
                selection-background-color: rgba(168, 85, 247, 0.35);
                color: {self.TEXT_PRIMARY};
            }}
            QCheckBox {{
                color: {self.TEXT_PRIMARY};
                spacing: 10px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid rgba(168, 85, 247, 0.3);
            }}
            QCheckBox::indicator:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #c084fc, stop:1 #a855f7);
                border-color: {self.ACCENT_PURPLE};
            }}
        """)
    
    # Getter/Setter
    def get_opacity(self) -> float:
        return self._opacity_slider.value() / 100.0
    
    def set_opacity(self, value: float) -> None:
        self._opacity_slider.setValue(int(value * 100))
    
    def get_font_size(self) -> int:
        return self._font_size_spin.value()
    
    def set_font_size(self, size: int) -> None:
        self._font_size_spin.setValue(size)
    
    def get_font_family(self) -> str:
        return self._font_combo.currentText()
    
    def set_font_family(self, family: str) -> None:
        index = self._font_combo.findText(family)
        if index >= 0:
            self._font_combo.setCurrentIndex(index)
    
    def get_position(self) -> tuple:
        return (self._pos_x_spin.value(), self._pos_y_spin.value())
    
    def set_position(self, x: int, y: int) -> None:
        self._pos_x_spin.setValue(x)
        self._pos_y_spin.setValue(y)
    
    def get_text_color(self) -> str:
        return self._text_color_btn.get_color()
    
    def set_text_color(self, color: str) -> None:
        self._text_color_btn.set_color(color)
    
    def get_bg_color(self) -> str:
        return self._bg_color_btn.get_color()
    
    def set_bg_color(self, color: str) -> None:
        self._bg_color_btn.set_color(color)
    
    def get_glow_color(self) -> str:
        return self._glow_color_btn.get_color()
    
    def set_glow_color(self, color: str) -> None:
        self._glow_color_btn.set_color(color)
    
    def is_blur_enabled(self) -> bool:
        return self._bg_checkbox.isChecked()
    
    def set_blur_enabled(self, enabled: bool) -> None:
        self._bg_checkbox.setChecked(enabled)
    
    def is_glow_enabled(self) -> bool:
        return self._glow_checkbox.isChecked()
    
    def set_glow_enabled(self, enabled: bool) -> None:
        self._glow_checkbox.setChecked(enabled)
    
    def is_shadow_enabled(self) -> bool:
        return self._shadow_checkbox.isChecked()
    
    def set_shadow_enabled(self, enabled: bool) -> None:
        self._shadow_checkbox.setChecked(enabled)
    
    def is_bold_enabled(self) -> bool:
        return self._bold_checkbox.isChecked()
    
    def set_bold_enabled(self, enabled: bool) -> None:
        self._bold_checkbox.setChecked(enabled)
    
    def is_italic_enabled(self) -> bool:
        return self._italic_checkbox.isChecked()
    
    def set_italic_enabled(self, enabled: bool) -> None:
        self._italic_checkbox.setChecked(enabled)
