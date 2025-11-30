import re
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ValidationException(Exception):
    """Base exception for validation errors"""
    pass


def validate_transaction_id(transaction_id: str) -> bool:
    """
    Validate transaction_id follows pattern TXNxxxxxxx
    
    Args:
        transaction_id: Transaction ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not transaction_id:
        return False
    pattern = r'^TXN\d{9}$'
    return bool(re.match(pattern, transaction_id))


def validate_date(date_str: str) -> bool:
    """
    Validate date format (YYYY-MM-DD or DD/MM/YYYY)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid date, False otherwise
    """
    if not date_str:
        return False
    
    formats = ['%Y-%m-%d', '%d/%m/%Y']
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_amount(amount_str: str) -> Dict[str, any]:
    """
    Validate amount field
    
    Args:
        amount_str: Amount string to validate
        
    Returns:
        Dictionary with 'valid' (bool) and 'anomaly' (bool) keys
    """
    result = {'valid': True, 'anomaly': False}
    
    # Check if empty
    if not amount_str or amount_str.strip() == '':
        result['valid'] = False
        return result
    
    try:
        amount = float(amount_str)
        
        # Check if negative
        if amount < 0:
            result['valid'] = False
            return result
        
        # Check if anomaly (> 10,000,000 IDR)
        if amount > 10000000:
            result['anomaly'] = True
            
    except ValueError:
        result['valid'] = False
    
    return result


def validate_currency(currency: str) -> bool:
    """
    Validate currency is one of IDR, USD, SGD
    
    Args:
        currency: Currency code to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_currencies = ['IDR', 'USD', 'SGD']
    return currency in valid_currencies


def validate_direction(direction: str) -> bool:
    """
    Validate direction is DEBIT or CREDIT
    
    Args:
        direction: Direction to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_directions = ['DEBIT', 'CREDIT']
    return direction in valid_directions


def validate_account_type(account_type: str) -> bool:
    """
    Validate account_type is one of SAVINGS, CURRENT, CREDIT_CARD, LOAN
    
    Args:
        account_type: Account type to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_types = ['SAVINGS', 'CURRENT', 'CREDIT_CARD', 'LOAN']
    return account_type in valid_types


def validate_row(row: Dict) -> Dict[str, any]:
    """
    Validate a single transaction row
    
    Args:
        row: Dictionary representing a transaction row
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'anomalies': []
    }
    
    # Validate transaction_id
    if not validate_transaction_id(row.get('transaction_id', '')):
        validation_result['valid'] = False
        validation_result['errors'].append('Invalid transaction_id pattern')
    
    # Validate date
    if not validate_date(row.get('transaction_date', '')):
        validation_result['valid'] = False
        validation_result['errors'].append('Invalid transaction_date format')
    
    # Validate amount
    amount_validation = validate_amount(row.get('amount', ''))
    if not amount_validation['valid']:
        validation_result['valid'] = False
        validation_result['errors'].append('Invalid amount')
    if amount_validation['anomaly']:
        validation_result['anomalies'].append('Amount exceeds 10,000,000 IDR')
    
    # Validate currency
    if not validate_currency(row.get('currency', '')):
        validation_result['valid'] = False
        validation_result['errors'].append('Invalid currency')
    
    # Validate direction (if present)
    if 'direction' in row and row['direction']:
        if not validate_direction(row['direction']):
            validation_result['valid'] = False
            validation_result['errors'].append('Invalid direction')
    
    # Validate account_type (if present)
    if 'account_type' in row and row['account_type']:
        if not validate_account_type(row['account_type']):
            validation_result['valid'] = False
            validation_result['errors'].append('Invalid account_type')
    
    return validation_result


def validate_data(data: List[Dict]) -> List[Dict]:
    """
    Validate list of transaction rows
    
    Args:
        data: List of transaction dictionaries
        
    Returns:
        List of dictionaries with original data and validation results
    """
    validated_data = []
    
    for idx, row in enumerate(data):
        validation = validate_row(row)
        row_with_validation = row.copy()
        row_with_validation['_validation'] = validation
        validated_data.append(row_with_validation)
        
        if not validation['valid']:
            logger.warning(f"Row {idx} validation failed: {validation['errors']}")
        if validation['anomalies']:
            logger.info(f"Row {idx} anomalies detected: {validation['anomalies']}")
    
    return validated_data