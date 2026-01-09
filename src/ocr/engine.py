"""
OCR Engine for ChwiliTranslate
EasyOCR tabanlı metin tanıma motoru
"""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from enum import Enum
import time


class OCRSpeed(Enum):
    """OCR hız modu"""
    FAST = "fast"
    NORMAL = "normal"
    ACCURATE = "accurate"


@dataclass
class OCRConfig:
    """OCR konfigürasyonu"""
    speed: OCRSpeed = OCRSpeed.NORMAL
    gpu_enabled: bool = True
    languages: List[str] = field(default_factory=lambda: ["en"])  # Sadece İngilizce varsayılan
    confidence_threshold: float = 0.7


@dataclass
class OCRResult:
    """OCR sonucu"""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    timestamp: float


class OCREngine:
    """EasyOCR tabanlı metin tanıma motoru"""
    
    def __init__(self, config: Optional[OCRConfig] = None):
        """OCR motorunu başlatır"""
        self._config = config or OCRConfig()
        self._reader = None
        self._gpu_available = False
        self._initialized = False
    
    def _init_reader(self) -> None:
        """EasyOCR reader'ı başlatır"""
        try:
            import easyocr
            
            # GPU kontrolü
            self._gpu_available = self._check_gpu()
            use_gpu = self._config.gpu_enabled and self._gpu_available
            
            self._reader = easyocr.Reader(
                self._config.languages,
                gpu=use_gpu
            )
            self._initialized = True
        except ImportError:
            raise ImportError("EasyOCR yüklü değil. 'pip install easyocr' ile yükleyin.")
        except Exception as e:
            raise Exception(f"OCR başlatma hatası: {e}")

    
    def _check_gpu(self) -> bool:
        """GPU kullanılabilirliğini kontrol eder"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def set_languages(self, languages: List[str]) -> None:
        """OCR dillerini ayarlar"""
        # Desteklenen dilleri filtrele
        supported = ["en", "ja", "ko", "tr", "de", "fr", "es", "it", "pt", "ru"]
        valid_langs = [l for l in languages if l in supported]
        if not valid_langs:
            valid_langs = ["en"]
        
        if set(valid_langs) != set(self._config.languages):
            self._config.languages = valid_langs
            self._initialized = False  # Yeniden başlatma gerekli
    
    def get_languages(self) -> List[str]:
        """Mevcut dil listesini döndürür"""
        return self._config.languages.copy()
    
    def set_speed(self, speed: OCRSpeed) -> None:
        """OCR hızını ayarlar"""
        self._config.speed = speed
    
    def get_speed(self) -> OCRSpeed:
        """Mevcut hız modunu döndürür"""
        return self._config.speed
    
    def enable_gpu(self, enabled: bool) -> None:
        """GPU hızlandırmayı açar/kapatır"""
        if enabled != self._config.gpu_enabled:
            self._config.gpu_enabled = enabled
            self._initialized = False  # Yeniden başlatma gerekli
    
    def is_gpu_enabled(self) -> bool:
        """GPU etkin mi döndürür"""
        return self._config.gpu_enabled
    
    def is_gpu_available(self) -> bool:
        """GPU kullanılabilir mi döndürür"""
        return self._gpu_available
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """Güven eşiğini ayarlar"""
        self._config.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def get_confidence_threshold(self) -> float:
        """Güven eşiğini döndürür"""
        return self._config.confidence_threshold
    
    def get_config(self) -> OCRConfig:
        """Mevcut konfigürasyonu döndürür"""
        return OCRConfig(
            speed=self._config.speed,
            gpu_enabled=self._config.gpu_enabled,
            languages=self._config.languages.copy(),
            confidence_threshold=self._config.confidence_threshold
        )

    
    def process_image(self, image: bytes) -> OCRResult:
        """Görüntüden metin çıkarır"""
        if not self._initialized:
            self._init_reader()
        
        start_time = time.time()
        
        try:
            # EasyOCR ile metin tanıma
            results = self._reader.readtext(image)
            
            # Sonuçları işle
            texts = []
            confidences = []
            boxes = []
            
            for result in results:
                bbox, text, conf = result
                # Düşük eşik kullan - daha fazla metin yakala
                if conf >= 0.3:  # Düşük eşik
                    texts.append(text)
                    confidences.append(conf)
                    # Bounding box'ı tuple'a çevir
                    if bbox:
                        x_coords = [p[0] for p in bbox]
                        y_coords = [p[1] for p in bbox]
                        boxes.append((
                            int(min(x_coords)),
                            int(min(y_coords)),
                            int(max(x_coords)),
                            int(max(y_coords))
                        ))
            
            combined_text = " ".join(texts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=combined_text,
                confidence=avg_confidence,
                bounding_boxes=boxes,
                timestamp=time.time() - start_time
            )
            
        except Exception as e:
            print(f"OCR exception: {e}")
            return OCRResult(
                text="",
                confidence=0.0,
                bounding_boxes=[],
                timestamp=time.time() - start_time
            )
    
    def is_initialized(self) -> bool:
        """Motor başlatıldı mı döndürür"""
        return self._initialized
