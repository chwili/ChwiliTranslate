"""
Translation Panel for ChwiliTranslate
Çeviri ayarları ve provider seçimi
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QDialog, QLineEdit, QFormLayout,
    QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class APIKeyDialog(QDialog):
    """API Key yönetim dialogu"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API Anahtarları")
        self.setMinimumWidth(400)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # Form
        form = QFormLayout()
        
        self._chatgpt_input = QLineEdit()
        self._chatgpt_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._chatgpt_input.setPlaceholderText("sk-...")
        form.addRow("ChatGPT:", self._chatgpt_input)
        
        self._gemini_input = QLineEdit()
        self._gemini_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Gemini:", self._gemini_input)
        
        self._google_input = QLineEdit()
        self._google_input.setPlaceholderText("Ücretsiz - API key gerekmez")
        self._google_input.setEnabled(False)
        form.addRow("Google:", self._google_input)
        
        self._deepl_input = QLineEdit()
        self._deepl_input.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("DeepL:", self._deepl_input)
        
        layout.addLayout(form)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QDialog {
                background-color: #0a0a0f;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #00d4ff;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
            }
        """)
    
    def get_keys(self) -> dict:
        return {
            "chatgpt": self._chatgpt_input.text(),
            "gemini": self._gemini_input.text(),
            "google": self._google_input.text(),
            "deepl": self._deepl_input.text()
        }
    
    def set_keys(self, keys: dict) -> None:
        self._chatgpt_input.setText(keys.get("chatgpt", ""))
        self._gemini_input.setText(keys.get("gemini", ""))
        self._google_input.setText(keys.get("google", ""))
        self._deepl_input.setText(keys.get("deepl", ""))


class TranslationPanel(QWidget):
    """Translation paneli"""
    
    # Sinyaller
    provider_changed = pyqtSignal(str)
    source_lang_changed = pyqtSignal(str)
    target_lang_changed = pyqtSignal(str)
    api_keys_updated = pyqtSignal(dict)
    
    # Mor/Siyah Gradient Tema
    CARD_BG = "rgba(35, 15, 55, 0.9)"
    ACCENT_PURPLE = "#a855f7"
    ACCENT_VIOLET = "#8b5cf6"
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#c4b5fd"
    
    PROVIDERS = [
        ("ChatGPT", "chatgpt", "🤖"),
        ("Gemini", "gemini", "✨"),
        ("Google (Ücretsiz)", "google", "🌐"),
        ("DeepL", "deepl", "📚"),
    ]
    
    LANGUAGES = [
        ("İngilizce", "en"),
        ("Türkçe", "tr"),
        ("Japonca", "ja"),
        ("Korece", "ko"),
        ("Çince", "zh"),
        ("Almanca", "de"),
        ("Fransızca", "fr"),
        ("İspanyolca", "es"),
    ]
    
    def __init__(self):
        super().__init__()
        self._selected_provider = "google"  # Varsayılan: Google (ücretsiz)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Başlık
        title = QLabel("Translation")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Dil ayarları kartı
        lang_card = self._create_language_card()
        layout.addWidget(lang_card)
        
        # Provider seçimi kartı
        provider_card = self._create_provider_card()
        layout.addWidget(provider_card)
        
        layout.addStretch()
    
    def _create_language_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("🌍 Dil Ayarları")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Kaynak dil
        source_layout = QHBoxLayout()
        source_label = QLabel("Kaynak Dil:")
        self._source_combo = QComboBox()
        for name, code in self.LANGUAGES:
            self._source_combo.addItem(name, code)
        self._source_combo.setCurrentIndex(0)  # İngilizce
        self._source_combo.currentIndexChanged.connect(
            lambda: self.source_lang_changed.emit(self._source_combo.currentData())
        )
        source_layout.addWidget(source_label)
        source_layout.addWidget(self._source_combo, 1)
        layout.addLayout(source_layout)
        
        # Hedef dil
        target_layout = QHBoxLayout()
        target_label = QLabel("Hedef Dil:")
        self._target_combo = QComboBox()
        for name, code in self.LANGUAGES:
            self._target_combo.addItem(name, code)
        self._target_combo.setCurrentIndex(1)  # Türkçe
        self._target_combo.currentIndexChanged.connect(
            lambda: self.target_lang_changed.emit(self._target_combo.currentData())
        )
        target_layout.addWidget(target_label)
        target_layout.addWidget(self._target_combo, 1)
        layout.addLayout(target_layout)
        
        return card

    
    def _create_provider_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        
        header = QLabel("🔌 Çeviri Sağlayıcısı")
        header.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Provider butonları
        self._provider_buttons = {}
        providers_layout = QHBoxLayout()
        
        for name, code, icon in self.PROVIDERS:
            btn = QPushButton(f"{icon} {name}")
            btn.setCheckable(True)
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda checked, c=code: self._on_provider_click(c))
            self._provider_buttons[code] = btn
            providers_layout.addWidget(btn)
        
        # Varsayılan seçim: Google (ücretsiz)
        self._provider_buttons["google"].setChecked(True)
        
        layout.addLayout(providers_layout)
        
        # API Key yönetimi
        api_layout = QHBoxLayout()
        api_layout.addStretch()
        self._api_btn = QPushButton("🔑 API Anahtarlarını Yönet")
        self._api_btn.setObjectName("linkButton")
        self._api_btn.clicked.connect(self._show_api_dialog)
        api_layout.addWidget(self._api_btn)
        layout.addLayout(api_layout)
        
        return card
    
    def _on_provider_click(self, provider: str) -> None:
        # Tüm butonları deselect et
        for btn in self._provider_buttons.values():
            btn.setChecked(False)
        
        # Seçilen butonu işaretle
        self._provider_buttons[provider].setChecked(True)
        self._selected_provider = provider
        self.provider_changed.emit(provider)
    
    def _show_api_dialog(self) -> None:
        dialog = APIKeyDialog(self)
        # Mevcut anahtarları yükle
        if hasattr(self, '_saved_api_keys'):
            dialog.set_keys(self._saved_api_keys)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            keys = dialog.get_keys()
            self._saved_api_keys = keys
            self.api_keys_updated.emit(keys)
    
    def set_api_keys(self, keys: dict) -> None:
        """API anahtarlarını ayarlar (config'den yükleme için)"""
        self._saved_api_keys = keys
    
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
            
            QComboBox {{
                background: rgba(35, 18, 55, 0.7);
                border: 1px solid rgba(168, 85, 247, 0.25);
                border-radius: 8px;
                padding: 8px 12px;
                color: {self.TEXT_PRIMARY};
                min-width: 150px;
            }}
            
            QComboBox:hover {{
                border-color: {self.ACCENT_PURPLE};
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
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background: rgba(168, 85, 247, 0.25);
                border-color: {self.ACCENT_PURPLE};
            }}
            
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(168, 85, 247, 0.35), stop:1 rgba(139, 92, 246, 0.35));
                border-color: {self.ACCENT_PURPLE};
                color: {self.ACCENT_PURPLE};
            }}
            
            QLineEdit {{
                background: rgba(25, 12, 40, 0.8);
                border: 1px solid rgba(168, 85, 247, 0.2);
                border-radius: 8px;
                padding: 8px;
                color: {self.TEXT_PRIMARY};
            }}
            
            #linkButton {{
                background-color: transparent;
                border: none;
                color: {self.ACCENT_PURPLE};
                text-decoration: underline;
            }}
            
            #linkButton:hover {{
                color: {self.ACCENT_VIOLET};
            }}
        """)
    
    # Getter/Setter metodları
    def get_provider(self) -> str:
        return self._selected_provider
    
    def set_provider(self, provider: str) -> None:
        self._on_provider_click(provider)
    
    def get_source_language(self) -> str:
        return self._source_combo.currentData()
    
    def set_source_language(self, lang: str) -> None:
        for i in range(self._source_combo.count()):
            if self._source_combo.itemData(i) == lang:
                self._source_combo.setCurrentIndex(i)
                break
    
    def get_target_language(self) -> str:
        return self._target_combo.currentData()
    
    def set_target_language(self, lang: str) -> None:
        for i in range(self._target_combo.count()):
            if self._target_combo.itemData(i) == lang:
                self._target_combo.setCurrentIndex(i)
                break
