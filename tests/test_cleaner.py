import pytest
from etl.cleaner import (
    clean_whitespace,
    normalize_date,
    clean_currency,
    clean_numeric,
    impute_merchant_category,
    clean_row
)


def test_clean_whitespace():
    """Test whitespace trimming"""
    assert clean_whitespace('  hello  ') == 'hello'
    assert clean_whitespace('hello') == 'hello'
    assert clean_whitespace('  ') == ''
    assert clean_whitespace(None) == ''


def test_normalize_date_yyyy_mm_dd():
    """Test date normalization from YYYY-MM-DD"""
    assert normalize_date('2024-01-01') == '2024-01-01'


def test_normalize_date_dd_mm_yyyy():
    """Test date normalization from DD/MM/YYYY"""
    assert normalize_date('01/01/2024') == '2024-01-01'
    assert normalize_date('15/12/2023') == '2023-12-15'


def test_normalize_date_with_whitespace():
    """Test date normalization with whitespace"""
    assert normalize_date('  2024-01-01  ') == '2024-01-01'


def test_normalize_date_invalid():
    """Test invalid date normalization"""
    assert normalize_date('invalid') == None
    assert normalize_date('') == None
    assert normalize_date(None) == None


def test_clean_currency_valid():
    """Test cleaning valid currency"""
    assert clean_currency('IDR') == 'IDR'
    assert clean_currency('usd') == 'USD'
    assert clean_currency('  sgd  ') == 'SGD'


def test_clean_currency_invalid():
    """Test cleaning invalid currency"""
    assert clean_currency('RP') == None
    assert clean_currency('XXX') == None
    assert clean_currency('EUR') == None
    assert clean_currency('') == None


def test_clean_numeric_valid():
    """Test cleaning valid numeric values"""
    assert clean_numeric('1000') == 1000.0
    assert clean_numeric('1000.50') == 1000.50
    assert clean_numeric('  500  ') == 500.0


def test_clean_numeric_invalid():
    """Test cleaning invalid numeric values"""
    assert clean_numeric('') == None
    assert clean_numeric('  ') == None
    assert clean_numeric('abc') == None
    assert clean_numeric(None) == None


def test_impute_merchant_category_existing():
    """Test merchant category with existing value"""
    row = {'merchant_category': 'RETAIL', 'amount': '1000'}
    assert impute_merchant_category(row) == 'RETAIL'


def test_impute_merchant_category_missing_large_amount():
    """Test merchant category imputation for large amount"""
    row = {'merchant_category': '', 'amount': '1500000'}
    assert impute_merchant_category(row) == 'RETAIL'


def test_impute_merchant_category_missing_medium_amount():
    """Test merchant category imputation for medium amount"""
    row = {'merchant_category': '', 'amount': '500000'}
    assert impute_merchant_category(row) == 'FOOD_BEVERAGE'


def test_impute_merchant_category_missing_small_amount():
    """Test merchant category imputation for small amount"""
    row = {'merchant_category': '', 'amount': '50000'}
    assert impute_merchant_category(row) == 'OTHERS'


def test_clean_row_complete():
    """Test cleaning a complete row"""
    row = {
        'transaction_id': '  TXN123456789  ',
        'transaction_date': '01/01/2024',
        'amount': '  1000  ',
        'currency': '  idr  ',
        'merchant_category': '  RETAIL  '
    }
    
    cleaned = clean_row(row)
    
    assert cleaned['transaction_id'] == 'TXN123456789'
    assert cleaned['transaction_date'] == '2024-01-01'
    assert cleaned['amount'] == 1000.0
    assert cleaned['currency'] == 'IDR'
    assert cleaned['merchant_category'] == 'RETAIL'


def test_clean_row_with_invalid_currency():
    """Test cleaning row with invalid currency"""
    row = {
        'transaction_id': 'TXN123456789',
        'transaction_date': '2024-01-01',
        'amount': '1000',
        'currency': 'XXX'
    }
    
    cleaned = clean_row(row)
    assert cleaned['currency'] == None