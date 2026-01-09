"""
Logger for ChwiliTranslate
Dosya ve konsol logging
"""

import logging
import os
from datetime import datetime


def setup_logger(name: str = "chwilitranslate", log_dir: str = "logs") -> logging.Logger:
    """Logger'ı yapılandırır"""
    
    # Log dizinini oluştur
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Logger oluştur
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Dosya handler
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Global logger instance
logger = setup_logger()
