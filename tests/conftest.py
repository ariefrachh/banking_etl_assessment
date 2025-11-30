import pytest
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_transaction():
    """Sample valid transaction for testing"""
    return {
        'transaction_id': 'TXN123456789',
        'transaction_date': '2024-01-01',
        'customer_id': 'CUST001',
        'account_id': 'ACC001',
        'amount': '5000000',
        'currency': 'IDR',
        'direction': 'DEBIT',
        'account_type': 'SAVINGS',
        'merchant_category': 'RETAIL',
        'risk_score': '0.5'
    }


@pytest.fixture
def sample_transactions_list():
    """Sample list of transactions for testing"""
    return [
        {
            'transaction_id': 'TXN123456789',
            'transaction_date': '2024-01-01',
            'customer_id': 'CUST001',
            'account_id': 'ACC001',
            'amount': '5000000',
            'currency': 'IDR',
            'direction': 'DEBIT',
            'account_type': 'SAVINGS'
        },
        {
            'transaction_id': 'TXN987654321',
            'transaction_date': '2024-01-02',
            'customer_id': 'CUST002',
            'account_id': 'ACC002',
            'amount': '10000',
            'currency': 'USD',
            'direction': 'CREDIT',
            'account_type': 'CURRENT'
        }
    ]


@pytest.fixture
def invalid_transaction():
    """Sample invalid transaction for testing"""
    return {
        'transaction_id': 'INVALID',
        'transaction_date': 'invalid-date',
        'customer_id': 'CUST001',
        'account_id': 'ACC001',
        'amount': '-1000',
        'currency': 'XXX',
        'direction': 'INVALID',
        'account_type': 'INVALID'
    }