"""
OCR Control Panel for ChwiliTranslate
OCR ayarları ve bölge seçimi - Çoklu bölge desteği
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSlider, QCheckBox, QPushButton, QFrame, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox, QLineEdit,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class RegionItemWidget(QWidget):
    """Tek bir bölge için özel widget"""
    
    enabled_changed = pyqtSignal(int, bool)
    name_changed = pyqtSignal(int, str)
    clicked = pyqtSignal(int)  # Tıklama sinyali
    
    def __init__(self, index: int, name: str, width: int, height: int, enabled: bool = True):
        super().__init__()
        self._index = index
        self._selected = False
        self._setup_ui(name, width, height, enabled)
    
    def _setup_ui(self, name: str, width: int, height: int, enabled: bool) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Checkbox
        self._checkbox = QCheckBox()
        self._checkbox.setChecked(enabled)
        self._checkbox.toggled.connect(lambda checked: self.enabled_changed.emit(self._index, checked))
        layout.addWidget(self._checkbox)
        
        # İsim (düzenlenebilir)
        self._name_edit = QLineEdit(name)
        self._name_edit.setFixedWidth(120)
        self._name_edit.setPlaceholderText("Bölge adı")
        self._name_edit.editingFinished.connect(self._on_name_changed)
        layout.addWidget(self._name_edit)
        
        # Boyut bilgisi
        self._size_label = QLabel(f"({width}x{height})")
        self._size_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(self._size_label)
        
        layout.addStretch()
        
        # Cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._apply_style()
    
    def mousePressEvent(self, event):
        """Tıklama olayı"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Input alanına tıklanmadıysa seçim yap
            child = self.childAt(event.pos())
            if not isinstance(child, QLineEdit):
                self.clicked.emit(self._index)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool) -> None:
        """Seçim durumunu ayarla"""
        self._selected = selected
        self._update_selection_style()
    
    def is_selected(self) -> bool:
        return self._selected
    
    def _update_selection_style(self) -> None:
        """Seçim stilini güncelle"""
        if self._selected:
            self.parent().setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(0, 212, 255, 0.25),
                        stop:1 rgba(0, 180, 220, 0.15));
                    border: 2px solid rgba(0, 212, 255, 0.6);
                    border-radius: 10px;
                }
            """)
        else:
            self.parent().setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(40, 40, 60, 0.5),
                        stop:1 rgba(30, 30, 50, 0.7));
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 10px;
                }
                QFrame:hover {
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(50, 50, 70, 0.6),
                        stop:1 rgba(40, 40, 60, 0.8));
                }
            """)
    
    def _apply_style(self) -> None:
        self._name_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 5px 8px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #00d4ff;
                background: rgba(0, 212, 255, 0.1);
            }
            QLineEdit:hover {
                border: 1px solid rgba(0, 212, 255, 0.5);
            }
        """)
        
        self._checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid rgba(255, 255, 255, 0.25);
                background: rgba(0, 0, 0, 0.3);
            }
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #34d399,
                    stop:1 #10b981);
                border: 2px solid #10b981;
            }
            QCheckBox::indicator:unchecked:hover {
                border: 2px solid rgba(52, 211, 153, 0.5);
                background: rgba(52, 211, 153, 0.1);
            }
        """)
    
    def _on_name_changed(self) -> None:
        self.name_changed.emit(self._index, self._name_edit.text())
    
    def set_checked(self, checked: bool) -> None:
        self._checkbox.blockSignals(True)
        self._checkbox.setChecked(checked)
        self._checkbox.blockSignals(False)
    
    def get_name(self) -> str:
        return self._name_edit.text()


