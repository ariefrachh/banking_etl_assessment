import logging
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_whitespace(value: str) -> str:
    """
    Remove leading and trailing whitespace
    
    Args:
        value: String to clean
        
    Returns:
        Cleaned string
    """
    if value is None:
        return ''
    return str(value).strip()


def normalize_date(date_str: str) -> Optional[str]:
    """
    Normalize date to YYYY-MM-DD format
    
    Args:
        date_str: Date string in YYYY-MM-DD or DD/MM/YYYY format
        
    Returns:
        Normalized date string or None if invalid
    """
    if not date_str:
        return None
    
    date_str = clean_whitespace(date_str)
    formats = ['%Y-%m-%d', '%d/%m/%Y']
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    logger.warning(f"Could not normalize date: {date_str}")
    return None


def clean_currency(currency: str) -> Optional[str]:
    """
    Clean currency field, return None if invalid
    
    Args:
        currency: Currency code
        
    Returns:
        Cleaned currency or None if invalid
    """
    if not currency:
        return None
    
    currency = clean_whitespace(currency).upper()
    valid_currencies = ['IDR', 'USD', 'SGD']
    
    if currency in valid_currencies:
        return currency
    
    logger.warning(f"Invalid currency detected: {currency}, setting to None")
    return None


def clean_numeric(value: str) -> Optional[float]:
    """
    Clean numeric value, return None if invalid
    
    Args:
        value: Numeric string
        
    Returns:
        Float value or None if invalid
    """
    if not value or clean_whitespace(value) == '':
        return None
    
    try:
        return float(clean_whitespace(value))
    except ValueError:
        logger.warning(f"Invalid numeric value: {value}, setting to None")
        return None


def impute_merchant_category(row: Dict) -> Optional[str]:
    """
    Simple rule-based imputation for merchant_category
    
    Args:
        row: Transaction row dictionary
        
    Returns:
        Imputed merchant category or None
    """
    merchant_category = row.get('merchant_category', '')
    
    if merchant_category and clean_whitespace(merchant_category):
        return clean_whitespace(merchant_category)
    
    # Simple rules based on amount or other fields
    amount = clean_numeric(row.get('amount', ''))
    
    if amount is None:
        return None
    
    # Simple imputation rules
    if amount > 1000000:
        return 'RETAIL'
    elif amount > 100000:
        return 'FOOD_BEVERAGE'
    else:
        return 'OTHERS'


def clean_row(row: Dict) -> Dict:
    """
    Clean a single transaction row
    
    Args:
        row: Dictionary representing a transaction row
        
    Returns:
        Cleaned dictionary
    """
    cleaned = {}
    
    # Clean all string fields
    for key, value in row.items():
        if key == '_validation':
            cleaned[key] = value
            continue
            
        if isinstance(value, str):
            cleaned[key] = clean_whitespace(value)
        else:
            cleaned[key] = value
    
    # Normalize date
    if 'transaction_date' in cleaned:
        cleaned['transaction_date'] = normalize_date(cleaned['transaction_date'])
    
    # Clean currency
    if 'currency' in cleaned:
        cleaned['currency'] = clean_currency(cleaned['currency'])
    
    # Clean numeric fields
    numeric_fields = ['amount', 'risk_score']
    for field in numeric_fields:
        if field in cleaned:
            cleaned[field] = clean_numeric(cleaned[field])
    
    # Impute merchant category
    if 'merchant_category' in row:
        cleaned['merchant_category'] = impute_merchant_category(cleaned)
    
    return cleaned


def clean_data(data: List[Dict]) -> List[Dict]:
    """
    Clean list of transaction rows
    
    Args:
        data: List of transaction dictionaries
        
    Returns:
        List of cleaned dictionaries
    """
    cleaned_data = []
    
    for idx, row in enumerate(data):
        cleaned_row = clean_row(row)
        cleaned_data.append(cleaned_row)
        logger.debug(f"Cleaned row {idx}")
    
    logger.info(f"Successfully cleaned {len(cleaned_data)} rows")
    return cleaned_data