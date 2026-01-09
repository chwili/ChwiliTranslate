"""
Cache Manager for ChwiliTranslate
SQLite tabanlı çeviri önbelleği
"""

import sqlite3
import os
import time
from dataclasses import dataclass
from typing import Optional
from contextlib import contextmanager


@dataclass
class CacheEntry:
    """Önbellek girişi"""
    source_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    provider: str
    timestamp: float


class CacheManager:
    """SQLite tabanlı çeviri önbelleği"""
    
    def __init__(self, db_path: str = "cache.db"):
        """Cache manager'ı başlatır"""
        self.db_path = db_path
        self._enabled = True
        self._init_database()
    
    def _init_database(self) -> None:
        """Veritabanı şemasını oluşturur"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    source_lang TEXT NOT NULL,
                    target_lang TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source_text, source_lang, target_lang)
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_source_text 
                ON translations(source_text)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_languages 
                ON translations(source_lang, target_lang)
            """)
            conn.commit()

    
    @contextmanager
    def _get_connection(self):
        """Veritabanı bağlantısı context manager"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def get(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Önbellekten çeviri getirir"""
        if not self._enabled:
            return None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT translated_text FROM translations
                WHERE source_text = ? AND source_lang = ? AND target_lang = ?
            """, (text, source_lang, target_lang))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set(self, source_text: str, translated_text: str, 
            source_lang: str, target_lang: str, provider: str) -> None:
        """Çeviriyi önbelleğe kaydeder"""
        if not self._enabled:
            return
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO translations 
                (source_text, translated_text, source_lang, target_lang, provider)
                VALUES (?, ?, ?, ?, ?)
            """, (source_text, translated_text, source_lang, target_lang, provider))
            conn.commit()
    
    def clear(self) -> None:
        """Tüm önbelleği temizler"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM translations")
            conn.commit()
    
    def get_stats(self) -> dict:
        """Önbellek istatistiklerini döndürür"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM translations")
            total = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT provider, COUNT(*) FROM translations 
                GROUP BY provider
            """)
            by_provider = dict(cursor.fetchall())
            
            cursor.execute("""
                SELECT source_lang, target_lang, COUNT(*) FROM translations 
                GROUP BY source_lang, target_lang
            """)
            by_language = [
                {"source": row[0], "target": row[1], "count": row[2]}
                for row in cursor.fetchall()
            ]
            
            return {
                "total_entries": total,
                "by_provider": by_provider,
                "by_language_pair": by_language
            }
    
    def is_enabled(self) -> bool:
        """Önbellek durumunu döndürür"""
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        """Önbelleği açar/kapatır"""
        self._enabled = enabled
    
    def get_entry(self, text: str, source_lang: str, target_lang: str) -> Optional[CacheEntry]:
        """Tam önbellek girişini getirir"""
        if not self._enabled:
            return None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT source_text, translated_text, source_lang, target_lang, 
                       provider, created_at
                FROM translations
                WHERE source_text = ? AND source_lang = ? AND target_lang = ?
            """, (text, source_lang, target_lang))
            result = cursor.fetchone()
            
            if result:
                return CacheEntry(
                    source_text=result[0],
                    translated_text=result[1],
                    source_lang=result[2],
                    target_lang=result[3],
                    provider=result[4],
                    timestamp=time.time()
                )
            return None
