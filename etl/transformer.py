import logging
import math
from datetime import datetime, date
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_date(date_str: Optional[str]) -> Optional[date]:
    """
    Convert date string to datetime.date object
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        datetime.date object or None
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, AttributeError):
        logger.warning(f"Could not convert date: {date_str}")
        return None


def convert_amount(amount: any) -> Optional[float]:
    """
    Convert amount to float
    
    Args:
        amount: Amount value (can be string, float, or None)
        
    Returns:
        Float value or None
    """
    if amount is None or amount == '':
        return None
    
    try:
        return float(amount)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert amount: {amount}")
        return None


def convert_risk_score(risk_score: any) -> Optional[float]:
    """
    Convert risk_score to float
    
    Args:
        risk_score: Risk score value
        
    Returns:
        Float value or None
    """
    if risk_score is None or risk_score == '':
        return None
    
    try:
        return float(risk_score)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert risk_score: {risk_score}")
        return None


def feature_is_large_transaction(amount: Optional[float]) -> bool:
    """
    Check if transaction is large (> 5,000,000)
    
    Args:
        amount: Transaction amount
        
    Returns:
        True if large transaction, False otherwise
    """
    if amount is None:
        return False
    return amount > 5000000


def feature_is_crossborder(currency: Optional[str]) -> bool:
    """
    Check if transaction is cross-border (currency != IDR)
    
    Args:
        currency: Currency code
        
    Returns:
        True if cross-border, False otherwise
    """
    if not currency:
        return False
    return currency != 'IDR'


def feature_transaction_day(transaction_date: Optional[date]) -> Optional[str]:
    """
    Get day of week from transaction date
    
    Args:
        transaction_date: Date object
        
    Returns:
        Day name (Monday, Tuesday, etc.) or None
    """
    if transaction_date is None:
        return None
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return days[transaction_date.weekday()]


def feature_amount_log(amount: Optional[float]) -> Optional[float]:
    """
    Calculate log of amount
    
    Args:
        amount: Transaction amount
        
    Returns:
        Log of amount or None
    """
    if amount is None or amount <= 0:
        return None
    
    try:
        return math.log(amount)
    except (ValueError, TypeError):
        logger.warning(f"Could not calculate log for amount: {amount}")
        return None


def transform_row(row: Dict) -> Dict:
    """
    Transform a single transaction row
    
    Args:
        row: Dictionary representing a transaction row
        
    Returns:
        Transformed dictionary with type conversions and derived features
    """
    transformed = row.copy()
    
    # Type conversions
    transformed['transaction_date'] = convert_date(row.get('transaction_date'))
    transformed['amount'] = convert_amount(row.get('amount'))
    transformed['risk_score'] = convert_risk_score(row.get('risk_score'))
    
    # Derived features
    transformed['is_large_transaction'] = feature_is_large_transaction(transformed['amount'])
    transformed['is_crossborder'] = feature_is_crossborder(row.get('currency'))
    transformed['transaction_day'] = feature_transaction_day(transformed['transaction_date'])
    transformed['amount_log'] = feature_amount_log(transformed['amount'])
    
    return transformed


def transform_data(data: List[Dict]) -> List[Dict]:
    """
    Transform list of transaction rows
    
    Args:
        data: List of transaction dictionaries
        
    Returns:
        List of transformed dictionaries
    """
    transformed_data = []
    
    for idx, row in enumerate(data):
        transformed_row = transform_row(row)
        transformed_data.append(transformed_row)
        logger.debug(f"Transformed row {idx}")
    
    logger.info(f"Successfully transformed {len(transformed_data)} rows")
    return transformed_data