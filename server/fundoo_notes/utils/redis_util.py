from typing import Any, Dict, List, Type, Union
from django.core.exceptions import ValidationError
from django.core.cache import cache
from loguru import logger
import json
class RedisUtils:
    """
    Utility class to interact with Redis cache.
    Provides methods for saving, getting, and deleting cached data.
    """

    @staticmethod
    def save(key: str, value: Any, timeout: int = 3600) -> None:
        """
        Save data to cache.
        
        Parameters:
            key (str): The cache key.
            value (Any): The value to cache.
            timeout (int): The cache timeout in seconds.
        """
        try:
            cache.set(key, value, timeout)
        except Exception as e:
            logger.error(f"Error saving to cache: {str(e)}")
            raise ValidationError(f"Error saving to cache: {str(e)}")

    @staticmethod
    def get(key: str) -> Any:
        """
        Retrieve data from cache.
        
        Parameters:
            key (str): The cache key.
        
        Returns:
            Any: The cached value or None if the key does not exist.
        """
        try:
            return cache.get(key)
        except Exception as e:
            logger.error(f"Error retrieving from cache: {str(e)}")
            raise ValidationError(f"Error retrieving from cache: {str(e)}")

    @staticmethod
    def delete(key: str) -> None:
        """
        Delete data from cache.
        
        Parameters:
            key (str): The cache key.
        """
        try:
            cache.delete(key)
        except Exception as e:
            logger.error(f"Error deleting from cache: {str(e)}")
            raise ValidationError(f"Error deleting from cache: {str(e)}")
        
    @staticmethod
    def deserialize(value: Any) -> Any:
        """
        Deserialize JSON string back into Python objects.
        
        Parameters:
            value (Any): The cached value (JSON string or None).
        
        Returns:
            Any: The deserialized Python object or None if the input was None.
        """
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Error deserializing cached value: {str(e)}")
            raise ValidationError(f"Error deserializing cached value: {str(e)}")

