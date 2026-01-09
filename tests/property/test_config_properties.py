"""
Property-based tests for Config Manager
Feature: chwili-translate, Property 7: Settings Persistence Round-Trip
Validates: Requirements 7.5
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.config import (
    ConfigManager, AppConfig, OCRConfig, TranslationConfig,
    OverlayConfig, OverlayPosition, SystemConfig, RegionConfig
)


# Strategies for generating valid config values
ocr_speed_strategy = st.sampled_from(["fast", "normal", "accurate"])
provider_strategy = st.sampled_from(["chatgpt", "gemini", "google", "deepl"])
language_strategy = st.sampled_from(["en", "ja", "ko", "zh", "tr", "de", "fr", "es"])
opacity_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
font_size_strategy = st.integers(min_value=8, max_value=72)
coordinate_strategy = st.integers(min_value=0, max_value=4000)
dimension_strategy = st.integers(min_value=100, max_value=4000)
monitor_strategy = st.integers(min_value=0, max_value=10)
confidence_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)


@st.composite
def ocr_config_strategy(draw):
    """Generate valid OCRConfig"""
    return OCRConfig(
        speed=draw(ocr_speed_strategy),
        gpu_enabled=draw(st.booleans()),
        languages=draw(st.lists(language_strategy, min_size=1, max_size=4, unique=True)),
        confidence_threshold=draw(confidence_strategy)
    )


@st.composite
def translation_config_strategy(draw):
    """Generate valid TranslationConfig"""
    return TranslationConfig(
        provider=draw(provider_strategy),
        source_language=draw(language_strategy),
        target_language=draw(language_strategy),
        api_keys={
            "chatgpt": draw(st.text(min_size=0, max_size=50)),
            "gemini": draw(st.text(min_size=0, max_size=50)),
            "google": draw(st.text(min_size=0, max_size=50)),
            "deepl": draw(st.text(min_size=0, max_size=50))
        }
    )


@st.composite
def overlay_config_strategy(draw):
    """Generate valid OverlayConfig"""
    return OverlayConfig(
        opacity=draw(opacity_strategy),
        font_size=draw(font_size_strategy),
        font_family=draw(st.sampled_from(["Segoe UI", "Arial", "Roboto", "Noto Sans"])),
        background_blur=draw(st.booleans()),
        glow_effect=draw(st.booleans()),
        position=OverlayPosition(
            x=draw(coordinate_strategy),
            y=draw(coordinate_strategy)
        )
    )


@st.composite
def system_config_strategy(draw):
    """Generate valid SystemConfig"""
    return SystemConfig(
        cache_enabled=draw(st.booleans()),
        selected_monitor=draw(monitor_strategy),
        exclusion_areas=draw(st.lists(
            st.fixed_dictionaries({
                "x": coordinate_strategy,
                "y": coordinate_strategy,
                "width": dimension_strategy,
                "height": dimension_strategy
            }),
            min_size=0,
            max_size=3
        ))
    )


@st.composite
def region_config_strategy(draw):
    """Generate valid RegionConfig"""
    return RegionConfig(
        x=draw(coordinate_strategy),
        y=draw(coordinate_strategy),
        width=draw(dimension_strategy),
        height=draw(dimension_strategy),
        monitor_id=draw(monitor_strategy)
    )


@st.composite
def app_config_strategy(draw):
    """Generate valid AppConfig"""
    return AppConfig(
        ocr=draw(ocr_config_strategy()),
        translation=draw(translation_config_strategy()),
        overlay=draw(overlay_config_strategy()),
        system=draw(system_config_strategy()),
        region=draw(region_config_strategy())
    )


def configs_equal(c1: AppConfig, c2: AppConfig) -> bool:
    """Compare two AppConfig objects for equality"""
    # OCR
    if c1.ocr.speed != c2.ocr.speed:
        return False
    if c1.ocr.gpu_enabled != c2.ocr.gpu_enabled:
        return False
    if set(c1.ocr.languages) != set(c2.ocr.languages):
        return False
    if abs(c1.ocr.confidence_threshold - c2.ocr.confidence_threshold) > 1e-6:
        return False
    
    # Translation
    if c1.translation.provider != c2.translation.provider:
        return False
    if c1.translation.source_language != c2.translation.source_language:
        return False
    if c1.translation.target_language != c2.translation.target_language:
        return False
    if c1.translation.api_keys != c2.translation.api_keys:
        return False
    
    # Overlay
    if abs(c1.overlay.opacity - c2.overlay.opacity) > 1e-6:
        return False
    if c1.overlay.font_size != c2.overlay.font_size:
        return False
    if c1.overlay.font_family != c2.overlay.font_family:
        return False
    if c1.overlay.background_blur != c2.overlay.background_blur:
        return False
    if c1.overlay.glow_effect != c2.overlay.glow_effect:
        return False
    if c1.overlay.position.x != c2.overlay.position.x:
        return False
    if c1.overlay.position.y != c2.overlay.position.y:
        return False
    
    # System
    if c1.system.cache_enabled != c2.system.cache_enabled:
        return False
    if c1.system.selected_monitor != c2.system.selected_monitor:
        return False
    if c1.system.exclusion_areas != c2.system.exclusion_areas:
        return False
    
    # Region
    if c1.region.x != c2.region.x:
        return False
    if c1.region.y != c2.region.y:
        return False
    if c1.region.width != c2.region.width:
        return False
    if c1.region.height != c2.region.height:
        return False
    if c1.region.monitor_id != c2.region.monitor_id:
        return False
    
    return True


@given(config=app_config_strategy())
@settings(max_examples=100)
def test_config_round_trip(config: AppConfig):
    """
    Feature: chwili-translate, Property 7: Settings Persistence Round-Trip
    
    For any valid AppConfig object, when saved to configuration and then loaded,
    the loaded configuration should be equivalent to the original.
    
    Validates: Requirements 7.5
    """
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Save the config
        manager = ConfigManager(config_path=temp_path)
        manager.save(config)
        
        # Load it back with a new manager instance
        manager2 = ConfigManager(config_path=temp_path)
        loaded_config = manager2.load()
        
        # Verify round-trip consistency
        assert configs_equal(config, loaded_config), \
            f"Config round-trip failed: original != loaded"
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)
