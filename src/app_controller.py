"""
Application Controller for ChwiliTranslate
Ana uygulama kontrolcüsü
"""

from dataclasses import dataclass
from typing import Optional, Callable
from enum import Enum
import time
import threading
import asyncio
import queue


class AppState(Enum):
    """Uygulama durumu"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class AppConfig:
    """Uygulama konfigürasyonu"""
    ocr_interval_ms: int = 400  # OCR tarama aralığı (0.4 saniye)
    cache_enabled: bool = True
    gpu_enabled: bool = True


class ApplicationController:
    """Ana uygulama kontrolcüsü"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """Application Controller'ı başlatır"""
        self._config = config or AppConfig()
        self._state = AppState.IDLE
        self._fps = 0.0
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._last_text = ""  # Son algılanan metin (tekrar çeviri önleme)
        self._ocr_ready = False  # OCR hazır mı?
        
        # Callbacks
        self._on_text_detected: Optional[Callable[[str], None]] = None
        self._on_translation_complete: Optional[Callable] = None
        self._on_state_changed: Optional[Callable[[AppState], None]] = None
        
        # Hariç tutulan alanlar
        self._exclusion_areas: list = []
        
        # Worker thread
        self._worker_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # UI güncellemeleri için queue
        self._ui_queue: queue.Queue = queue.Queue()
        
        # Bileşenler (lazy initialization)
        self._ocr_engine = None
        self._translation_engine = None
        self._cache_manager = None
        self._region_selector = None
        self._overlay_window = None

    
    def set_ocr_engine(self, engine) -> None:
        """OCR Engine'i ayarlar"""
        self._ocr_engine = engine
    
    def set_translation_engine(self, engine) -> None:
        """Translation Engine'i ayarlar"""
        self._translation_engine = engine
    
    def set_cache_manager(self, cache) -> None:
        """Cache Manager'ı ayarlar"""
        self._cache_manager = cache
    
    def set_region_selector(self, selector) -> None:
        """Region Selector'ı ayarlar"""
        self._region_selector = selector
    
    def set_overlay_window(self, overlay) -> None:
        """Overlay Window'u ayarlar"""
        self._overlay_window = overlay
    
    def set_exclusion_areas(self, areas: list) -> None:
        """Hariç tutulan alanları ayarlar"""
        self._exclusion_areas = areas.copy()
    
    def get_exclusion_areas(self) -> list:
        """Hariç tutulan alanları döndürür"""
        return self._exclusion_areas.copy()
    
    def _is_in_exclusion_area(self, x: int, y: int, w: int, h: int) -> bool:
        """Verilen koordinatların hariç tutulan alanda olup olmadığını kontrol eder"""
        for area in self._exclusion_areas:
            ax, ay = area.get("x", 0), area.get("y", 0)
            aw, ah = area.get("width", 0), area.get("height", 0)
            
            # Dikdörtgen kesişim kontrolü
            if (x < ax + aw and x + w > ax and
                y < ay + ah and y + h > ay):
                return True
        return False
    
    def start(self) -> None:
        """OCR döngüsünü başlatır"""
        if self._state == AppState.RUNNING:
            return
        
        self._state = AppState.RUNNING
        self._stop_event.clear()
        self._frame_count = 0
        self._last_fps_time = time.time()
        self._last_text = ""
        self._ocr_ready = False
        
        # Worker thread başlat
        self._worker_thread = threading.Thread(target=self._ocr_loop, daemon=True)
        self._worker_thread.start()
        
        if self._on_state_changed:
            self._on_state_changed(self._state)
    
    def stop(self) -> None:
        """OCR döngüsünü durdurur"""
        if self._state == AppState.IDLE:
            return
        
        self._stop_event.set()
        
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)
        
        self._state = AppState.IDLE
        self._fps = 0.0
        self._ocr_ready = False
        
        if self._on_state_changed:
            self._on_state_changed(self._state)
    
    def pause(self) -> None:
        """OCR döngüsünü duraklatır"""
        if self._state == AppState.RUNNING:
            self._state = AppState.PAUSED
            if self._on_state_changed:
                self._on_state_changed(self._state)
    
    def resume(self) -> None:
        """OCR döngüsünü devam ettirir"""
        if self._state == AppState.PAUSED:
            self._state = AppState.RUNNING
            if self._on_state_changed:
                self._on_state_changed(self._state)
    
    def get_state(self) -> AppState:
        """Uygulama durumunu döndürür"""
        return self._state
    
    def get_fps(self) -> float:
        """Anlık FPS değerini döndürür"""
        return self._fps

    
    def _ocr_loop(self) -> None:
        """OCR döngüsü (worker thread'de çalışır)"""
        # Overlay'e "Yükleniyor" mesajı gönder
        self._update_overlay("⏳ OCR yükleniyor...")
        
        # OCR engine'i başlat (bu uzun sürebilir)
        try:
            if self._ocr_engine and not self._ocr_engine.is_initialized():
                self._ocr_engine._init_reader()
            self._ocr_ready = True
            self._update_overlay("✅ Hazır - Metin bekleniyor...")
        except Exception as e:
            print(f"OCR başlatma hatası: {e}")
            self._update_overlay(f"❌ OCR hatası: {str(e)[:50]}")
            return
        
        # Ana döngü
        while not self._stop_event.is_set():
            if self._state == AppState.PAUSED:
                time.sleep(0.1)
                continue
            
            start_time = time.time()
            
            try:
                self._process_frame()
            except Exception as e:
                print(f"OCR işleme hatası: {e}")
            
            # FPS hesapla
            self._frame_count += 1
            current_time = time.time()
            elapsed = current_time - self._last_fps_time
            
            if elapsed >= 1.0:
                self._fps = self._frame_count / elapsed
                self._frame_count = 0
                self._last_fps_time = current_time
            
            # Bekleme süresi
            process_time = time.time() - start_time
            wait_time = max(0, (self._config.ocr_interval_ms / 1000.0) - process_time)
            
            if wait_time > 0:
                time.sleep(wait_time)
    
    def _update_overlay(self, text: str) -> None:
        """Overlay'i günceller (thread-safe)"""
        if self._overlay_window:
            # Doğrudan çağır - PyQt bunu handle edecek
            try:
                self._overlay_window.set_text(text)
            except Exception as e:
                print(f"Overlay güncelleme hatası: {e}")
    
    def _process_frame(self) -> None:
        """Tek bir frame işler - tüm aktif bölgeleri tarar"""
        if not self._region_selector or not self._ocr_engine or not self._ocr_ready:
            return
        
        # Tüm aktif bölgeleri al
        regions = self._region_selector.get_enabled_regions()
        if not regions:
            # Geriye uyumluluk - tek bölge
            region = self._region_selector.get_current_region()
            if region:
                regions = [region]
            else:
                return
        
        all_texts = []
        
        for region in regions:
            # Ekran görüntüsü al
            try:
                image_data = self._region_selector.capture_region(region)
            except Exception as e:
                print(f"Ekran yakalama hatası ({region.name}): {e}")
                continue
            
            # OCR işlemi
            try:
                ocr_result = self._ocr_engine.process_image(image_data)
            except Exception as e:
                print(f"OCR hatası ({region.name}): {e}")
                continue
            
            if not ocr_result.text or not ocr_result.text.strip():
                continue
            
            # Hariç tutulan alanları kontrol et
            skip_region = False
            if self._exclusion_areas and ocr_result.bounding_boxes:
                for bbox in ocr_result.bounding_boxes:
                    global_x = region.x + bbox[0]
                    global_y = region.y + bbox[1]
                    box_w = bbox[2] - bbox[0]
                    box_h = bbox[3] - bbox[1]
                    
                    if self._is_in_exclusion_area(global_x, global_y, box_w, box_h):
                        print(f"Metin hariç tutulan alanda, atlanıyor: ({global_x}, {global_y})")
                        skip_region = True
                        break
            
            if skip_region:
                continue
            
            all_texts.append(ocr_result.text.strip())
        
        if not all_texts:
            return
        
        # Tüm metinleri birleştir
        combined_text = " ".join(all_texts)
        
        # Aynı metin tekrar algılandıysa çevirme
        if combined_text == self._last_text:
            return
        
        self._last_text = combined_text
        print(f"OCR algıladı: {combined_text[:100]}")
        
        # Callback
        if self._on_text_detected:
            self._on_text_detected(combined_text)
        
        # Çeviri
        if self._translation_engine:
            self._translate_text(combined_text)
    
    def _translate_text(self, text: str) -> None:
        """Metni çevirir"""
        try:
            # Yeni event loop oluştur ve çalıştır
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    self._translation_engine.translate(text)
                )
            finally:
                loop.close()
            
            # Overlay'e gönder
            if self._overlay_window and result:
                self._update_overlay(result.translated_text)
            
            # Callback
            if self._on_translation_complete:
                self._on_translation_complete(result)
                
        except Exception as e:
            error_msg = str(e)
            print(f"Çeviri hatası: {error_msg}")
            # Hata mesajını overlay'de göster
            if self._overlay_window:
                if "API anahtarı" in error_msg:
                    self._update_overlay("⚠️ API anahtarı ayarlanmamış!")
                else:
                    self._update_overlay(f"⚠️ Çeviri hatası")
    
    def on_text_detected(self, callback: Callable[[str], None]) -> None:
        """Metin algılama callback'i ayarlar"""
        self._on_text_detected = callback
    
    def on_translation_complete(self, callback: Callable) -> None:
        """Çeviri tamamlama callback'i ayarlar"""
        self._on_translation_complete = callback
    
    def on_state_changed(self, callback: Callable[[AppState], None]) -> None:
        """Durum değişikliği callback'i ayarlar"""
        self._on_state_changed = callback
    
    def cleanup(self) -> None:
        """Kaynakları temizler"""
        self.stop()
        self._ocr_engine = None
        self._translation_engine = None
        self._cache_manager = None
        self._region_selector = None
        self._overlay_window = None
        self._ocr_ready = False
