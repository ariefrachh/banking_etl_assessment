import pytest
import math
from datetime import date
from etl.transformer import (
    convert_date,
    convert_amount,
    convert_risk_score,
    feature_is_large_transaction,
    feature_is_crossborder,
    feature_transaction_day,
    feature_amount_log,
    transform_row
)


def test_convert_date_valid():
    """Test date conversion"""
    result = convert_date('2024-01-01')
    assert result == date(2024, 1, 1)


def test_convert_date_invalid():
    """Test invalid date conversion"""
    assert convert_date('invalid') == None
    assert convert_date('') == None
    assert convert_date(None) == None


def test_convert_amount_valid():
    """Test amount conversion"""
    assert convert_amount('1000') == 1000.0
    assert convert_amount('1000.50') == 1000.50
    assert convert_amount(1000) == 1000.0


def test_convert_amount_invalid():
    """Test invalid amount conversion"""
    assert convert_amount('') == None
    assert convert_amount(None) == None
    assert convert_amount('abc') == None


def test_convert_risk_score_valid():
    """Test risk score conversion"""
    assert convert_risk_score('0.5') == 0.5
    assert convert_risk_score(0.75) == 0.75


def test_convert_risk_score_invalid():
    """Test invalid risk score conversion"""
    assert convert_risk_score('') == None
    assert convert_risk_score(None) == None


def test_feature_is_large_transaction():
    """Test large transaction feature"""
    assert feature_is_large_transaction(6000000) == True
    assert feature_is_large_transaction(4000000) == False
    assert feature_is_large_transaction(5000001) == True
    assert feature_is_large_transaction(None) == False


def test_feature_is_crossborder():
    """Test cross-border transaction feature"""
    assert feature_is_crossborder('USD') == True
    assert feature_is_crossborder('SGD') == True
    assert feature_is_crossborder('IDR') == False
    assert feature_is_crossborder(None) == False
    assert feature_is_crossborder('') == False


def test_feature_transaction_day():
    """Test transaction day feature"""
    # 2024-01-01 is a Monday
    assert feature_transaction_day(date(2024, 1, 1)) == 'Monday'
    # 2024-01-02 is a Tuesday
    assert feature_transaction_day(date(2024, 1, 2)) == 'Tuesday'
    # 2024-01-07 is a Sunday
    assert feature_transaction_day(date(2024, 1, 7)) == 'Sunday'
    assert feature_transaction_day(None) == None


def test_feature_amount_log():
    """Test amount log feature"""
    result = feature_amount_log(1000)
    assert result is not None
    assert abs(result - math.log(1000)) < 0.0001
    
    assert feature_amount_log(None) == None
    assert feature_amount_log(0) == None
    assert feature_amount_log(-100) == None


def test_transform_row_complete():
    """Test complete row transformation"""
    row = {
        'transaction_id': 'TXN123456789',
        'transaction_date': '2024-01-01',
        'customer_id': 'CUST001',
        'account_id': 'ACC001',
        'amount': 6000000,
        'currency': 'USD',
        'risk_score': 0.5
    }
    
    transformed = transform_row(row)
    
    # Check type conversions
    assert isinstance(transformed['transaction_date'], date)
    assert transformed['transaction_date'] == date(2024, 1, 1)
    assert isinstance(transformed['amount'], float)
    assert transformed['amount'] == 6000000.0
    assert transformed['risk_score'] == 0.5
    
    # Check derived features
    assert transformed['is_large_transaction'] == True
    assert transformed['is_crossborder'] == True
    assert transformed['transaction_day'] == 'Monday'
    assert transformed['amount_log'] is not None


def test_transform_row_small_idr_transaction():
    """Test transformation of small IDR transaction"""
    row = {
        'transaction_id': 'TXN123456789',
        'transaction_date': '2024-01-02',
        'amount': 1000000,
        'currency': 'IDR'
    }
    
    transformed = transform_row(row)
    
    assert transformed['is_large_transaction'] == False
    assert transformed['is_crossborder'] == False
    assert transformed['transaction_day'] == 'Tuesday'


def test_transform_row_with_none_values():
    """Test transformation with None values"""
    row = {
        'transaction_id': 'TXN123456789',
        'transaction_date': None,
        'amount': None,
        'currency': None
    }
    
    transformed = transform_row(row)
    
    assert transformed['transaction_date'] == None
    assert transformed['amount'] == None
    assert transformed['is_large_transaction'] == False
    assert transformed['is_crossborder'] == False
    assert transformed['transaction_day'] == None
    assert transformed['amount_log'] == None