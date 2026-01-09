"""
Property-based tests for Overlay Window
Feature: chwili-translate, Property 5: Overlay Configuration Application
Validates: Requirements 5.3, 5.4
"""

import os
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.overlay.overlay_window import OverlayWindow, OverlayConfig


# Stratejiler
opacity_strategy = st.floats(min_value=0.0, max_value=1.0, allow_nan=False)
font_size_strategy = st.integers(min_value=8, max_value=72)
font_family_strategy = st.sampled_from(["Segoe UI", "Arial", "Roboto", "Noto Sans", "Consolas"])
coordinate_strategy = st.integers(min_value=0, max_value=4000)
dimension_strategy = st.integers(min_value=50, max_value=2000)


@given(
    opacity=opacity_strategy,
    font_size=font_size_strategy
)
@settings(max_examples=100)
def test_overlay_configuration_application(opacity: float, font_size: int):
    """
    Feature: chwili-translate, Property 5: Overlay Configuration Application
    
    For any valid opacity value (0.0-1.0) and font size (positive integer),
    when applied to the Overlay_Renderer, the overlay's configuration should
    reflect those exact values.
    
    Validates: Requirements 5.3, 5.4
    """
    overlay = OverlayWindow()
    
    # Opacity ayarla
    overlay.set_opacity(opacity)
    configured_opacity = overlay.get_opacity()
    
    # Font size ayarla
    overlay.set_font_size(font_size)
    configured_font_size = overlay.get_font_size()
    
    # Doğrulama
    assert abs(configured_opacity - opacity) < 1e-6, \
        f"Opacity farklı: beklenen {opacity}, alınan {configured_opacity}"
    assert configured_font_size == font_size, \
        f"Font size farklı: beklenen {font_size}, alınan {configured_font_size}"


@given(font_family=font_family_strategy)
@settings(max_examples=100)
def test_overlay_font_family(font_family: str):
    """
    Overlay font family konfigürasyon testi
    """
    overlay = OverlayWindow()
    
    overlay.set_font_family(font_family)
    configured = overlay.get_font_family()
    
    assert configured == font_family, \
        f"Font family farklı: beklenen {font_family}, alınan {configured}"


@given(
    x=coordinate_strategy,
    y=coordinate_strategy
)
@settings(max_examples=100)
def test_overlay_position(x: int, y: int):
    """
    Overlay pozisyon konfigürasyon testi
    """
    overlay = OverlayWindow()
    
    overlay.set_position(x, y)
    pos_x, pos_y = overlay.get_position()
    
    assert pos_x == x, f"X pozisyonu farklı: beklenen {x}, alınan {pos_x}"
    assert pos_y == y, f"Y pozisyonu farklı: beklenen {y}, alınan {pos_y}"


@given(
    width=dimension_strategy,
    height=dimension_strategy
)
@settings(max_examples=100)
def test_overlay_size(width: int, height: int):
    """
    Overlay boyut konfigürasyon testi
    """
    overlay = OverlayWindow()
    
    overlay.set_size(width, height)
    w, h = overlay.get_size()
    
    assert w == width, f"Width farklı: beklenen {width}, alınan {w}"
    assert h == height, f"Height farklı: beklenen {height}, alınan {h}"


@given(
    blur=st.booleans(),
    glow=st.booleans()
)
@settings(max_examples=100)
def test_overlay_effects(blur: bool, glow: bool):
    """
    Overlay efekt konfigürasyon testi
    """
    overlay = OverlayWindow()
    
    overlay.set_background_blur(blur)
    overlay.set_glow_effect(glow)
    
    assert overlay.get_background_blur() == blur
    assert overlay.get_glow_effect() == glow
