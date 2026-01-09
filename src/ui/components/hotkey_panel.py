"""
Hotkey Panel for ChwiliTranslate
Klavye kısayolları ayar paneli
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeySequence


class HotkeyBadge(QPushButton):
    """Kısayol tuşu badge'i"""
    
    key_changed = pyqtSignal(str)  # Yeni tuş
    
    def __init__(self, key: str, parent=None):
        super().__init__(key, parent)
        self._current_key = key
        self._editing = False
        self._error = False
        self.setFixedHeight(36)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()
        self.clicked.connect(self._start_editing)
    
    def _apply_style(self) -> None:
        if self._error:
            bg = "rgba(239, 68, 68, 0.3)"
            border = "#ef4444"
            glow = "0 0 10px rgba(239, 68, 68, 0.5)"
        elif self._editing:
            bg = "rgba(168, 85, 247, 0.3)"
            border = "#a855f7"
            glow = "0 0 15px rgba(168, 85, 247, 0.6)"
        else:
            bg = "rgba(139, 92, 246, 0.2)"
            border = "#8b5cf6"
            glow = "none"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: rgba(168, 85, 247, 0.3);
                box-shadow: {glow};
            }}
        """)
    
    def _start_editing(self) -> None:
        self._editing = True
        self._error = False
        self.setText("Tuşa basın...")
        self._apply_style()
        self.setFocus()
    
    def stop_editing(self, success: bool = True) -> None:
        self._editing = False
        if success:
            self.setText(self._current_key)
        self._apply_style()
    
    def set_error(self, error: bool) -> None:
        self._error = error
        self._apply_style()
        if error:
            QTimer.singleShot(1500, lambda: self.set_error(False))
    
    def set_key(self, key: str) -> None:
        self._current_key = key
        self.setText(key)
    
    def get_key(self) -> str:
        return self._current_key
    
    def is_editing(self) -> bool:
        return self._editing
    
    def keyPressEvent(self, event) -> None:
        if not self._editing:
            super().keyPressEvent(event)
            return
        
        # Tuş kombinasyonunu oluştur
        key = event.key()
        modifiers = event.modifiers()
        
        # Sadece modifier tuşlarını yoksay
        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return
        
        # Escape ile iptal
        if key == Qt.Key.Key_Escape:
            self.stop_editing(True)
            return
        
        # Tuş dizisini oluştur
        parts = []
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            parts.append("Ctrl")
        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            parts.append("Shift")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            parts.append("Alt")
        
        # Tuş adını al
        key_name = QKeySequence(key).toString()
        if key_name:
            parts.append(key_name)
        
        if parts:
            new_key = "+".join(parts)
            self._current_key = new_key
            self.key_changed.emit(new_key)
            self.stop_editing(True)


class HotkeyRow(QFrame):
    """Tek bir kısayol satırı"""
    
    key_change_requested = pyqtSignal(str, str)  # action_id, new_key
    
    def __init__(self, action_id: str, name: str, key: str, category: str, locked: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("hotkeyRow")
        self._action_id = action_id
        self._locked = locked
        self._setup_ui(name, key, category)
        self._apply_style()
    
    def _setup_ui(self, name: str, key: str, category: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(15)
        
        # İşlev adı
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 12))
        name_label.setStyleSheet("color: #ffffff;")
        name_label.setMinimumWidth(200)
        layout.addWidget(name_label)
        
        # Kategori etiketi
        cat_label = QLabel(category)
        cat_label.setFont(QFont("Segoe UI", 10))
        cat_label.setStyleSheet("""
            color: #c4b5fd;
            background-color: rgba(168, 85, 247, 0.2);
            padding: 3px 10px;
            border-radius: 5px;
        """)
        cat_label.setFixedWidth(80)
        cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(cat_label)
        
        layout.addStretch()
        
        # Kilitli ise kilit ikonu göster
        if self._locked:
            lock_label = QLabel("🔒")
            lock_label.setToolTip("Bu kısayol değiştirilemez")
            layout.addWidget(lock_label)
        
        # Kısayol badge
        self._badge = HotkeyBadge(key)
        if self._locked:
            self._badge.setEnabled(False)
            self._badge.setStyleSheet("""
                QPushButton {
                    background-color: rgba(60, 30, 80, 0.4);
                    border: 1px solid rgba(168, 85, 247, 0.2);
                    border-radius: 8px;
                    color: #9ca3af;
                    font-size: 13px;
                    font-weight: bold;
                    padding: 5px 15px;
                }
            """)
        else:
            self._badge.key_changed.connect(self._on_key_changed)
        layout.addWidget(self._badge)
    
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QFrame#hotkeyRow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(18, 8, 28, 0.8), stop:1 rgba(10, 5, 18, 0.8));
                border-radius: 10px;
                border: 1px solid rgba(168, 85, 247, 0.1);
            }
            QFrame#hotkeyRow:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(25, 12, 38, 0.9), stop:1 rgba(15, 8, 25, 0.9));
                border: 1px solid rgba(168, 85, 247, 0.25);
            }
            QLabel {
                background: transparent;
                border: none;
            }
        """)
    
    def _on_key_changed(self, new_key: str) -> None:
        self.key_change_requested.emit(self._action_id, new_key)
    
    def set_key(self, key: str) -> None:
        self._badge.set_key(key)
    
    def set_error(self, error: bool) -> None:
        self._badge.set_error(error)
    
    def get_action_id(self) -> str:
        return self._action_id


