import pytest
from etl.loader import (
    load_csv,
    LoaderException,
    EmptyRowException,
    WrongColumnCountException,
    MissingMandatoryColumnsException
)


def test_missing_file():
    """Test loading non-existent file"""
    with pytest.raises(LoaderException) as exc_info:
        load_csv('non_existent_file.csv')
    assert 'File not found' in str(exc_info.value)


def test_empty_row_detection(tmp_path):
    """Test detection of empty rows"""
    csv_file = tmp_path / "test_empty_row.csv"
    csv_file.write_text(
        "transaction_id,transaction_date,customer_id,account_id,amount,currency\n"
        "TXN123456789,2024-01-01,CUST001,ACC001,1000,IDR\n"
        ",,,,,\n"
    )
    
    with pytest.raises(EmptyRowException) as exc_info:
        load_csv(str(csv_file))
    assert 'Empty row detected' in str(exc_info.value)


def test_wrong_column_count(tmp_path):
    """Test detection of wrong column count"""
    csv_file = tmp_path / "test_wrong_columns.csv"
    csv_file.write_text(
        "transaction_id,transaction_date,customer_id,account_id,amount,currency\n"
        "TXN123456789,2024-01-01,CUST001,ACC001\n"
    )
    
    with pytest.raises(WrongColumnCountException) as exc_info:
        load_csv(str(csv_file))
    assert 'Wrong column count' in str(exc_info.value)


def test_missing_mandatory_columns(tmp_path):
    """Test detection of missing mandatory columns"""
    csv_file = tmp_path / "test_missing_cols.csv"
    csv_file.write_text(
        "transaction_id,customer_id\n"
        "TXN123456789,CUST001\n"
    )
    
    with pytest.raises(MissingMandatoryColumnsException) as exc_info:
        load_csv(str(csv_file))
    assert 'Missing mandatory columns' in str(exc_info.value)


def test_successful_load(tmp_path):
    """Test successful CSV loading"""
    csv_file = tmp_path / "test_success.csv"
    csv_file.write_text(
        "transaction_id,transaction_date,customer_id,account_id,amount,currency\n"
        "TXN123456789,2024-01-01,CUST001,ACC001,1000,IDR\n"
        "TXN987654321,2024-01-02,CUST002,ACC002,2000,USD\n"
    )
    
    result = load_csv(str(csv_file))
    assert len(result) == 2
    assert result[0]['transaction_id'] == 'TXN123456789'
    assert result[1]['transaction_id'] == 'TXN987654321'