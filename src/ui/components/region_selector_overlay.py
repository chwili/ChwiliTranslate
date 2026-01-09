"""
Region Selector Overlay for ChwiliTranslate
Tam ekran bölge seçim arayüzü
"""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QCursor, QFont, QBrush
from typing import List, Dict


class RegionSelectorOverlay(QWidget):
    """Tam ekran bölge seçim overlay'i"""
    
    # Sinyaller
    region_selected = pyqtSignal(int, int, int, int)  # x, y, width, height
    selection_cancelled = pyqtSignal()
    
    def __init__(self, monitor_geometry: QRect = None):
        super().__init__()
        self._start_point = None
        self._end_point = None
        self._is_selecting = False
        self._exclusion_areas: List[Dict] = []  # Hariç tutulan alanlar
        
        self._setup_window(monitor_geometry)
    
    def _setup_window(self, geometry: QRect = None) -> None:
        """Pencere ayarlarını yapar"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # Tam ekran veya belirtilen geometri
        if geometry:
            self.setGeometry(geometry)
        else:
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
    
    def paintEvent(self, event) -> None:
        """Çizim olayı"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Yarı saydam arka plan
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        # Seçim dikdörtgeni (önce çiz, sonra hariç tutulan alanlar üstte olsun)
        if self._start_point and self._end_point:
            selection_rect = QRect(self._start_point, self._end_point).normalized()
            
            # Seçili alanı temizle (şeffaf yap)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            
            # Seçim çerçevesi
            pen = QPen(QColor(0, 212, 255), 3)
            painter.setPen(pen)
            painter.drawRect(selection_rect)
            
            # Boyut bilgisi
            width = selection_rect.width()
            height = selection_rect.height()
            info_text = f"{width} x {height}"
            
            # Boyut bilgisi arka planı
            info_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
            painter.setFont(info_font)
            info_metrics = painter.fontMetrics()
            info_rect = info_metrics.boundingRect(info_text)
            
            info_bg = QRect(
                selection_rect.x(),
                selection_rect.y() - info_rect.height() - 10,
                info_rect.width() + 16,
                info_rect.height() + 8
            )
            painter.fillRect(info_bg, QColor(0, 212, 255, 200))
            painter.setPen(QColor(0, 0, 0))
            painter.drawText(
                selection_rect.x() + 8,
                selection_rect.y() - 8,
                info_text
            )
        
        # Hariç tutulan alanları kırmızı kutular olarak çiz (en üstte)
        for area in self._exclusion_areas:
            ex_rect = QRect(
                area.get("x", 0),
                area.get("y", 0),
                area.get("width", 0),
                area.get("height", 0)
            )
            
            # Kırmızı yarı saydam dolgu
            painter.fillRect(ex_rect, QColor(200, 50, 50, 100))
            
            # Kırmızı çerçeve - kalın
            pen = QPen(QColor(255, 60, 60), 4)
            painter.setPen(pen)
            painter.drawRect(ex_rect)
            
            # Yazıları doğrudan çiz - kutu yok
            # Ana başlık: "SEÇİLEMEZ"
            title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
            painter.setFont(title_font)
            title_text = "SEÇİLEMEZ"
            title_metrics = painter.fontMetrics()
            title_width = title_metrics.horizontalAdvance(title_text)
            title_height = title_metrics.height()
            
            # Başlık konumu (ortada)
            title_x = ex_rect.x() + (ex_rect.width() - title_width) // 2
            title_y = ex_rect.y() + (ex_rect.height() // 2)
            
            # Yazı gölgesi
            painter.setPen(QColor(0, 0, 0, 200))
            painter.drawText(title_x + 3, title_y + 3, title_text)
            
            # Ana yazı - beyaz
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(title_x, title_y, title_text)
            
            # Alt yazı: "Hariç tutulan alanları kaldır"
            subtitle_font = QFont("Segoe UI", 16)
            painter.setFont(subtitle_font)
            subtitle_text = "Hariç tutulan alanları kaldır"
            subtitle_metrics = painter.fontMetrics()
            subtitle_width = subtitle_metrics.horizontalAdvance(subtitle_text)
            
            subtitle_x = ex_rect.x() + (ex_rect.width() - subtitle_width) // 2
            subtitle_y = title_y + 35
            
            # Alt yazı gölgesi
            painter.setPen(QColor(0, 0, 0, 200))
            painter.drawText(subtitle_x + 2, subtitle_y + 2, subtitle_text)
            
            # Alt yazı - açık gri
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(subtitle_x, subtitle_y, subtitle_text)
        
        # ESC ipucu - ekranın üstünde
        hint_font = QFont("Segoe UI", 11)
        painter.setFont(hint_font)
        hint_text = "ESC - İptal  |  Fare ile bölge seçin"
        hint_metrics = painter.fontMetrics()
        hint_width = hint_metrics.horizontalAdvance(hint_text)
        
        hint_x = (self.width() - hint_width) // 2
        hint_y = 40
        
        # Hint arka planı
        hint_bg = QRect(hint_x - 15, hint_y - 20, hint_width + 30, 30)
        painter.fillRect(hint_bg, QColor(0, 0, 0, 180))
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(hint_x, hint_y, hint_text)
    
    def mousePressEvent(self, event) -> None:
        """Fare basma olayı"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_point = event.pos()
            self._end_point = event.pos()
            self._is_selecting = True
            self.update()
    
    def mouseMoveEvent(self, event) -> None:
        """Fare hareket olayı"""
        if self._is_selecting:
            self._end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event) -> None:
        """Fare bırakma olayı"""
        if event.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            
            if self._start_point and self._end_point:
                rect = QRect(self._start_point, self._end_point).normalized()
                
                if rect.width() > 10 and rect.height() > 10:
                    # Hariç tutulan alanla çakışma kontrolü
                    if self._intersects_exclusion_area(rect):
                        # Seçim hariç tutulan alanla çakışıyor, iptal et
                        self._start_point = None
                        self._end_point = None
                        self.update()
                        return
                    
                    self.region_selected.emit(
                        rect.x(), rect.y(),
                        rect.width(), rect.height()
                    )
                    self.close()
                else:
                    # Çok küçük seçim, iptal et
                    self._start_point = None
                    self._end_point = None
                    self.update()
    
    def _intersects_exclusion_area(self, rect: QRect) -> bool:
        """Seçimin hariç tutulan alanla çakışıp çakışmadığını kontrol eder"""
        for area in self._exclusion_areas:
            ex_rect = QRect(
                area.get("x", 0),
                area.get("y", 0),
                area.get("width", 0),
                area.get("height", 0)
            )
            if rect.intersects(ex_rect):
                return True
        return False
    
    def keyPressEvent(self, event) -> None:
        """Tuş basma olayı"""
        if event.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
    
    def start_selection(self) -> None:
        """Bölge seçimini başlatır"""
        self._start_point = None
        self._end_point = None
        self._is_selecting = False
        
        # Ekran geometrisini güncelle
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        
        self.showFullScreen()
        self.activateWindow()
        self.raise_()
    
    def set_exclusion_areas(self, areas: List[Dict]) -> None:
        """Hariç tutulan alanları ayarlar"""
        self._exclusion_areas = areas.copy()
        self.update()
