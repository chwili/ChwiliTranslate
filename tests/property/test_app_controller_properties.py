"""
Property-based tests for Application Controller
Feature: chwili-translate, Property 6: Application State Transitions
Validates: Requirements 9.1, 9.3
"""

import os
import time
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.app_controller import ApplicationController, AppState, AppConfig


@given(st.just(True))  # Basit tetikleyici
@settings(max_examples=100)
def test_application_state_transitions(_):
    """
    Feature: chwili-translate, Property 6: Application State Transitions
    
    For any application in IDLE state, calling start() should transition to
    RUNNING state, and calling stop() should transition back to IDLE state.
    
    Validates: Requirements 9.1, 9.3
    """
    controller = ApplicationController()
    
    # Başlangıç durumu IDLE olmalı
    assert controller.get_state() == AppState.IDLE, \
        f"Başlangıç durumu IDLE olmalı, alınan: {controller.get_state()}"
    
    # start() çağrıldığında RUNNING olmalı
    controller.start()
    assert controller.get_state() == AppState.RUNNING, \
        f"start() sonrası RUNNING olmalı, alınan: {controller.get_state()}"
    
    # stop() çağrıldığında IDLE olmalı
    controller.stop()
    assert controller.get_state() == AppState.IDLE, \
        f"stop() sonrası IDLE olmalı, alınan: {controller.get_state()}"


@given(st.just(True))
@settings(max_examples=100)
def test_pause_resume_transitions(_):
    """
    Pause/Resume durum geçişleri testi
    """
    controller = ApplicationController()
    
    # Başlat
    controller.start()
    assert controller.get_state() == AppState.RUNNING
    
    # Duraklat
    controller.pause()
    assert controller.get_state() == AppState.PAUSED
    
    # Devam et
    controller.resume()
    assert controller.get_state() == AppState.RUNNING
    
    # Temizle
    controller.stop()
    assert controller.get_state() == AppState.IDLE


@given(st.just(True))
@settings(max_examples=100)
def test_double_start_stop(_):
    """
    Çift start/stop çağrısı testi
    """
    controller = ApplicationController()
    
    # Çift start
    controller.start()
    controller.start()  # İkinci çağrı etkisiz olmalı
    assert controller.get_state() == AppState.RUNNING
    
    # Çift stop
    controller.stop()
    controller.stop()  # İkinci çağrı etkisiz olmalı
    assert controller.get_state() == AppState.IDLE


@given(st.just(True))
@settings(max_examples=100)
def test_state_callback(_):
    """
    Durum değişikliği callback testi
    """
    controller = ApplicationController()
    states_received = []
    
    def on_state_change(state):
        states_received.append(state)
    
    controller.on_state_changed(on_state_change)
    
    controller.start()
    controller.stop()
    
    assert AppState.RUNNING in states_received
    assert AppState.IDLE in states_received
