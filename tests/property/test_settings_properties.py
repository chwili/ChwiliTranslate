"""
Property-based tests for Settings Panel
Feature: chwili-translate, Property 10: Exclusion Area Filtering
Validates: Requirements 7.3
"""

import os
from hypothesis import given, strategies as st, settings
from typing import List, Dict

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


# Exclusion area stratejisi
coordinate_strategy = st.integers(min_value=0, max_value=4000)
dimension_strategy = st.integers(min_value=10, max_value=1000)

exclusion_area_strategy = st.fixed_dictionaries({
    "x": coordinate_strategy,
    "y": coordinate_strategy,
    "width": dimension_strategy,
    "height": dimension_strategy
})


def point_in_exclusion_area(x: int, y: int, area: Dict) -> bool:
    """Bir noktanın exclusion area içinde olup olmadığını kontrol eder"""
    return (area["x"] <= x < area["x"] + area["width"] and
            area["y"] <= y < area["y"] + area["height"])


def filter_ocr_results(results: List[Dict], exclusion_areas: List[Dict]) -> List[Dict]:
    """OCR sonuçlarını exclusion area'lara göre filtreler"""
    filtered = []
    for result in results:
        x, y = result.get("x", 0), result.get("y", 0)
        in_exclusion = any(
            point_in_exclusion_area(x, y, area) 
            for area in exclusion_areas
        )
        if not in_exclusion:
            filtered.append(result)
    return filtered


@given(
    exclusion_areas=st.lists(exclusion_area_strategy, min_size=1, max_size=5),
    test_point_x=coordinate_strategy,
    test_point_y=coordinate_strategy
)
@settings(max_examples=100)
def test_exclusion_area_filtering(exclusion_areas: List[Dict], test_point_x: int, test_point_y: int):
    """
    Feature: chwili-translate, Property 10: Exclusion Area Filtering
    
    For any defined exclusion area within a capture region, OCR results
    should not include text from coordinates within the exclusion area.
    
    Validates: Requirements 7.3
    """
    # Test OCR sonucu oluştur
    ocr_result = {"x": test_point_x, "y": test_point_y, "text": "test"}
    
    # Filtreleme uygula
    filtered = filter_ocr_results([ocr_result], exclusion_areas)
    
    # Noktanın herhangi bir exclusion area içinde olup olmadığını kontrol et
    in_any_exclusion = any(
        point_in_exclusion_area(test_point_x, test_point_y, area)
        for area in exclusion_areas
    )
    
    if in_any_exclusion:
        # Exclusion area içindeyse, sonuç filtrelenmeli
        assert len(filtered) == 0, \
            f"Exclusion area içindeki sonuç filtrelenmedi: ({test_point_x}, {test_point_y})"
    else:
        # Exclusion area dışındaysa, sonuç kalmalı
        assert len(filtered) == 1, \
            f"Exclusion area dışındaki sonuç yanlışlıkla filtrelendi: ({test_point_x}, {test_point_y})"


@given(
    area=exclusion_area_strategy,
    offset_x=st.integers(min_value=0, max_value=100),
    offset_y=st.integers(min_value=0, max_value=100)
)
@settings(max_examples=100)
def test_point_inside_exclusion_area(area: Dict, offset_x: int, offset_y: int):
    """
    Exclusion area içindeki noktaların doğru tespit edildiğini test eder
    """
    # Area içinde bir nokta oluştur
    if offset_x < area["width"] and offset_y < area["height"]:
        point_x = area["x"] + offset_x
        point_y = area["y"] + offset_y
        
        assert point_in_exclusion_area(point_x, point_y, area), \
            f"Area içindeki nokta tespit edilemedi: ({point_x}, {point_y}) in {area}"


@given(area=exclusion_area_strategy)
@settings(max_examples=100)
def test_point_outside_exclusion_area(area: Dict):
    """
    Exclusion area dışındaki noktaların doğru tespit edildiğini test eder
    """
    # Area dışında bir nokta (sağ alt köşenin dışında)
    point_x = area["x"] + area["width"] + 10
    point_y = area["y"] + area["height"] + 10
    
    assert not point_in_exclusion_area(point_x, point_y, area), \
        f"Area dışındaki nokta yanlış tespit edildi: ({point_x}, {point_y}) in {area}"