class HotkeyPanel(QWidget):
    """Klavye kısayolları ayar paneli"""
    
    # Mor/Siyah Gradient Tema
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    def __init__(self, hotkey_manager, parent=None):
        super().__init__(parent)
        self._manager = hotkey_manager
        self._rows: dict = {}
        self._setup_ui()
        self._load_hotkeys()
        
        # Manager sinyallerini bağla
        self._manager.hotkeys_changed.connect(self._load_hotkeys)
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Başlık alanı
        header = QHBoxLayout()
        
        title = QLabel("⌨️ Klavye Kısayolları")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {self.ACCENT_PURPLE};")
        header.addWidget(title)
        
        header.addStretch()
        
        # Varsayılana dön butonu
        reset_btn = QPushButton("🔄 Varsayılana Dön")
        reset_btn.setFixedHeight(40)
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._on_reset_all)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(168, 85, 247, 0.2);
                border: 1px solid {self.ACCENT_PURPLE};
                border-radius: 10px;
                color: {self.TEXT_PRIMARY};
                font-size: 13px;
                padding: 8px 20px;
            }}
            QPushButton:hover {{
                background-color: rgba(168, 85, 247, 0.4);
            }}
        """)
        header.addWidget(reset_btn)
        
        layout.addLayout(header)
        
        # Açıklama
        desc = QLabel("Aşağıdaki kısayolları dilediğiniz gibi değiştirebilirsiniz. Bir tuşa tıklayıp yeni kombinasyonu girin.")
        desc.setStyleSheet(f"color: {self.TEXT_SECONDARY}; font-size: 13px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Kısayol listesi container
        self._list_container = QVBoxLayout()
        self._list_container.setSpacing(8)
        layout.addLayout(self._list_container)
        
        layout.addStretch()
    
    def _load_hotkeys(self) -> None:
        """Kısayolları yükler ve UI'ı günceller"""
        # Mevcut satırları temizle
        while self._list_container.count():
            item = self._list_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._rows.clear()
        
        # Kategorilere göre grupla
        categories = self._manager.get_categories()
        
        for category in categories:
            # Kategori başlığı
            cat_label = QLabel(f"📁 {category}")
            cat_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            cat_label.setStyleSheet(f"color: {self.ACCENT_PURPLE}; margin-top: 10px;")
            self._list_container.addWidget(cat_label)
            
            # Bu kategorideki kısayollar
            hotkeys = self._manager.get_hotkeys_by_category(category)
            for action_id, data in hotkeys.items():
                # toggle_app (F9) değiştirilemez
                is_locked = action_id == "toggle_app"
                row = HotkeyRow(action_id, data["name"], data["key"], category, locked=is_locked)
                row.key_change_requested.connect(self._on_key_change)
                self._rows[action_id] = row
                self._list_container.addWidget(row)
    
    def _on_key_change(self, action_id: str, new_key: str) -> None:
        """Tuş değişikliği isteği"""
        # Engellenen tuş kontrolü
        if self._manager.is_blocked_key(new_key):
            self._rows[action_id].set_error(True)
            return
        
        # Çakışma kontrolü
        conflict = self._manager.check_conflict(new_key, action_id)
        if conflict:
            self._rows[action_id].set_error(True)
            if conflict in self._rows:
                self._rows[conflict].set_error(True)
            return
        
        # Tuşu kaydet
        if self._manager.set_hotkey(action_id, new_key):
            self._rows[action_id].set_key(new_key)
    
    def _on_reset_all(self) -> None:
        """Tüm kısayolları varsayılana döndür"""
        self._manager.reset_to_defaults()
