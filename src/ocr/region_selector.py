"""
Region Selector for ChwiliTranslate
Ekran bölgesi seçim aracı - Çoklu bölge desteği
"""

from dataclasses import dataclass, field
from typing import Optional, List, Callable, Dict
import io


@dataclass
class Region:
    """Ekran bölgesi"""
    x: int
    y: int
    width: int
    height: int
    monitor_id: int = 0
    name: str = ""  # Bölge adı (opsiyonel)
    enabled: bool = True  # Bölge aktif mi?
    
    def to_dict(self) -> Dict:
        """Dictionary'e çevirir"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "monitor_id": self.monitor_id,
            "name": self.name,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Region":
        """Dictionary'den oluşturur"""
        return cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 800),
            height=data.get("height", 600),
            monitor_id=data.get("monitor_id", 0),
            name=data.get("name", ""),
            enabled=data.get("enabled", True)
        )
    
    def is_valid(self) -> bool:
        """Bölgenin geçerli olup olmadığını kontrol eder"""
        return self.width > 0 and self.height > 0


class RegionSelector:
    """Ekran bölgesi seçim aracı - Çoklu bölge desteği"""
    
    MAX_REGIONS = 5  # Maksimum bölge sayısı
    
    def __init__(self):
        """Region Selector'ı başlatır"""
        self._current_region: Optional[Region] = None
        self._regions: List[Region] = []  # Çoklu bölge listesi
        self._monitors: List[Dict] = []
        self._on_complete_callback: Optional[Callable[[Region], None]] = None
        self._is_selecting = False
        self._selecting_index: int = -1  # Hangi bölge için seçim yapılıyor (-1 = yeni)
    
    def get_monitors(self) -> List[Dict]:
        """Mevcut monitörleri listeler"""
        try:
            import mss
            with mss.mss() as sct:
                monitors = []
                for i, mon in enumerate(sct.monitors[1:], start=0):  # İlki tüm ekranlar
                    monitors.append({
                        "id": i,
                        "left": mon["left"],
                        "top": mon["top"],
                        "width": mon["width"],
                        "height": mon["height"],
                        "name": f"Monitor {i + 1}"
                    })
                self._monitors = monitors
                return monitors
        except ImportError:
            return [{"id": 0, "left": 0, "top": 0, "width": 1920, "height": 1080, "name": "Default"}]

    
    def start_selection(self, on_complete: Callable[[Region], None], index: int = -1) -> None:
        """Bölge seçim modunu başlatır
        
        Args:
            on_complete: Seçim tamamlandığında çağrılacak callback
            index: Düzenlenecek bölge indeksi (-1 = yeni bölge)
        """
        self._on_complete_callback = on_complete
        self._is_selecting = True
        self._selecting_index = index
    
    def complete_selection(self, region: Region) -> None:
        """Seçimi tamamlar"""
        if self._selecting_index >= 0 and self._selecting_index < len(self._regions):
            # Mevcut bölgeyi güncelle
            self._regions[self._selecting_index] = region
        else:
            # Yeni bölge ekle
            if len(self._regions) < self.MAX_REGIONS:
                if not region.name:
                    region.name = f"Bölge {len(self._regions) + 1}"
                self._regions.append(region)
        
        # Geriye uyumluluk için current_region'ı da güncelle
        self._current_region = region
        self._is_selecting = False
        self._selecting_index = -1
        
        if self._on_complete_callback:
            self._on_complete_callback(region)
    
    def cancel_selection(self) -> None:
        """Seçimi iptal eder"""
        self._is_selecting = False
        self._selecting_index = -1
        self._on_complete_callback = None
    
    def is_selecting(self) -> bool:
        """Seçim modunda mı döndürür"""
        return self._is_selecting
    
    # Çoklu bölge metodları
    def get_regions(self) -> List[Region]:
        """Tüm bölgeleri döndürür"""
        return self._regions.copy()
    
    def get_enabled_regions(self) -> List[Region]:
        """Sadece aktif bölgeleri döndürür"""
        return [r for r in self._regions if r.enabled]
    
    def get_region(self, index: int) -> Optional[Region]:
        """Belirtilen indeksteki bölgeyi döndürür"""
        if 0 <= index < len(self._regions):
            return self._regions[index]
        return None
    
    def add_region(self, region: Region) -> bool:
        """Yeni bölge ekler"""
        if len(self._regions) >= self.MAX_REGIONS:
            return False
        if not region.name:
            region.name = f"Bölge {len(self._regions) + 1}"
        self._regions.append(region)
        return True
    
    def remove_region(self, index: int) -> bool:
        """Bölgeyi kaldırır"""
        if 0 <= index < len(self._regions):
            self._regions.pop(index)
            return True
        return False
    
    def set_region_enabled(self, index: int, enabled: bool) -> None:
        """Bölgenin aktifliğini ayarlar"""
        if 0 <= index < len(self._regions):
            self._regions[index].enabled = enabled
    
    def set_regions(self, regions: List[Region]) -> None:
        """Tüm bölgeleri ayarlar"""
        self._regions = regions[:self.MAX_REGIONS]
    
    def clear_regions(self) -> None:
        """Tüm bölgeleri temizler"""
        self._regions.clear()
        self._current_region = None
    
    def get_region_count(self) -> int:
        """Bölge sayısını döndürür"""
        return len(self._regions)
    
    def can_add_region(self) -> bool:
        """Yeni bölge eklenebilir mi"""
        return len(self._regions) < self.MAX_REGIONS
    
    # Geriye uyumluluk
    def get_current_region(self) -> Optional[Region]:
        """Mevcut seçili bölgeyi döndürür (geriye uyumluluk)"""
        # Aktif bölgeler varsa ilkini döndür
        enabled = self.get_enabled_regions()
        if enabled:
            return enabled[0]
        return self._current_region
    
    def set_region(self, region: Region) -> None:
        """Bölgeyi ayarlar (geriye uyumluluk)"""
        self._current_region = region
        # Eğer bölge listesi boşsa ekle
        if not self._regions:
            self.add_region(region)
    
    def capture_region(self, region: Optional[Region] = None) -> bytes:
        """Belirtilen bölgenin ekran görüntüsünü alır"""
        target_region = region or self._current_region
        
        if not target_region:
            raise ValueError("Bölge belirtilmedi")
        
        try:
            import mss
            from PIL import Image
            
            with mss.mss() as sct:
                # Monitör offset'ini hesapla
                monitors = self.get_monitors()
                monitor_offset_x = 0
                monitor_offset_y = 0
                
                if target_region.monitor_id < len(monitors):
                    mon = monitors[target_region.monitor_id]
                    monitor_offset_x = mon["left"]
                    monitor_offset_y = mon["top"]
                
                # Yakalama alanı
                monitor = {
                    "left": monitor_offset_x + target_region.x,
                    "top": monitor_offset_y + target_region.y,
                    "width": target_region.width,
                    "height": target_region.height
                }
                
                # Ekran görüntüsü al
                screenshot = sct.grab(monitor)
                
                # PIL Image'e çevir
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Bytes'a çevir
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                return buffer.getvalue()
                
        except ImportError:
            raise ImportError("mss veya Pillow yüklü değil")
    
    def capture_full_screen(self, monitor_id: int = 0) -> bytes:
        """Tam ekran görüntüsü alır"""
        monitors = self.get_monitors()
        
        if monitor_id >= len(monitors):
            monitor_id = 0
        
        mon = monitors[monitor_id]
        region = Region(
            x=0,
            y=0,
            width=mon["width"],
            height=mon["height"],
            monitor_id=monitor_id
        )
        
        return self.capture_region(region)
