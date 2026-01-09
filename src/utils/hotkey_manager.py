"""
Hotkey Manager for ChwiliTranslate
Global klavye kısayolları yönetimi
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, Callable, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QApplication


# Varsayılan kısayollar
DEFAULT_HOTKEYS: Dict[str, Dict] = {
    # Genel
    "toggle_ocr": {"key": "F8", "name": "OCR Başlat / Durdur", "category": "Genel"},
    "toggle_app": {"key": "F9", "name": "Uygulamayı Gizle / Göster", "category": "Genel"},
    "select_region": {"key": "F10", "name": "OCR Bölgesi Seç", "category": "Genel"},
    "toggle_settings": {"key": "F11", "name": "Ayarlar Paneli", "category": "Genel"},
    "clear_cache": {"key": "F12", "name": "Cache Temizle", "category": "Genel"},
    
    # Overlay
    "font_size_up": {"key": "Ctrl+Shift+Up", "name": "Yazı Boyutu Artır", "category": "Overlay"},
    "font_size_down": {"key": "Ctrl+Shift+Down", "name": "Yazı Boyutu Azalt", "category": "Overlay"},
    "opacity_down": {"key": "Ctrl+Shift+Left", "name": "Opaklık Azalt", "category": "Overlay"},
    "opacity_up": {"key": "Ctrl+Shift+Right", "name": "Opaklık Artır", "category": "Overlay"},
    
    # Uygulama
    "quit_app": {"key": "Ctrl+Shift+Q", "name": "Uygulamayı Kapat", "category": "Uygulama"},
}

# Engellenen sistem kısayolları
BLOCKED_KEYS = [
    "Alt+F4", "Ctrl+Alt+Delete", "Alt+Tab", "Win", "Ctrl+Esc",
    "Ctrl+C", "Ctrl+V", "Ctrl+X", "Ctrl+Z", "Ctrl+A", "Ctrl+S"
]


class HotkeyManager(QObject):
    """Global hotkey yöneticisi"""
    
    # Sinyaller
    hotkey_triggered = pyqtSignal(str)  # action_id
    hotkeys_changed = pyqtSignal()
    
    CONFIG_FILE = "hotkeys.json"
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hotkeys: Dict[str, Dict] = {}
        self._shortcuts: Dict[str, QShortcut] = {}
        self._callbacks: Dict[str, Callable] = {}
        self._widget = None
        self._load_hotkeys()
    
    def set_widget(self, widget) -> None:
        """Ana widget'ı ayarlar (shortcut'lar için)"""
        self._widget = widget
        self._register_all_shortcuts()
    
    def _load_hotkeys(self) -> None:
        """Kısayolları dosyadan yükler"""
        import copy
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                # Varsayılanları al, kaydedilmişlerle güncelle
                self._hotkeys = copy.deepcopy(DEFAULT_HOTKEYS)
                for action_id, data in saved.items():
                    if action_id in self._hotkeys:
                        self._hotkeys[action_id]["key"] = data.get("key", self._hotkeys[action_id]["key"])
            except (json.JSONDecodeError, IOError):
                self._hotkeys = copy.deepcopy(DEFAULT_HOTKEYS)
        else:
            self._hotkeys = copy.deepcopy(DEFAULT_HOTKEYS)
    
    def _save_hotkeys(self) -> None:
        """Kısayolları dosyaya kaydeder"""
        save_data = {}
        for action_id, data in self._hotkeys.items():
            save_data[action_id] = {"key": data["key"]}
        
        with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    def _register_all_shortcuts(self) -> None:
        """Tüm kısayolları kaydet"""
        if not self._widget:
            return
        
        # Eski shortcut'ları temizle
        for shortcut in self._shortcuts.values():
            shortcut.setEnabled(False)
            shortcut.deleteLater()
        self._shortcuts.clear()
        
        # Yeni shortcut'ları oluştur
        for action_id, data in self._hotkeys.items():
            # F9 global hotkey olarak pynput ile yönetiliyor, QShortcut oluşturma
            if action_id == "toggle_app":
                continue
            key = data["key"]
            if key:
                shortcut = QShortcut(QKeySequence(key), self._widget)
                shortcut.activated.connect(lambda aid=action_id: self._on_shortcut_activated(aid))
                self._shortcuts[action_id] = shortcut
    
    def _on_shortcut_activated(self, action_id: str) -> None:
        """Kısayol tetiklendiğinde"""
        self.hotkey_triggered.emit(action_id)
        if action_id in self._callbacks:
            self._callbacks[action_id]()
    
    def register_callback(self, action_id: str, callback: Callable) -> None:
        """Bir aksiyon için callback kaydet"""
        self._callbacks[action_id] = callback
    
    def get_hotkey(self, action_id: str) -> Optional[str]:
        """Bir aksiyonun kısayolunu döndürür"""
        if action_id in self._hotkeys:
            return self._hotkeys[action_id]["key"]
        return None
    
    def set_hotkey(self, action_id: str, key: str) -> bool:
        """Bir aksiyonun kısayolunu değiştirir"""
        # Engellenen tuşları kontrol et
        if key in BLOCKED_KEYS:
            return False
        
        # Çakışma kontrolü
        for aid, data in self._hotkeys.items():
            if aid != action_id and data["key"] == key:
                return False
        
        if action_id in self._hotkeys:
            self._hotkeys[action_id]["key"] = key
            self._save_hotkeys()
            self._register_all_shortcuts()
            self.hotkeys_changed.emit()
            return True
        return False
    
    def get_all_hotkeys(self) -> Dict[str, Dict]:
        """Tüm kısayolları döndürür"""
        return self._hotkeys.copy()
    
    def get_categories(self) -> List[str]:
        """Tüm kategorileri döndürür"""
        categories = []
        for data in self._hotkeys.values():
            cat = data["category"]
            if cat not in categories:
                categories.append(cat)
        return categories
    
    def get_hotkeys_by_category(self, category: str) -> Dict[str, Dict]:
        """Kategoriye göre kısayolları döndürür"""
        return {
            aid: data for aid, data in self._hotkeys.items()
            if data["category"] == category
        }
    
    def check_conflict(self, key: str, exclude_action: str = None) -> Optional[str]:
        """Çakışma kontrolü yapar, çakışan action_id döndürür"""
        for aid, data in self._hotkeys.items():
            if aid != exclude_action and data["key"] == key:
                return aid
        return None
    
    def is_blocked_key(self, key: str) -> bool:
        """Engellenen tuş mu kontrol eder"""
        return key in BLOCKED_KEYS
    
    def reset_to_defaults(self) -> None:
        """Varsayılanlara döner"""
        import copy
        self._hotkeys = copy.deepcopy(DEFAULT_HOTKEYS)
        self._save_hotkeys()
        self._register_all_shortcuts()
        self.hotkeys_changed.emit()
    
    def reset_single(self, action_id: str) -> None:
        """Tek bir kısayolu varsayılana döndürür"""
        if action_id in DEFAULT_HOTKEYS:
            self._hotkeys[action_id]["key"] = DEFAULT_HOTKEYS[action_id]["key"]
            self._save_hotkeys()
            self._register_all_shortcuts()
            self.hotkeys_changed.emit()
