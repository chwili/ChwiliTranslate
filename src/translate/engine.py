"""
Translation Engine for ChwiliTranslate
Ana çeviri motoru yöneticisi
"""

import os
import base64
from typing import Optional, Dict, List
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .providers import (
    TranslationProvider, TranslationProviderBase, TranslationResult,
    ChatGPTProvider, GeminiProvider, GoogleTranslateProvider, DeepLProvider
)
from .cache import CacheManager


class TranslationEngine:
    """Çeviri motoru yöneticisi"""
    
    # Şifreleme için sabit salt (gerçek uygulamada güvenli saklanmalı)
    ENCRYPTION_SALT = b'chwilitranslate_salt_2024'
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Translation Engine'i başlatır"""
        self._provider: TranslationProvider = TranslationProvider.GOOGLE  # Varsayılan: Google (ücretsiz)
        self._source_lang: str = "en"
        self._target_lang: str = "tr"
        self._api_keys: Dict[TranslationProvider, str] = {}
        self._encrypted_keys: Dict[TranslationProvider, bytes] = {}
        self._cache = cache_manager
        self._fernet = self._create_fernet()
        
        # Provider instance'ları
        self._providers: Dict[TranslationProvider, TranslationProviderBase] = {}
        
        # Google provider'ı hemen başlat (ücretsiz)
        self._providers[TranslationProvider.GOOGLE] = GoogleTranslateProvider("")
    
    def _create_fernet(self) -> Fernet:
        """Şifreleme için Fernet oluşturur"""
        # Makine bazlı anahtar oluştur
        machine_id = os.environ.get('COMPUTERNAME', 'default_machine')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.ENCRYPTION_SALT,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
        return Fernet(key)
    
    def set_provider(self, provider: TranslationProvider) -> None:
        """Aktif çeviri sağlayıcısını ayarlar"""
        self._provider = provider

    
    def get_provider(self) -> TranslationProvider:
        """Aktif çeviri sağlayıcısını döndürür"""
        return self._provider
    
    def set_languages(self, source_lang: str, target_lang: str) -> None:
        """Kaynak ve hedef dilleri ayarlar"""
        self._source_lang = source_lang
        self._target_lang = target_lang
    
    def set_api_key(self, provider: TranslationProvider, api_key: str) -> None:
        """API anahtarını güvenli şekilde saklar (şifreli)"""
        # Şifrele ve sakla
        encrypted = self._fernet.encrypt(api_key.encode())
        self._encrypted_keys[provider] = encrypted
        self._api_keys[provider] = api_key
        
        # Provider instance'ını güncelle
        self._update_provider_instance(provider, api_key)
    
    def get_api_key(self, provider: TranslationProvider) -> Optional[str]:
        """API anahtarını döndürür (şifre çözülmüş)"""
        if provider in self._api_keys:
            return self._api_keys[provider]
        
        if provider in self._encrypted_keys:
            decrypted = self._fernet.decrypt(self._encrypted_keys[provider])
            return decrypted.decode()
        
        return None
    
    def set_encrypted_key(self, provider: TranslationProvider, encrypted_key: bytes) -> None:
        """Şifrelenmiş API anahtarını saklar"""
        self._encrypted_keys[provider] = encrypted_key
        # Şifre çöz ve cache'le
        try:
            decrypted = self._fernet.decrypt(encrypted_key)
            self._api_keys[provider] = decrypted.decode()
            self._update_provider_instance(provider, self._api_keys[provider])
        except Exception:
            pass
    
    def get_encrypted_key(self, provider: TranslationProvider) -> Optional[bytes]:
        """Şifrelenmiş API anahtarını döndürür"""
        return self._encrypted_keys.get(provider)
    
    def _update_provider_instance(self, provider: TranslationProvider, api_key: str) -> None:
        """Provider instance'ını günceller"""
        if provider == TranslationProvider.CHATGPT:
            self._providers[provider] = ChatGPTProvider(api_key)
        elif provider == TranslationProvider.GEMINI:
            self._providers[provider] = GeminiProvider(api_key)
        elif provider == TranslationProvider.GOOGLE:
            self._providers[provider] = GoogleTranslateProvider(api_key)
        elif provider == TranslationProvider.DEEPL:
            self._providers[provider] = DeepLProvider(api_key)

    
    async def translate(self, text: str) -> TranslationResult:
        """Metni çevirir (cache kontrolü dahil)"""
        # Önce cache kontrol et
        if self._cache and self._cache.is_enabled():
            cached_translation = self._cache.get(
                text, self._source_lang, self._target_lang
            )
            if cached_translation:
                return TranslationResult(
                    original_text=text,
                    translated_text=cached_translation,
                    provider=self._provider,
                    cached=True
                )
        
        # Provider'dan çeviri al
        provider_instance = self._providers.get(self._provider)
        if not provider_instance:
            # Google için API key gerekmez
            if self._provider == TranslationProvider.GOOGLE:
                self._providers[self._provider] = GoogleTranslateProvider("")
                provider_instance = self._providers[self._provider]
            else:
                api_key = self.get_api_key(self._provider)
                if not api_key:
                    raise Exception(f"{self._provider.value} için API anahtarı ayarlanmamış")
                self._update_provider_instance(self._provider, api_key)
                provider_instance = self._providers[self._provider]
        
        translated_text = await provider_instance.translate(
            text, self._source_lang, self._target_lang
        )
        
        # Cache'e kaydet
        if self._cache and self._cache.is_enabled():
            self._cache.set(
                text, translated_text,
                self._source_lang, self._target_lang,
                self._provider.value
            )
        
        return TranslationResult(
            original_text=text,
            translated_text=translated_text,
            provider=self._provider,
            cached=False
        )
    
    def get_supported_languages(self, provider: Optional[TranslationProvider] = None) -> List[str]:
        """Desteklenen dilleri döndürür"""
        target_provider = provider or self._provider
        provider_instance = self._providers.get(target_provider)
        
        if provider_instance:
            return provider_instance.get_supported_languages()
        
        # Varsayılan diller
        return ["en", "tr", "ja", "ko", "zh", "de", "fr", "es"]
    
    def validate_api_key(self, provider: TranslationProvider, api_key: str) -> bool:
        """API anahtarını doğrular"""
        if provider == TranslationProvider.CHATGPT:
            return ChatGPTProvider(api_key).validate_api_key(api_key)
        elif provider == TranslationProvider.GEMINI:
            return GeminiProvider(api_key).validate_api_key(api_key)
        elif provider == TranslationProvider.GOOGLE:
            return GoogleTranslateProvider(api_key).validate_api_key(api_key)
        elif provider == TranslationProvider.DEEPL:
            return DeepLProvider(api_key).validate_api_key(api_key)
        return False
