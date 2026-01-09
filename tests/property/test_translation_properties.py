"""
Property-based tests for Translation Engine
Feature: chwili-translate
"""

import os
from hypothesis import given, strategies as st, settings

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.translate.providers import TranslationProvider
from src.translate.engine import TranslationEngine


provider_strategy = st.sampled_from(list(TranslationProvider))


@given(provider=provider_strategy)
@settings(max_examples=100)
def test_translation_provider_selection(provider: TranslationProvider):
    """
    Feature: chwili-translate, Property 2: Translation Provider Selection
    
    For any valid TranslationProvider enum value, when set as the active provider,
    subsequent translation requests should use that provider and the result should
    indicate the correct provider was used.
    
    Validates: Requirements 3.2, 3.4
    """
    engine = TranslationEngine()
    
    # Provider'ı ayarla
    engine.set_provider(provider)
    
    # Doğru provider'ın ayarlandığını kontrol et
    assert engine.get_provider() == provider, \
        f"Provider ayarlanamadı: beklenen {provider}, alınan {engine.get_provider()}"


# API Key güvenli saklama testi
api_key_strategy = st.text(min_size=25, max_size=100, alphabet=st.characters(
    whitelist_categories=('L', 'N'),
    whitelist_characters='-_'
))


@given(
    provider=provider_strategy,
    api_key=api_key_strategy
)
@settings(max_examples=100)
def test_api_key_secure_storage_round_trip(provider: TranslationProvider, api_key: str):
    """
    Feature: chwili-translate, Property 8: API Key Secure Storage Round-Trip
    
    For any valid API key string and TranslationProvider, when stored through
    set_api_key and retrieved, the key should be recoverable (after decryption)
    and match the original.
    
    Validates: Requirements 3.3
    """
    engine = TranslationEngine()
    
    # API anahtarını kaydet
    engine.set_api_key(provider, api_key)
    
    # Geri oku
    retrieved_key = engine.get_api_key(provider)
    
    # Round-trip doğrulama
    assert retrieved_key == api_key, \
        f"API key round-trip başarısız: beklenen '{api_key}', alınan '{retrieved_key}'"


@given(
    provider=provider_strategy,
    api_key=api_key_strategy
)
@settings(max_examples=100)
def test_encrypted_key_round_trip(provider: TranslationProvider, api_key: str):
    """
    Şifrelenmiş anahtar round-trip testi
    
    Validates: Requirements 3.3
    """
    engine = TranslationEngine()
    
    # API anahtarını kaydet
    engine.set_api_key(provider, api_key)
    
    # Şifrelenmiş anahtarı al
    encrypted = engine.get_encrypted_key(provider)
    assert encrypted is not None, "Şifrelenmiş anahtar bulunamadı"
    
    # Yeni engine ile şifrelenmiş anahtarı yükle
    engine2 = TranslationEngine()
    engine2.set_encrypted_key(provider, encrypted)
    
    # Şifre çözülmüş anahtarı kontrol et
    decrypted = engine2.get_api_key(provider)
    assert decrypted == api_key, \
        f"Encrypted key round-trip başarısız: beklenen '{api_key}', alınan '{decrypted}'"
