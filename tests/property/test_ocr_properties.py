"""
Property-based tests for OCR Engine
Feature: chwili-translate, Property 4: OCR Engine Language Configuration
Validates: Requirements 1.1, 10.3
"""

import os
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ocr.engine import OCREngine, OCRConfig, OCRSpeed


# Stratejiler
language_strategy = st.sampled_from(["en", "ja", "ko", "zh", "tr", "de", "fr", "es"])
speed_strategy = st.sampled_from(list(OCRSpeed))
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


@given(languages=st.lists(language_strategy, min_size=1, max_size=4, unique=True))
@settings(max_examples=100)
def test_ocr_language_configuration(languages: list):
    """
    Feature: chwili-translate, Property 4: OCR Engine Language Configuration
    
    For any valid list of language codes, when set on the OCR_Engine,
    the engine's language configuration should reflect exactly those languages.
    
    Validates: Requirements 1.1, 10.3
    """
    engine = OCREngine()
    
    # Dilleri ayarla
    engine.set_languages(languages)
    
    # Dilleri geri oku
    configured_languages = engine.get_languages()
    
    # Aynı dillerin ayarlandığını doğrula (sıra önemli değil)
    assert set(configured_languages) == set(languages), \
        f"Dil konfigürasyonu başarısız: beklenen {set(languages)}, alınan {set(configured_languages)}"


@given(speed=speed_strategy)
@settings(max_examples=100)
def test_ocr_speed_configuration(speed: OCRSpeed):
    """
    OCR hız modu konfigürasyon testi
    
    Validates: Requirements 1.4, 1.5
    """
    engine = OCREngine()
    
    # Hızı ayarla
    engine.set_speed(speed)
    
    # Hızı geri oku
    configured_speed = engine.get_speed()
    
    assert configured_speed == speed, \
        f"Hız konfigürasyonu başarısız: beklenen {speed}, alınan {configured_speed}"


@given(threshold=confidence_strategy)
@settings(max_examples=100)
def test_ocr_confidence_threshold(threshold: float):
    """
    OCR güven eşiği konfigürasyon testi
    """
    engine = OCREngine()
    
    # Eşiği ayarla
    engine.set_confidence_threshold(threshold)
    
    # Eşiği geri oku
    configured_threshold = engine.get_confidence_threshold()
    
    # Değerin 0-1 arasında olduğunu doğrula
    assert 0.0 <= configured_threshold <= 1.0
    assert abs(configured_threshold - threshold) < 1e-6, \
        f"Güven eşiği başarısız: beklenen {threshold}, alınan {configured_threshold}"


@given(gpu_enabled=st.booleans())
@settings(max_examples=100)
def test_ocr_gpu_configuration(gpu_enabled: bool):
    """
    OCR GPU konfigürasyon testi
    
    Validates: Requirements 1.3
    """
    engine = OCREngine()
    
    # GPU'yu ayarla
    engine.enable_gpu(gpu_enabled)
    
    # GPU durumunu geri oku
    configured_gpu = engine.is_gpu_enabled()
    
    assert configured_gpu == gpu_enabled, \
        f"GPU konfigürasyonu başarısız: beklenen {gpu_enabled}, alınan {configured_gpu}"
