"""
Property-based tests for Region Selector
Feature: chwili-translate, Property 3: Region Coordinate Persistence
Validates: Requirements 2.2
"""

import os
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ocr.region_selector import Region, RegionSelector


# Stratejiler
coordinate_strategy = st.integers(min_value=0, max_value=4000)
dimension_strategy = st.integers(min_value=1, max_value=4000)
monitor_strategy = st.integers(min_value=0, max_value=10)


@given(
    x=coordinate_strategy,
    y=coordinate_strategy,
    width=dimension_strategy,
    height=dimension_strategy,
    monitor_id=monitor_strategy
)
@settings(max_examples=100)
def test_region_coordinate_persistence(x: int, y: int, width: int, height: int, monitor_id: int):
    """
    Feature: chwili-translate, Property 3: Region Coordinate Persistence
    
    For any valid Region with x, y, width, height, and monitor_id values,
    when saved through the Region_Selector, retrieving the region should
    return coordinates equal to the original values.
    
    Validates: Requirements 2.2
    """
    # Region oluştur
    original_region = Region(
        x=x,
        y=y,
        width=width,
        height=height,
        monitor_id=monitor_id
    )
    
    # RegionSelector'a kaydet
    selector = RegionSelector()
    selector.set_region(original_region)
    
    # Geri oku
    retrieved_region = selector.get_current_region()
    
    # Koordinatların korunduğunu doğrula
    assert retrieved_region is not None, "Region bulunamadı"
    assert retrieved_region.x == x, f"x koordinatı farklı: {retrieved_region.x} != {x}"
    assert retrieved_region.y == y, f"y koordinatı farklı: {retrieved_region.y} != {y}"
    assert retrieved_region.width == width, f"width farklı: {retrieved_region.width} != {width}"
    assert retrieved_region.height == height, f"height farklı: {retrieved_region.height} != {height}"
    assert retrieved_region.monitor_id == monitor_id, f"monitor_id farklı: {retrieved_region.monitor_id} != {monitor_id}"


@given(
    x=coordinate_strategy,
    y=coordinate_strategy,
    width=dimension_strategy,
    height=dimension_strategy,
    monitor_id=monitor_strategy
)
@settings(max_examples=100)
def test_region_dict_round_trip(x: int, y: int, width: int, height: int, monitor_id: int):
    """
    Region dictionary round-trip testi
    """
    # Region oluştur
    original = Region(x=x, y=y, width=width, height=height, monitor_id=monitor_id)
    
    # Dictionary'e çevir
    data = original.to_dict()
    
    # Dictionary'den geri oluştur
    restored = Region.from_dict(data)
    
    # Eşitliği doğrula
    assert restored.x == original.x
    assert restored.y == original.y
    assert restored.width == original.width
    assert restored.height == original.height
    assert restored.monitor_id == original.monitor_id


@given(
    width=dimension_strategy,
    height=dimension_strategy
)
@settings(max_examples=100)
def test_region_validity(width: int, height: int):
    """
    Region geçerlilik testi
    """
    region = Region(x=0, y=0, width=width, height=height)
    
    # Pozitif boyutlar geçerli olmalı
    assert region.is_valid() == (width > 0 and height > 0)
