"""
Settings Panel for ChwiliTranslate
Sistem ayarları
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QPushButton, QFrame, QListWidget, QListWidgetItem,
    QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QScreen
from typing import List, Dict


class SettingsPanel(QWidget):
    """Sistem ayarları paneli"""
    
    # Sinyaller
    cache_changed = pyqtSignal(bool)
    gpu_changed = pyqtSignal(bool)
    monitor_changed = pyqtSignal(int)
    exclusion_areas_changed = pyqtSignal(list)
    clear_cache_clicked = pyqtSignal()
    add_exclusion_clicked = pyqtSignal()  # Region selector açmak için
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_RED = "#ef4444"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self):
        super().__init__()
        self._exclusion_areas: List[Dict] = []
        self._setup_ui()
        self._apply_styles()
        self._detect_monitors()
    
    def _detect_monitors(self) -> None:
        """Sistemdeki monitörleri algılar"""
        self._monitor_combo.clear()
        app = QApplication.instance()
        if app:
            screens = app.screens()
            for i, screen in enumerate(screens):
                geo = screen.geometry()
                name = f"Monitör {i + 1} ({geo.width()}x{geo.height()})"
                self._monitor_combo.addItem(name, i)
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        title = QLabel("Ayarlar")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Sistem kartı
        system_card = self._create_system_card()
        layout.addWidget(system_card)
        
        # Cache kartı
        cache_card = self._create_cache_card()
        layout.addWidget(cache_card)
        
        # Exclusion areas kartı
        exclusion_card = self._create_exclusion_card()
        layout.addWidget(exclusion_card)
        
        layout.addStretch()
    
    def _create_system_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("⚙️ Sistem")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # GPU
        self._gpu_checkbox = QCheckBox("GPU Hızlandırma (CUDA)")
        self._gpu_checkbox.setChecked(True)
        self._gpu_checkbox.toggled.connect(self.gpu_changed.emit)
        layout.addWidget(self._gpu_checkbox)
        
        # Monitor seçimi
        monitor_layout = QHBoxLayout()
        monitor_label = QLabel("Monitör:")
        self._monitor_combo = QComboBox()
        self._monitor_combo.currentIndexChanged.connect(
            lambda i: self.monitor_changed.emit(self._monitor_combo.itemData(i) or 0)
        )
        monitor_layout.addWidget(monitor_label)
        monitor_layout.addWidget(self._monitor_combo, 1)
        layout.addLayout(monitor_layout)
        
        # Monitörleri yenile butonu
        refresh_btn = QPushButton("🔄 Monitörleri Yenile")
        refresh_btn.clicked.connect(self._detect_monitors)
        layout.addWidget(refresh_btn)
        
        return card
    
    def _create_cache_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("💾 Önbellek")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        self._cache_checkbox = QCheckBox("Önbellek Aktif")
        self._cache_checkbox.setChecked(True)
        self._cache_checkbox.toggled.connect(self.cache_changed.emit)
        layout.addWidget(self._cache_checkbox)
        
        self._cache_info = QLabel("Önbellek: 0 giriş")
        self._cache_info.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        layout.addWidget(self._cache_info)
        
        # Temizlendi mesajı (gizli)
        self._cache_cleared_label = QLabel("✅ Önbellek temizlendi!")
        self._cache_cleared_label.setStyleSheet("color: #22c55e; font-weight: bold;")
        self._cache_cleared_label.hide()
        layout.addWidget(self._cache_cleared_label)
        
        self._clear_cache_btn = QPushButton("🗑️ Önbelleği Temizle")
        self._clear_cache_btn.setObjectName("dangerButton")
        self._clear_cache_btn.clicked.connect(self._on_clear_cache)
        layout.addWidget(self._clear_cache_btn)
        
        return card

    
    def _create_exclusion_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("🚫 Hariç Tutulan Alanlar")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        desc = QLabel("OCR taramasından hariç tutulacak ekran bölgeleri")
        desc.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        layout.addWidget(desc)
        
        self._exclusion_list = QListWidget()
        self._exclusion_list.setMaximumHeight(120)
        layout.addWidget(self._exclusion_list)
        
        btn_layout = QHBoxLayout()
        self._add_exclusion_btn = QPushButton("➕ Alan Ekle")
        self._add_exclusion_btn.clicked.connect(self._on_add_exclusion)
        self._remove_exclusion_btn = QPushButton("➖ Seçileni Kaldır")
        self._remove_exclusion_btn.clicked.connect(self._remove_exclusion_area)
        btn_layout.addWidget(self._add_exclusion_btn)
        btn_layout.addWidget(self._remove_exclusion_btn)
        layout.addLayout(btn_layout)
        
        return card
    
    def _on_add_exclusion(self) -> None:
        """Alan ekle butonuna tıklandığında"""
        self.add_exclusion_clicked.emit()
    
    def _on_clear_cache(self) -> None:
        """Önbelleği temizle butonuna tıklandığında"""
        self.clear_cache_clicked.emit()
        self._cache_info.setText("Önbellek: 0 giriş")
        self._cache_cleared_label.show()
        # 3 saniye sonra mesajı gizle
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, self._cache_cleared_label.hide)
    
    def add_exclusion_area(self, x: int, y: int, w: int, h: int) -> None:
        """Yeni hariç tutulan alan ekler"""
        area = {"x": x, "y": y, "width": w, "height": h}
        self._exclusion_areas.append(area)
        self._update_exclusion_list()
        self.exclusion_areas_changed.emit(self._exclusion_areas)
    
    def _remove_exclusion_area(self) -> None:
        current = self._exclusion_list.currentRow()
        if current >= 0 and current < len(self._exclusion_areas):
            self._exclusion_areas.pop(current)
            self._update_exclusion_list()
            self.exclusion_areas_changed.emit(self._exclusion_areas)
    
    def _update_exclusion_list(self) -> None:
        self._exclusion_list.clear()
        for i, area in enumerate(self._exclusion_areas):
            item = QListWidgetItem(
                f"Alan {i+1}: ({area['x']}, {area['y']}) - {area['width']}x{area['height']}"
            )
            self._exclusion_list.addItem(item)
    
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
            QComboBox {{
                background: rgba(35, 18, 55, 0.7);
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 8px;
                padding: 8px;
                color: {self.TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(15, 8, 25, 0.98);
                border: 1px solid rgba(168, 85, 247, 0.25);
                selection-background-color: rgba(168, 85, 247, 0.35);
                color: {self.TEXT_PRIMARY};
            }}
            QPushButton {{
                background: rgba(35, 18, 55, 0.7);
                color: {self.TEXT_PRIMARY};
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 8px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background: rgba(168, 85, 247, 0.25);
                border-color: {self.ACCENT_PURPLE};
            }}
            #dangerButton {{
                background-color: rgba(239, 68, 68, 0.15);
                border-color: {self.ACCENT_RED};
                color: {self.ACCENT_RED};
            }}
            #dangerButton:hover {{
                background-color: rgba(239, 68, 68, 0.25);
            }}
            QListWidget {{
                background: rgba(12, 6, 20, 0.7);
                border: 1px solid rgba(168, 85, 247, 0.15);
                border-radius: 8px;
                color: {self.TEXT_PRIMARY};
            }}
        """)
    
    # Getter/Setter
    def is_cache_enabled(self) -> bool:
        return self._cache_checkbox.isChecked()
    
    def set_cache_enabled(self, enabled: bool) -> None:
        self._cache_checkbox.setChecked(enabled)
    
    def is_gpu_enabled(self) -> bool:
        return self._gpu_checkbox.isChecked()
    
    def set_gpu_enabled(self, enabled: bool) -> None:
        self._gpu_checkbox.setChecked(enabled)
    
    def get_selected_monitor(self) -> int:
        return self._monitor_combo.currentData() or 0
    
    def set_cache_info(self, count: int) -> None:
        self._cache_info.setText(f"Önbellek: {count} giriş")
    
    def get_exclusion_areas(self) -> List[Dict]:
        return self._exclusion_areas.copy()
    
    def set_exclusion_areas(self, areas: List[Dict]) -> None:
        self._exclusion_areas = areas.copy()
        self._update_exclusion_list()
