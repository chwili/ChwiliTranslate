"""
Status Bar for ChwiliTranslate
OCR durumu, FPS ve GPU bilgisi
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class StatusBar(QWidget):
    """Floating status bar"""
    
    # Sinyaller
    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.95)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    ACCENT_GREEN = "#22c55e"
    ACCENT_RED = "#ef4444"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self):
        super().__init__()
        self._is_running = False
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)
        
        # OCR durumu
        self._ocr_indicator = QLabel("●")
        self._ocr_indicator.setFont(QFont("Segoe UI", 12))
        self._ocr_status = QLabel("OCR Inactive")
        layout.addWidget(self._ocr_indicator)
        layout.addWidget(self._ocr_status)
        
        # Ayırıcı
        layout.addWidget(self._create_separator())
        
        # GPU durumu
        self._gpu_indicator = QLabel("●")
        self._gpu_indicator.setFont(QFont("Segoe UI", 12))
        self._gpu_status = QLabel("CPU Only")
        self._gpu_indicator.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
        layout.addWidget(self._gpu_indicator)
        layout.addWidget(self._gpu_status)
        
        layout.addStretch()
        
        # START/STOP butonu
        self._start_btn = QPushButton("▶ START")
        self._start_btn.setFixedSize(120, 40)
        self._start_btn.setObjectName("startButton")
        self._start_btn.clicked.connect(self._on_start_click)
        layout.addWidget(self._start_btn)
    
    def _create_separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setStyleSheet("background-color: rgba(255, 255, 255, 0.2);")
        sep.setFixedWidth(1)
        return sep
    
    def _on_start_click(self) -> None:
        if self._is_running:
            self.stop_clicked.emit()
        else:
            self.start_clicked.emit()
    
    def _apply_styles(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(18, 8, 28, 0.95), stop:1 rgba(12, 5, 20, 0.95));
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 15px;
            }}
            QLabel {{
                color: {self.TEXT_PRIMARY};
                border: none;
                background: transparent;
            }}
            #startButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_PURPLE}, stop:1 {self.ACCENT_VIOLET});
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            #startButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #b366ff, stop:1 #9d6eff);
            }}
            #stopButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ACCENT_RED}, stop:1 #dc2626);
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }}
            #stopButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f87171, stop:1 #ef4444);
            }}
        """)
        self._update_indicators()

    
    def _update_indicators(self) -> None:
        """Göstergeleri günceller"""
        if self._is_running:
            self._ocr_indicator.setStyleSheet(f"color: {self.ACCENT_GREEN};")
            self._ocr_status.setText("OCR Active")
            self._start_btn.setText("■ STOP")
            self._start_btn.setObjectName("stopButton")
        else:
            self._ocr_indicator.setStyleSheet(f"color: {self.ACCENT_RED};")
            self._ocr_status.setText("OCR Inactive")
            self._start_btn.setText("▶ START")
            self._start_btn.setObjectName("startButton")
        
        # Stil yenile
        self._start_btn.style().unpolish(self._start_btn)
        self._start_btn.style().polish(self._start_btn)
    
    # Public metodlar
    def set_running(self, running: bool) -> None:
        """OCR çalışma durumunu ayarlar"""
        self._is_running = running
        self._update_indicators()
    
    def is_running(self) -> bool:
        """OCR çalışıyor mu döndürür"""
        return self._is_running
    
    def set_fps(self, fps: float) -> None:
        """FPS değerini günceller - artık kullanılmıyor"""
        pass
    
    def get_fps_text(self) -> str:
        """FPS metnini döndürür - artık kullanılmıyor"""
        return ""
    
    def set_gpu_status(self, enabled: bool, available: bool = True) -> None:
        """GPU durumunu günceller"""
        if not available:
            # GPU/CUDA mevcut değil - CPU kullanılıyor
            self._gpu_indicator.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
            self._gpu_status.setText("CPU Mode")
        elif enabled and available:
            # GPU mevcut ve aktif
            self._gpu_indicator.setStyleSheet(f"color: {self.ACCENT_GREEN};")
            self._gpu_status.setText("GPU Active")
        else:
            # GPU mevcut ama devre dışı
            self._gpu_indicator.setStyleSheet(f"color: {self.TEXT_SECONDARY};")
            self._gpu_status.setText("GPU Off")
    
    def get_gpu_status_text(self) -> str:
        """GPU durum metnini döndürür"""
        return self._gpu_status.text()
    
    def get_ocr_status_text(self) -> str:
        """OCR durum metnini döndürür"""
        return self._ocr_status.text()
