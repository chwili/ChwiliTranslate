"""
Translation Providers for ChwiliTranslate
Çeviri sağlayıcıları ve temel sınıflar
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
import aiohttp
import json


class TranslationProvider(Enum):
    """Çeviri sağlayıcı enum"""
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    GOOGLE = "google"
    DEEPL = "deepl"


@dataclass
class TranslationConfig:
    """Çeviri konfigürasyonu"""
    provider: TranslationProvider
    api_key: str
    source_language: str
    target_language: str


@dataclass
class TranslationResult:
    """Çeviri sonucu"""
    original_text: str
    translated_text: str
    provider: TranslationProvider
    cached: bool


class TranslationProviderBase(ABC):
    """Çeviri sağlayıcı temel sınıfı"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Metni çevirir"""
        pass
    
    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """API anahtarını doğrular"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Desteklenen dilleri döndürür"""
        pass


class ChatGPTProvider(TranslationProviderBase):
    """OpenAI ChatGPT çeviri sağlayıcısı"""
    
    API_URL = "https://api.openai.com/v1/chat/completions"
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """ChatGPT ile çeviri yapar"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"Translate the following text from {source_lang} to {target_lang}. Only return the translation, nothing else:\n\n{text}"
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.API_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"ChatGPT API hatası: {response.status} - {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"].strip()
    
    def validate_api_key(self, api_key: str) -> bool:
        """API anahtarını doğrular"""
        return api_key and api_key.startswith("sk-") and len(api_key) > 20
    
    def get_supported_languages(self) -> List[str]:
        return ["en", "tr", "ja", "ko", "zh", "de", "fr", "es", "it", "pt", "ru", "ar"]


class GeminiProvider(TranslationProviderBase):
    """Google Gemini çeviri sağlayıcısı"""
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Gemini ile çeviri yapar"""
        url = f"{self.API_URL}?key={self.api_key}"
        
        prompt = f"Translate the following text from {source_lang} to {target_lang}. Only return the translation, nothing else:\n\n{text}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API hatası: {response.status} - {error_text}")
                
                data = await response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    
    def validate_api_key(self, api_key: str) -> bool:
        return api_key and len(api_key) > 20
    
    def get_supported_languages(self) -> List[str]:
        return ["en", "tr", "ja", "ko", "zh", "de", "fr", "es", "it", "pt", "ru", "ar"]


class GoogleTranslateProvider(TranslationProviderBase):
    """Google Translate çeviri sağlayıcısı (Ücretsiz)"""
    
    def __init__(self, api_key: str = ""):
        super().__init__(api_key)
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Google Translate ile çeviri yapar (ücretsiz API)"""
        import urllib.parse
        
        # Ücretsiz Google Translate API
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(full_url) as response:
                if response.status != 200:
                    raise Exception(f"Google Translate hatası: {response.status}")
                
                data = await response.json()
                # Sonuçları birleştir
                translated_parts = []
                if data and data[0]:
                    for part in data[0]:
                        if part[0]:
                            translated_parts.append(part[0])
                
                return "".join(translated_parts)
    
    def validate_api_key(self, api_key: str) -> bool:
        return True  # Ücretsiz, API key gerekmez
    
    def get_supported_languages(self) -> List[str]:
        return ["en", "tr", "ja", "ko", "zh", "de", "fr", "es", "it", "pt", "ru", "ar"]


class DeepLProvider(TranslationProviderBase):
    """DeepL çeviri sağlayıcısı"""
    
    API_URL = "https://api-free.deepl.com/v2/translate"
    
    # DeepL dil kodları eşlemesi
    LANG_MAP = {
        "en": "EN",
        "tr": "TR",
        "ja": "JA",
        "ko": "KO",
        "zh": "ZH",
        "de": "DE",
        "fr": "FR",
        "es": "ES",
        "it": "IT",
        "pt": "PT",
        "ru": "RU"
    }
    
    def _fix_punctuation(self, original: str, translated: str) -> str:
        """Orijinal metindeki son noktalamayı korur"""
        if not original or not translated:
            return translated
        
        # Orijinal ve çeviri son karakterleri
        orig_end = original.rstrip()[-1] if original.rstrip() else ""
        trans_end = translated.rstrip()[-1] if translated.rstrip() else ""
        
        punctuation = ".!?:;,"
        
        # Orijinalde noktalama varsa ve çeviride farklıysa düzelt
        if orig_end in punctuation:
            if trans_end in punctuation and trans_end != orig_end:
                # Yanlış noktalamayı doğrusuyla değiştir
                return translated.rstrip()[:-1] + orig_end
            elif trans_end not in punctuation:
                # Noktalama ekle
                return translated.rstrip() + orig_end
        elif orig_end not in punctuation and trans_end in punctuation:
            # Orijinalde yoksa çeviriden kaldır
            return translated.rstrip()[:-1]
        
        return translated
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """DeepL ile çeviri yapar"""
        headers = {
            "Authorization": f"DeepL-Auth-Key {self.api_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "text": text,
            "source_lang": self.LANG_MAP.get(source_lang, source_lang.upper()),
            "target_lang": self.LANG_MAP.get(target_lang, target_lang.upper())
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.API_URL, headers=headers, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepL API hatası: {response.status} - {error_text}")
                
                result = await response.json()
                translated = result["translations"][0]["text"]
                return self._fix_punctuation(text, translated)
    
    def validate_api_key(self, api_key: str) -> bool:
        return api_key and len(api_key) > 20
    
    def get_supported_languages(self) -> List[str]:
        return ["en", "tr", "ja", "ko", "zh", "de", "fr", "es", "it", "pt", "ru"]