class OCRControlPanel(QWidget):
    """OCR Control paneli"""
    
    # Sinyaller
    speed_changed = pyqtSignal(str)
    accuracy_changed = pyqtSignal(float)
    gpu_changed = pyqtSignal(bool)
    select_region_clicked = pyqtSignal()
    add_region_clicked = pyqtSignal()  # Yeni bölge ekle
    edit_region_clicked = pyqtSignal(int)  # Bölge düzenle (index)
    remove_region_clicked = pyqtSignal(int)  # Bölge sil (index)
    region_enabled_changed = pyqtSignal(int, bool)  # Bölge aktiflik değişti
    region_name_changed = pyqtSignal(int, str)  # Bölge ismi değişti
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_RED = "#ef4444"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self):
        super().__init__()
        self._regions = []  # Bölge listesi
        self._updating_list = False  # Liste güncellenirken sinyal engelleme
        self._selected_index = -1  # Seçili bölge indeksi
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        """UI bileşenlerini oluşturur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("OCR Control")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # OCR Ayarları kartı
        ocr_card = self._create_ocr_settings_card()
        layout.addWidget(ocr_card)
        
        # Çoklu Region seçimi kartı
        region_card = self._create_multi_region_card()
        layout.addWidget(region_card)
        
        layout.addStretch()
    
    def _create_ocr_settings_card(self) -> QFrame:
        """OCR ayarları kartını oluşturur"""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Kart başlığı
        header = QLabel("⚡ OCR Ayarları")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # OCR Speed
        speed_layout = QHBoxLayout()
        speed_label = QLabel("OCR Hızı:")
        self._speed_combo = QComboBox()
        self._speed_combo.addItems(["Fast", "Normal", "Accurate"])
        self._speed_combo.setCurrentText("Normal")
        self._speed_combo.currentTextChanged.connect(self.speed_changed.emit)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self._speed_combo, 1)
        layout.addLayout(speed_layout)
        
        # Accuracy slider
        accuracy_layout = QVBoxLayout()
        accuracy_header = QHBoxLayout()
        accuracy_label = QLabel("Doğruluk Eşiği:")
        self._accuracy_value = QLabel("70%")
        accuracy_header.addWidget(accuracy_label)
        accuracy_header.addWidget(self._accuracy_value)
        accuracy_layout.addLayout(accuracy_header)
        
        self._accuracy_slider = QSlider(Qt.Orientation.Horizontal)
        self._accuracy_slider.setRange(0, 100)
        self._accuracy_slider.setValue(70)
        self._accuracy_slider.valueChanged.connect(self._on_accuracy_changed)
        accuracy_layout.addWidget(self._accuracy_slider)
        layout.addLayout(accuracy_layout)
        
        # GPU Acceleration
        self._gpu_checkbox = QCheckBox("GPU Hızlandırma (CUDA)")
        self._gpu_checkbox.setChecked(True)
        self._gpu_checkbox.toggled.connect(self.gpu_changed.emit)
        layout.addWidget(self._gpu_checkbox)
        
        return card

    
    def _create_multi_region_card(self) -> QFrame:
        """Çoklu region seçimi kartını oluşturur"""
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        # Kart başlığı
        header_layout = QHBoxLayout()
        header = QLabel("📷 OCR Bölgeleri")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        header_layout.addWidget(header)
        
        self._region_count_label = QLabel("(0/5)")
        self._region_count_label.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        header_layout.addWidget(self._region_count_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Bölge listesi container
        self._region_container = QWidget()
        self._region_layout = QVBoxLayout(self._region_container)
        self._region_layout.setContentsMargins(0, 0, 0, 0)
        self._region_layout.setSpacing(6)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(self._region_container)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(170)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 25, 0.8),
                    stop:1 rgba(10, 10, 18, 0.9));
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 0.03);
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0, 212, 255, 0.4);
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(0, 212, 255, 0.6);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        layout.addWidget(scroll)
        
        # Bölge widget'larını tutacak liste
        self._region_widgets: list = []
        
        # Boş durum mesajı
        self._empty_label = QLabel("Henüz bölge eklenmedi")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; padding: 30px;")
        self._region_layout.addWidget(self._empty_label)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        # Yeni bölge ekle
        self._add_btn = QPushButton("➕ Bölge Ekle")
        self._add_btn.setFixedHeight(42)
        self._add_btn.setObjectName("addBtn")
        self._add_btn.clicked.connect(self._on_add_region)
        btn_layout.addWidget(self._add_btn)
        
        # Düzenle
        self._edit_btn = QPushButton("✏️ Düzenle")
        self._edit_btn.setFixedHeight(42)
        self._edit_btn.setObjectName("editBtn")
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._on_edit_region)
        btn_layout.addWidget(self._edit_btn)
        
        # Sil
        self._remove_btn = QPushButton("🗑️ Sil")
        self._remove_btn.setFixedHeight(42)
        self._remove_btn.setEnabled(False)
        self._remove_btn.setObjectName("removeBtn")
        self._remove_btn.clicked.connect(self._on_remove_region)
        btn_layout.addWidget(self._remove_btn)
        
        layout.addLayout(btn_layout)
        
        # Eski tek bölge seçimi için geriye uyumluluk
        self._select_btn = QPushButton("🎯 Hızlı Bölge Seç")
        self._select_btn.setFixedHeight(40)
        self._select_btn.setToolTip("Tek bölge seçmek için (mevcut bölgeleri temizler)")
        self._select_btn.clicked.connect(self.select_region_clicked.emit)
        self._select_btn.setVisible(False)  # Varsayılan gizli
        layout.addWidget(self._select_btn)
        
        # Preview alanı
        self._preview_frame = QFrame()
        self._preview_frame.setFixedHeight(130)
        self._preview_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(15, 15, 25, 0.6),
                    stop:1 rgba(10, 10, 18, 0.8));
                border: 2px dashed rgba(0, 212, 255, 0.25);
                border-radius: 12px;
            }
            QFrame:hover {
                border: 2px dashed rgba(0, 212, 255, 0.45);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 212, 255, 0.05),
                    stop:1 rgba(10, 10, 18, 0.8));
            }
        """)
        preview_layout = QVBoxLayout(self._preview_frame)
        self._preview_label = QLabel("Bölge seçin")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        self._preview_label.setScaledContents(True)
        preview_layout.addWidget(self._preview_label)
        layout.addWidget(self._preview_frame)
        
        return card
    
    def _on_add_region(self) -> None:
        """Yeni bölge ekle butonuna tıklandı"""
        if len(self._regions) >= 5:
            QMessageBox.warning(self, "Limit", "Maksimum 5 bölge ekleyebilirsiniz.")
            return
        self.add_region_clicked.emit()
    
    def _on_edit_region(self) -> None:
        """Düzenle butonuna tıklandı"""
        if self._selected_index >= 0:
            self.edit_region_clicked.emit(self._selected_index)
    
    def _on_remove_region(self) -> None:
        """Sil butonuna tıklandı"""
        if self._selected_index >= 0:
            self.remove_region_clicked.emit(self._selected_index)
            self._selected_index = -1  # Seçimi temizle
    
    def _get_selected_index(self) -> int:
        """Seçili bölge indeksini döndürür"""
        return self._selected_index
    
    def _on_region_clicked(self, index: int) -> None:
        """Bölgeye tıklandı - seçimi güncelle"""
        # Önceki seçimi kaldır
        for i, (frame, widget) in enumerate(self._region_items):
            widget.set_selected(i == index)
        
        self._selected_index = index
        self._edit_btn.setEnabled(True)
        self._remove_btn.setEnabled(True)
    
    def _on_region_enabled(self, index: int, enabled: bool) -> None:
        """Bölge aktifliği değişti"""
        self.region_enabled_changed.emit(index, enabled)
    
    def _on_region_name(self, index: int, name: str) -> None:
        """Bölge ismi değişti"""
        self.region_name_changed.emit(index, name)
    
    def _on_accuracy_changed(self, value: int) -> None:
        """Accuracy slider değiştiğinde"""
        self._accuracy_value.setText(f"{value}%")
        self.accuracy_changed.emit(value / 100.0)
    
    def _apply_styles(self) -> None:
        """Stilleri uygular - Mor/Siyah gradient tasarım"""
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
                border-radius: 16px;
                padding: 18px;
            }}
            
            QComboBox {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(35, 18, 55, 0.8),
                    stop:1 rgba(20, 10, 35, 0.9));
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 10px;
                padding: 10px 14px;
                color: {self.TEXT_PRIMARY};
                min-width: 140px;
                font-size: 13px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {self.ACCENT_PURPLE};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(168, 85, 247, 0.2),
                    stop:1 rgba(20, 10, 35, 0.9));
            }}
            
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: rgba(15, 8, 25, 0.98);
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 8px;
                selection-background-color: rgba(168, 85, 247, 0.35);
                color: {self.TEXT_PRIMARY};
                padding: 5px;
            }}
            
            QLineEdit {{
                background: rgba(25, 12, 40, 0.8);
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 8px;
                padding: 8px;
                color: {self.TEXT_PRIMARY};
            }}
            
            QSlider::groove:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(168, 85, 247, 0.15),
                    stop:1 rgba(139, 92, 246, 0.2));
                height: 8px;
                border-radius: 4px;
            }}
            
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c084fc,
                    stop:1 #a855f7);
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }}
            
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d8b4fe,
                    stop:1 #c084fc);
                border: 2px solid rgba(255, 255, 255, 0.4);
            }}
            
            QSlider::sub-page:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a855f7,
                    stop:1 #8b5cf6);
                border-radius: 4px;
            }}
            
            QCheckBox {{
                color: {self.TEXT_PRIMARY};
                spacing: 12px;
                font-size: 13px;
                background: transparent;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid rgba(168, 85, 247, 0.3);
                background: rgba(168, 85, 247, 0.08);
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid rgba(168, 85, 247, 0.6);
                background: rgba(168, 85, 247, 0.15);
            }}
            
            QCheckBox::indicator:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #c084fc,
                    stop:1 #a855f7);
                border: 2px solid #a855f7;
            }}
            
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a855f7,
                    stop:1 #8b5cf6);
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 16px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c084fc,
                    stop:1 #a855f7);
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9333ea,
                    stop:1 #7c3aed);
            }}
            
            QPushButton:disabled {{
                background: rgba(168, 85, 247, 0.15);
                color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(168, 85, 247, 0.1);
            }}
            
            #removeBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff6b6b,
                    stop:1 #ee5a5a);
            }}
            
            #removeBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff8585,
                    stop:1 #ff6b6b);
            }}
            
            #removeBtn:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc4c4c,
                    stop:1 #c43c3c);
            }}
            
            #editBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d946ef,
                    stop:1 #c026d3);
            }}
            
            #editBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e879f9,
                    stop:1 #d946ef);
            }}
            
            #editBtn:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c3aed,
                    stop:1 #6d28d9);
            }}
            
            #addBtn {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399,
                    stop:1 #10b981);
            }}
            
            #addBtn:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6ee7b7,
                    stop:1 #34d399);
            }}
            
            #addBtn:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669,
                    stop:1 #047857);
            }}
        """)
    
    # Getter/Setter metodları
    def get_speed(self) -> str:
        return self._speed_combo.currentText().lower()
    
    def set_speed(self, speed: str) -> None:
        self._speed_combo.setCurrentText(speed.capitalize())
    
    def get_accuracy(self) -> float:
        return self._accuracy_slider.value() / 100.0
    
    def set_accuracy(self, value: float) -> None:
        self._accuracy_slider.setValue(int(value * 100))
    
    def is_gpu_enabled(self) -> bool:
        return self._gpu_checkbox.isChecked()
    
    def set_gpu_enabled(self, enabled: bool) -> None:
        self._gpu_checkbox.setChecked(enabled)
    
    # Çoklu bölge metodları
    def set_regions(self, regions: list) -> None:
        """Bölge listesini günceller"""
        self._updating_list = True
        self._regions = regions
        self._selected_index = -1
        
        # Eski widget'ları temizle
        for widget in self._region_widgets:
            widget.deleteLater()
        self._region_widgets.clear()
        
        # Region items listesi (frame, widget) tuple
        self._region_items = []
        
        # Boş mesajı göster/gizle
        self._empty_label.setVisible(len(regions) == 0)
        
        # Yeni widget'ları oluştur
        for i, region in enumerate(regions):
            name = region.name if hasattr(region, 'name') and region.name else f"Bölge {i + 1}"
            width = region.width if hasattr(region, 'width') else 0
            height = region.height if hasattr(region, 'height') else 0
            enabled = region.enabled if hasattr(region, 'enabled') else True
            
            # Bölge item widget'ı
            item_frame = QFrame()
            item_frame.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(40, 40, 60, 0.5),
                        stop:1 rgba(30, 30, 50, 0.7));
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 10px;
                }
                QFrame:hover {
                    border: 1px solid rgba(0, 212, 255, 0.3);
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(50, 50, 70, 0.6),
                        stop:1 rgba(40, 40, 60, 0.8));
                }
            """)
            
            item_widget = RegionItemWidget(i, name, width, height, enabled)
            item_widget.enabled_changed.connect(self._on_region_enabled)
            item_widget.name_changed.connect(self._on_region_name)
            item_widget.clicked.connect(self._on_region_clicked)
            
            frame_layout = QVBoxLayout(item_frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.addWidget(item_widget)
            
            self._region_layout.addWidget(item_frame)
            self._region_widgets.append(item_frame)
            self._region_items.append((item_frame, item_widget))
        
        self._region_count_label.setText(f"({len(regions)}/5)")
        self._add_btn.setEnabled(len(regions) < 5)
        self._edit_btn.setEnabled(False)  # Seçim yapılana kadar devre dışı
        self._remove_btn.setEnabled(False)
        self._updating_list = False
    
    def get_selected_region_index(self) -> int:
        """Seçili bölge indeksini döndürür"""
        return self._get_selected_index()
    
    # Geriye uyumluluk
    def set_region_info(self, x: int, y: int, w: int, h: int) -> None:
        """Eski tek bölge bilgisi (geriye uyumluluk)"""
        pass  # Artık set_regions kullanılıyor
    
    def set_preview_image(self, image_data: bytes) -> None:
        """Önizleme görüntüsünü ayarlar"""
        from PyQt6.QtGui import QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        scaled = pixmap.scaled(
            self._preview_frame.width() - 20,
            self._preview_frame.height() - 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self._preview_label.setPixmap(scaled)
