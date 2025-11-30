import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from utils.async_api import fetch_quote, fetch_multiple_quotes, APIException


@pytest.mark.asyncio
async def test_fetch_quote_success():
    """Test successful API call"""
    mock_response = {
        'id': 1,
        'quote': 'Test quote',
        'author': 'Test author'
    }
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        result = await fetch_quote('TEST')
        
        assert result == mock_response
        assert result['id'] == 1
        assert result['quote'] == 'Test quote'


@pytest.mark.asyncio
async def test_fetch_quote_api_error():
    """Test API error handling"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 500
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        with pytest.raises(APIException) as exc_info:
            await fetch_quote('TEST')
        
        assert 'status code' in str(exc_info.value)


@pytest.mark.asyncio
async def test_fetch_quote_timeout():
    """Test timeout handling"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.side_effect = asyncio.TimeoutError()
        
        with pytest.raises(APIException) as exc_info:
            await fetch_quote('TEST')
        
        assert 'timeout' in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_fetch_quote_retry():
    """Test retry logic"""
    mock_response = {
        'id': 1,
        'quote': 'Test quote',
        'author': 'Test author'
    }
    
    call_count = 0
    
    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        mock_resp = AsyncMock()
        if call_count < 2:
            mock_resp.status = 500
        else:
            mock_resp.status = 200
            mock_resp.json = AsyncMock(return_value=mock_response)
        
        return mock_resp
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.side_effect = side_effect
        
        result = await fetch_quote('TEST')
        
        assert result == mock_response
        assert call_count == 2


@pytest.mark.asyncio
async def test_fetch_multiple_quotes_success():
    """Test fetching multiple quotes"""
    mock_response = {
        'id': 1,
        'quote': 'Test quote',
        'author': 'Test author'
    }
    
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(return_value=mock_response)
        mock_get.return_value.__aenter__.return_value = mock_resp
        
        symbols = ['SYM1', 'SYM2', 'SYM3']
        results = await fetch_multiple_quotes(symbols)
        
        assert len(results) == 3
        for result in results:
            assert result['id'] == 1


@pytest.mark.asyncio
async def test_fetch_multiple_quotes_partial_failure():
    """Test fetching multiple quotes with partial failures"""
    mock_response = {
        'id': 1,
        'quote': 'Test quote',
        'author': 'Test author'
    }
    
    # Counter for each symbol
    symbol_calls = {'SYM1': 0, 'SYM2': 0, 'SYM3': 0}
    
    async def side_effect(*args, **kwargs):
        # We need to track which symbol is being called
        # Since we can't easily track it, let's use a simpler approach
        mock_resp = AsyncMock()
        mock_resp.status = 500  # Always fail to trigger all retries
        return mock_resp
    
    # Patch fetch_quote to fail for the second symbol only
    original_fetch = fetch_quote
    call_index = [0]
    
    async def mock_fetch_quote(symbol):
        call_index[0] += 1
        if call_index[0] == 2:  # Second call fails
            raise APIException("Mock failure")
        return await original_fetch(symbol)
    
    with patch('utils.async_api.fetch_quote', side_effect=mock_fetch_quote):
        symbols = ['SYM1', 'SYM2', 'SYM3']
        results = await fetch_multiple_quotes(symbols)
        
        # Should have 2 results (SYM2 failed)
        assert len(results) == 2