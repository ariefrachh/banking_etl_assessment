import aiohttp
import asyncio
import logging
from typing import Dict, Optional
from functools import wraps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIException(Exception):
    """Custom exception for API errors"""
    pass


def retry(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry async functions
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed")
            
            raise last_exception
        
        return wrapper
    return decorator


@retry(max_retries=3, delay=1.0)
async def fetch_quote(symbol: str) -> Dict:
    """
    Fetch random quote from API
    
    Args:
        symbol: Symbol parameter (not used in this mock API but kept for signature)
        
    Returns:
        Dictionary containing quote data
        
    Raises:
        APIException: If API request fails
    """
    url = "https://dummyjson.com/quotes/random"
    timeout = aiohttp.ClientTimeout(total=10)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Successfully fetched quote: {data.get('id', 'N/A')}")
                    return data
                else:
                    error_msg = f"API returned status code: {response.status}"
                    logger.error(error_msg)
                    raise APIException(error_msg)
                    
    except asyncio.TimeoutError:
        logger.error("Request timeout")
        raise APIException("Request timeout")
    except aiohttp.ClientError as e:
        logger.error(f"Client error: {str(e)}")
        raise APIException(f"Client error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise APIException(f"Unexpected error: {str(e)}")


async def fetch_multiple_quotes(symbols: list) -> list:
    """
    Fetch multiple quotes concurrently
    
    Args:
        symbols: List of symbols to fetch
        
    Returns:
        List of quote dictionaries
    """
    tasks = [fetch_quote(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful_results = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch quote for symbol {symbols[idx]}: {str(result)}")
        else:
            successful_results.append(result)
    
    return successful_results