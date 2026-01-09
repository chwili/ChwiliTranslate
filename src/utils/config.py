"""
Config Manager for ChwiliTranslate
JSON-based configuration loading/saving with default config creation.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class OCRConfig:
    """OCR Engine configuration"""
    speed: str = "normal"  # fast, normal, accurate
    gpu_enabled: bool = True
    languages: List[str] = field(default_factory=lambda: ["en"])  # Sadece İngilizce varsayılan
    confidence_threshold: float = 0.7


@dataclass
class TranslationConfig:
    """Translation Engine configuration"""
    provider: str = "gemini"  # chatgpt, gemini, google, deepl
    source_language: str = "en"
    target_language: str = "tr"
    api_keys: Dict[str, str] = field(default_factory=lambda: {
        "chatgpt": "",
        "gemini": "",
        "google": "",
        "deepl": ""
    })


@dataclass
class OverlayPosition:
    """Overlay position"""
    x: int = 100
    y: int = 100


@dataclass
class OverlayConfig:
    """Overlay Renderer configuration"""
    opacity: float = 0.85
    font_size: int = 16
    font_family: str = "Segoe UI"
    background_blur: bool = True
    glow_effect: bool = False
    text_shadow: bool = True
    bold: bool = False
    italic: bool = False
    text_color: str = "#ffffff"
    bg_color: str = "#000000"
    glow_color: str = "#00d4ff"
    position: OverlayPosition = field(default_factory=OverlayPosition)


@dataclass
class SystemConfig:
    """System settings configuration"""
    cache_enabled: bool = True
    selected_monitor: int = 0
    exclusion_areas: List[Dict] = field(default_factory=list)


@dataclass
class RegionConfig:
    """Capture region configuration"""
    x: int = 0
    y: int = 0
    width: int = 800
    height: int = 600
    monitor_id: int = 0
    name: str = ""
    enabled: bool = True


@dataclass
class RegionsConfig:
    """Multiple capture regions configuration"""
    regions: List[Dict] = field(default_factory=list)  # List of RegionConfig as dicts


@dataclass
class AppConfig:
    """Main application configuration"""
    ocr: OCRConfig = field(default_factory=OCRConfig)
    translation: TranslationConfig = field(default_factory=TranslationConfig)
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    system: SystemConfig = field(default_factory=SystemConfig)
    region: RegionConfig = field(default_factory=RegionConfig)  # Geriye uyumluluk
    regions: RegionsConfig = field(default_factory=RegionsConfig)  # Çoklu bölge


class ConfigManager:
    """JSON-based configuration manager"""
    
    DEFAULT_CONFIG_PATH = "config.json"
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize config manager with optional custom path"""
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Optional[AppConfig] = None
    
    def _config_to_dict(self, config: AppConfig) -> dict:
        """Convert AppConfig to dictionary for JSON serialization"""
        return {
            "ocr": asdict(config.ocr),
            "translation": asdict(config.translation),
            "overlay": {
                "opacity": config.overlay.opacity,
                "font_size": config.overlay.font_size,
                "font_family": config.overlay.font_family,
                "background_blur": config.overlay.background_blur,
                "glow_effect": config.overlay.glow_effect,
                "text_shadow": config.overlay.text_shadow,
                "bold": config.overlay.bold,
                "italic": config.overlay.italic,
                "text_color": config.overlay.text_color,
                "bg_color": config.overlay.bg_color,
                "glow_color": config.overlay.glow_color,
                "position": asdict(config.overlay.position)
            },
            "system": asdict(config.system),
            "region": asdict(config.region),
            "regions": asdict(config.regions)
        }

    
    def _dict_to_config(self, data: dict) -> AppConfig:
        """Convert dictionary to AppConfig"""
        ocr_data = data.get("ocr", {})
        ocr = OCRConfig(
            speed=ocr_data.get("speed", "normal"),
            gpu_enabled=ocr_data.get("gpu_enabled", True),
            languages=ocr_data.get("languages", ["en", "ja", "ko", "zh"]),
            confidence_threshold=ocr_data.get("confidence_threshold", 0.7)
        )
        
        trans_data = data.get("translation", {})
        translation = TranslationConfig(
            provider=trans_data.get("provider", "gemini"),
            source_language=trans_data.get("source_language", "en"),
            target_language=trans_data.get("target_language", "tr"),
            api_keys=trans_data.get("api_keys", {
                "chatgpt": "", "gemini": "", "google": "", "deepl": ""
            })
        )
        
        overlay_data = data.get("overlay", {})
        position_data = overlay_data.get("position", {})
        overlay = OverlayConfig(
            opacity=overlay_data.get("opacity", 0.85),
            font_size=overlay_data.get("font_size", 16),
            font_family=overlay_data.get("font_family", "Segoe UI"),
            background_blur=overlay_data.get("background_blur", True),
            glow_effect=overlay_data.get("glow_effect", False),
            text_shadow=overlay_data.get("text_shadow", True),
            bold=overlay_data.get("bold", False),
            italic=overlay_data.get("italic", False),
            text_color=overlay_data.get("text_color", "#ffffff"),
            bg_color=overlay_data.get("bg_color", "#000000"),
            glow_color=overlay_data.get("glow_color", "#00d4ff"),
            position=OverlayPosition(
                x=position_data.get("x", 100),
                y=position_data.get("y", 100)
            )
        )
        
        system_data = data.get("system", {})
        system = SystemConfig(
            cache_enabled=system_data.get("cache_enabled", True),
            selected_monitor=system_data.get("selected_monitor", 0),
            exclusion_areas=system_data.get("exclusion_areas", [])
        )
        
        region_data = data.get("region", {})
        region = RegionConfig(
            x=region_data.get("x", 0),
            y=region_data.get("y", 0),
            width=region_data.get("width", 800),
            height=region_data.get("height", 600),
            monitor_id=region_data.get("monitor_id", 0),
            name=region_data.get("name", ""),
            enabled=region_data.get("enabled", True)
        )
        
        # Çoklu bölge
        regions_data = data.get("regions", {})
        regions = RegionsConfig(
            regions=regions_data.get("regions", [])
        )
        
        return AppConfig(
            ocr=ocr,
            translation=translation,
            overlay=overlay,
            system=system,
            region=region,
            regions=regions
        )

    
    def create_default_config(self) -> AppConfig:
        """Create and return default configuration"""
        return AppConfig()
    
    def load(self) -> AppConfig:
        """Load configuration from file, create default if not exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._config = self._dict_to_config(data)
            except (json.JSONDecodeError, IOError):
                self._config = self.create_default_config()
                self.save(self._config)
        else:
            self._config = self.create_default_config()
            self.save(self._config)
        
        return self._config
    
    def save(self, config: AppConfig) -> None:
        """Save configuration to file"""
        self._config = config
        data = self._config_to_dict(config)
        
        # Ensure directory exists
        config_dir = os.path.dirname(self.config_path)
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_config(self) -> AppConfig:
        """Get current configuration, load if not loaded"""
        if self._config is None:
            return self.load()
        return self._config
    
    def update_ocr(self, **kwargs) -> None:
        """Update OCR configuration"""
        config = self.get_config()
        for key, value in kwargs.items():
            if hasattr(config.ocr, key):
                setattr(config.ocr, key, value)
        self.save(config)
    
    def update_translation(self, **kwargs) -> None:
        """Update translation configuration"""
        config = self.get_config()
        for key, value in kwargs.items():
            if hasattr(config.translation, key):
                setattr(config.translation, key, value)
        self.save(config)
    
    def update_overlay(self, **kwargs) -> None:
        """Update overlay configuration"""
        config = self.get_config()
        for key, value in kwargs.items():
            if hasattr(config.overlay, key):
                setattr(config.overlay, key, value)
        self.save(config)
    
    def update_region(self, **kwargs) -> None:
        """Update region configuration"""
        config = self.get_config()
        for key, value in kwargs.items():
            if hasattr(config.region, key):
                setattr(config.region, key, value)
        self.save(config)
    
    def update_regions(self, regions: List[Dict]) -> None:
        """Update multiple regions configuration"""
        config = self.get_config()
        config.regions.regions = regions
        self.save(config)
    
    def get_regions(self) -> List[Dict]:
        """Get saved regions"""
        config = self.get_config()
        return config.regions.regions
