import pytest
from etl.validator import (
    validate_transaction_id,
    validate_date,
    validate_amount,
    validate_currency,
    validate_direction,
    validate_account_type,
    validate_row
)


def test_validate_transaction_id_valid():
    """Test valid transaction ID"""
    assert validate_transaction_id('TXN123456789') == True


def test_validate_transaction_id_invalid_pattern():
    """Test invalid transaction ID pattern"""
    assert validate_transaction_id('TXN12345') == False
    assert validate_transaction_id('ABC123456789') == False
    assert validate_transaction_id('TXN12345678A') == False
    assert validate_transaction_id('') == False


def test_validate_date_valid():
    """Test valid date formats"""
    assert validate_date('2024-01-01') == True
    assert validate_date('01/01/2024') == True


def test_validate_date_invalid():
    """Test invalid date format"""
    assert validate_date('2024/01/01') == False
    assert validate_date('01-01-2024') == False
    assert validate_date('invalid') == False
    assert validate_date('') == False


def test_validate_amount_negative():
    """Test negative amount"""
    result = validate_amount('-100')
    assert result['valid'] == False


def test_validate_amount_empty():
    """Test empty amount"""
    result = validate_amount('')
    assert result['valid'] == False
    
    result = validate_amount('   ')
    assert result['valid'] == False


def test_validate_amount_anomaly():
    """Test amount exceeding 10,000,000"""
    result = validate_amount('15000000')
    assert result['valid'] == True
    assert result['anomaly'] == True


def test_validate_amount_valid():
    """Test valid amount"""
    result = validate_amount('5000')
    assert result['valid'] == True
    assert result['anomaly'] == False


def test_validate_currency_valid():
    """Test valid currencies"""
    assert validate_currency('IDR') == True
    assert validate_currency('USD') == True
    assert validate_currency('SGD') == True


def test_validate_currency_invalid():
    """Test invalid currency"""
    assert validate_currency('RP') == False
    assert validate_currency('XXX') == False
    assert validate_currency('EUR') == False
    assert validate_currency('') == False


def test_validate_direction_valid():
    """Test valid direction"""
    assert validate_direction('DEBIT') == True
    assert validate_direction('CREDIT') == True


def test_validate_direction_invalid():
    """Test invalid direction"""
    assert validate_direction('DEBET') == False
    assert validate_direction('KREDIT') == False
    assert validate_direction('') == False


def test_validate_account_type_valid():
    """Test valid account types"""
    assert validate_account_type('SAVINGS') == True
    assert validate_account_type('CURRENT') == True
    assert validate_account_type('CREDIT_CARD') == True
    assert validate_account_type('LOAN') == True


def test_validate_account_type_invalid():
    """Test invalid account type"""
    assert validate_account_type('CHECKING') == False
    assert validate_account_type('DEPOSIT') == False
    assert validate_account_type('') == False


def test_validate_row_all_valid():
    """Test row with all valid fields"""
    row = {
        'transaction_id': 'TXN123456789',
        'transaction_date': '2024-01-01',
        'customer_id': 'CUST001',
        'account_id': 'ACC001',
        'amount': '5000',
        'currency': 'IDR',
        'direction': 'DEBIT',
        'account_type': 'SAVINGS'
    }
    
    result = validate_row(row)
    assert result['valid'] == True
    assert len(result['errors']) == 0


def test_validate_row_multiple_errors():
    """Test row with multiple validation errors"""
    row = {
        'transaction_id': 'INVALID',
        'transaction_date': 'invalid-date',
        'customer_id': 'CUST001',
        'account_id': 'ACC001',
        'amount': '-1000',
        'currency': 'XXX',
        'direction': 'INVALID',
        'account_type': 'INVALID'
    }
    
    result = validate_row(row)
    assert result['valid'] == False
    assert len(result['errors']) > 0