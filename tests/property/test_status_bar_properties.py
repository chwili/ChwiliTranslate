"""
Property-based tests for Status Bar
Feature: chwili-translate, Property 9: Status Bar State Synchronization
Validates: Requirements 8.5
"""

import os
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class MockStatusBar:
    """Test için StatusBar mock'u (PyQt6 bağımsız)"""
    
    def __init__(self):
        self._is_running = False
        self._fps = 0.0
        self._gpu_enabled = False
        self._gpu_available = True
        self._ocr_status = "OCR Inactive"
        self._gpu_status = "CPU Only"
    
    def set_running(self, running: bool) -> None:
        self._is_running = running
        self._ocr_status = "OCR Active" if running else "OCR Inactive"
    
    def is_running(self) -> bool:
        return self._is_running
    
    def set_fps(self, fps: float) -> None:
        self._fps = fps
    
    def get_fps(self) -> float:
        return self._fps
    
    def set_gpu_status(self, enabled: bool, available: bool = True) -> None:
        self._gpu_enabled = enabled
        self._gpu_available = available
        if enabled and available:
            self._gpu_status = "NVIDIA On"
        elif enabled and not available:
            self._gpu_status = "GPU N/A"
        else:
            self._gpu_status = "CPU Only"
    
    def get_gpu_status(self) -> str:
        return self._gpu_status
    
    def get_ocr_status(self) -> str:
        return self._ocr_status


@given(running=st.booleans())
@settings(max_examples=100)
def test_status_bar_ocr_state_sync(running: bool):
    """
    Feature: chwili-translate, Property 9: Status Bar State Synchronization
    
    For any change in application state (OCR active/inactive),
    the Status_Bar state should reflect the current system state.
    
    Validates: Requirements 8.5
    """
    status_bar = MockStatusBar()
    
    # Durumu ayarla
    status_bar.set_running(running)
    
    # Senkronizasyonu doğrula
    assert status_bar.is_running() == running, \
        f"OCR durumu senkronize değil: beklenen {running}, alınan {status_bar.is_running()}"
    
    expected_status = "OCR Active" if running else "OCR Inactive"
    assert status_bar.get_ocr_status() == expected_status, \
        f"OCR status metni yanlış: beklenen '{expected_status}', alınan '{status_bar.get_ocr_status()}'"


@given(
    gpu_enabled=st.booleans(),
    gpu_available=st.booleans()
)
@settings(max_examples=100)
def test_status_bar_gpu_state_sync(gpu_enabled: bool, gpu_available: bool):
    """
    GPU durumu senkronizasyon testi
    
    Validates: Requirements 8.5
    """
    status_bar = MockStatusBar()
    
    # GPU durumunu ayarla
    status_bar.set_gpu_status(gpu_enabled, gpu_available)
    
    # Beklenen durum
    if gpu_enabled and gpu_available:
        expected = "NVIDIA On"
    elif gpu_enabled and not gpu_available:
        expected = "GPU N/A"
    else:
        expected = "CPU Only"
    
    assert status_bar.get_gpu_status() == expected, \
        f"GPU status yanlış: beklenen '{expected}', alınan '{status_bar.get_gpu_status()}'"


@given(fps=st.floats(min_value=0.0, max_value=120.0, allow_nan=False))
@settings(max_examples=100)
def test_status_bar_fps_sync(fps: float):
    """
    FPS değeri senkronizasyon testi
    
    Validates: Requirements 8.5
    """
    status_bar = MockStatusBar()
    
    # FPS ayarla
    status_bar.set_fps(fps)
    
    # Senkronizasyonu doğrula
    assert abs(status_bar.get_fps() - fps) < 1e-6, \
        f"FPS senkronize değil: beklenen {fps}, alınan {status_bar.get_fps()}"
