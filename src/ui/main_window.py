"""
Main Window for ChwiliTranslate
PyQt6 QMainWindow - Dark theme ve glassmorphism stili
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""
    
    # Stil sabitleri - Mor/Siyah Gradient Tema
    DARK_BG = "#0d0d0d"
    CARD_BG = "rgba(30, 15, 45, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_PINK = "#d946ef"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_window(self) -> None:
        """Pencere ayarlarını yapar"""
        self.setWindowTitle("ChwiliTranslate")
        # Sabit boyut - değiştirilemez
        self.setFixedSize(1100, 700)
    
    def _setup_ui(self) -> None:
        """UI bileşenlerini oluşturur"""
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self._sidebar = self._create_sidebar()
        main_layout.addWidget(self._sidebar)
        
        # İçerik alanı
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget (sekmeler için)
        self._stack = QStackedWidget()
        content_layout.addWidget(self._stack)
        
        # Placeholder sayfalar
        self._create_pages()
        
        main_layout.addWidget(content_area, 1)

    
    def _create_sidebar(self) -> QWidget:
        """Sidebar oluşturur"""
        sidebar = QFrame()
        sidebar.setFixedWidth(60)
        sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setSpacing(10)
        
        # Logo/başlık - ikon kullan
        import os
        # main_window.py src/ui içinde, assets kök dizinde
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "assets", "icons", "icon_48.png")
        
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(45, 45)
        
        if os.path.exists(icon_path):
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(icon_path)
            scaled = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(scaled)
        else:
            logo.setText("CT")
            logo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            logo.setStyleSheet(f"color: {self.ACCENT_PURPLE};")
        layout.addWidget(logo)
        
        layout.addSpacing(20)
        
        # Navigasyon butonları
        self._nav_buttons = []
        
        nav_items = [
            ("🏠", "Ana Sayfa", 0),
            ("📷", "OCR Control", 1),
            ("🌐", "Translation", 2),
            ("💬", "Overlay", 3),
            ("⚙️", "Ayarlar", 4),
            ("⌨️", "Kısayollar", 5),
        ]
        
        for icon, tooltip, index in nav_items:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(45, 45)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=index: self._on_nav_click(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # İlk butonu seç
        if self._nav_buttons:
            self._nav_buttons[0].setChecked(True)
        
        layout.addStretch()
        
        return sidebar
    
    def _create_pages(self) -> None:
        """Sayfa placeholder'larını oluşturur"""
        pages = ["Ana Sayfa", "OCR Control", "Translation", "Overlay", "Ayarlar", "Kısayollar"]
        
        for page_name in pages:
            page = QWidget()
            layout = QVBoxLayout(page)
            
            # Başlık
            title = QLabel(page_name)
            title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
            title.setStyleSheet(f"color: {self.TEXT_PRIMARY};")
            layout.addWidget(title)
            
            # Placeholder içerik
            content = QLabel(f"{page_name} içeriği burada görünecek")
            content.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
            layout.addWidget(content)
            
            layout.addStretch()
            
            self._stack.addWidget(page)
    
    def _on_nav_click(self, index: int) -> None:
        """Navigasyon butonuna tıklandığında"""
        # Tüm butonları deselect et
        for btn in self._nav_buttons:
            btn.setChecked(False)
        
        # Tıklanan butonu seç
        self._nav_buttons[index].setChecked(True)
        
        # Sayfayı değiştir
        self._stack.setCurrentIndex(index)

    
    def _apply_styles(self) -> None:
        """Mor/Siyah gradient stillerini uygular"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #050505, stop:0.4 #0a0510, stop:0.7 #0f0818, stop:1 #0a0510);
            }}
            
            #sidebar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(12, 5, 20, 0.98), stop:1 rgba(5, 2, 10, 0.98));
                border-right: 1px solid rgba(168, 85, 247, 0.2);
            }}
            
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 10px;
                color: {self.TEXT_SECONDARY};
                font-size: 18px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(168, 85, 247, 0.15);
            }}
            
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(168, 85, 247, 0.25), stop:1 rgba(139, 92, 246, 0.25));
                color: {self.ACCENT_PURPLE};
                border: 1px solid {self.ACCENT_PURPLE};
            }}
            
            QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
            
            QFrame#card {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18, 8, 28, 0.95), stop:1 rgba(10, 5, 18, 0.95));
                border: 1px solid rgba(168, 85, 247, 0.15);
                border-radius: 15px;
            }}
            
            QScrollBar:vertical {{
                background-color: rgba(168, 85, 247, 0.05);
                width: 8px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_PURPLE}, stop:1 {self.ACCENT_VIOLET});
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_PINK}, stop:1 {self.ACCENT_PURPLE});
            }}
        """)
    
    def set_page(self, index: int) -> None:
        """Belirtilen sayfaya geçer"""
        if 0 <= index < len(self._nav_buttons):
            self._on_nav_click(index)
    
    def get_current_page(self) -> int:
        """Mevcut sayfa indeksini döndürür"""
        return self._stack.currentIndex()
    
    def set_page_widget(self, index: int, widget: QWidget) -> None:
        """Belirtilen sayfanın widget'ını değiştirir (scroll ile)"""
        if 0 <= index < self._stack.count():
            old_widget = self._stack.widget(index)
            self._stack.removeWidget(old_widget)
            
            # Scroll area oluştur
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setStyleSheet("""
                QScrollArea {
                    background-color: transparent;
                    border: none;
                }
                QScrollArea > QWidget > QWidget {
                    background-color: transparent;
                }
            """)
            
            # Container widget
            container = QWidget()
            container_layout = QVBoxLayout(container)
            container_layout.setContentsMargins(20, 20, 20, 20)
            container_layout.addWidget(widget)
            
            scroll.setWidget(container)
            self._stack.insertWidget(index, scroll)
