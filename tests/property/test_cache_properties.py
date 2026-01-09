"""
Property-based tests for Cache Manager
Feature: chwili-translate, Property 1: Cache Round-Trip Consistency
Validates: Requirements 4.1, 4.2
"""

import os
import tempfile
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.translate.cache import CacheManager


# Stratejiler
text_strategy = st.text(min_size=1, max_size=500, alphabet=st.characters(
    whitelist_categories=('L', 'N', 'P', 'S', 'Z'),
    blacklist_characters='\x00'
))
language_strategy = st.sampled_from(["en", "ja", "ko", "zh", "tr", "de", "fr", "es"])
provider_strategy = st.sampled_from(["chatgpt", "gemini", "google", "deepl"])


@given(
    source_text=text_strategy,
    translated_text=text_strategy,
    source_lang=language_strategy,
    target_lang=language_strategy,
    provider=provider_strategy
)
@settings(max_examples=100)
def test_cache_round_trip(source_text, translated_text, source_lang, target_lang, provider):
    """
    Feature: chwili-translate, Property 1: Cache Round-Trip Consistency
    
    For any valid source text, source language, and target language combination,
    if the text is translated and cached, then querying the cache with the same
    parameters should return the exact same translated text.
    
    Validates: Requirements 4.1, 4.2
    """
    # Geçici veritabanı oluştur
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        cache = CacheManager(db_path=temp_db)
        
        # Çeviriyi kaydet
        cache.set(source_text, translated_text, source_lang, target_lang, provider)
        
        # Geri oku
        result = cache.get(source_text, source_lang, target_lang)
        
        # Round-trip doğrulama
        assert result == translated_text, \
            f"Cache round-trip başarısız: beklenen '{translated_text}', alınan '{result}'"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@given(
    source_text=text_strategy,
    translated_text=text_strategy,
    source_lang=language_strategy,
    target_lang=language_strategy,
    provider=provider_strategy
)
@settings(max_examples=100)
def test_cache_entry_round_trip(source_text, translated_text, source_lang, target_lang, provider):
    """
    Cache entry round-trip testi - tam giriş bilgisi kontrolü
    
    Validates: Requirements 4.1, 4.2
    """
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name
    
    try:
        cache = CacheManager(db_path=temp_db)
        
        # Kaydet
        cache.set(source_text, translated_text, source_lang, target_lang, provider)
        
        # Tam giriş olarak oku
        entry = cache.get_entry(source_text, source_lang, target_lang)
        
        assert entry is not None, "Cache girişi bulunamadı"
        assert entry.source_text == source_text
        assert entry.translated_text == translated_text
        assert entry.source_lang == source_lang
        assert entry.target_lang == target_lang
        assert entry.provider == provider
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)
