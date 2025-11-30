# Banking ETL Assessment

## Overview
This project implements a mini ETL (Extract, Transform, Load) pipeline for processing banking transaction data. The pipeline includes validation, cleaning, and transformation steps specifically designed for banking transactions.

## Project Structure
```
banking_etl_assessment/
│
├── README.md
├── data/
│   └── banking_transactions.csv
│
├── etl/
│   ├── __init__.py
│   ├── loader.py          # CSV loading with validation
│   ├── validator.py       # Banking-specific validation rules
│   ├── cleaner.py         # Data cleaning and normalization
│   └── transformer.py     # Type conversion and feature engineering
│
├── utils/
│   ├── __init__.py
│   └── async_api.py       # Async API caller with retry logic
│
└── tests/
    ├── test_loader.py
    ├── test_validator.py
    ├── test_cleaner.py
    ├── test_transformer.py
    ├── test_utils.py
    └── conftest.py
```

## ETL Flow Explanation

### 1. Loader (`etl/loader.py`)
The loader module reads CSV files and performs initial validation:
- Reads CSV into list of dictionaries
- Detects empty rows
- Validates column count consistency
- Checks for mandatory columns
- Custom exception classes for different error types
- Comprehensive logging

**Mandatory columns:**
- transaction_id
- transaction_date
- customer_id
- account_id
- amount
- currency

### 2. Validator (`etl/validator.py`)
Implements banking-specific validation rules:

**Validation Rules:**
- **transaction_id**: Must follow pattern `TXNxxxxxxxxx` (TXN followed by 9 digits)
- **transaction_date**: Valid date format (YYYY-MM-DD or DD/MM/YYYY)
- **amount**: 
  - Must not be negative
  - Must not be empty
  - Flags anomaly if > 10,000,000 IDR
- **currency**: Must be one of IDR, USD, SGD
- **direction**: Must be DEBIT or CREDIT
- **account_type**: Must be SAVINGS, CURRENT, CREDIT_CARD, or LOAN

### 3. Cleaner (`etl/cleaner.py`)
Handles data cleaning and normalization:
- Removes whitespace from all fields
- Normalizes dates to YYYY-MM-DD format
- Sets invalid currency to None
- Sets missing numeric values to None
- Imputes missing merchant_category using simple rules:
  - Amount > 1,000,000: RETAIL
  - Amount > 100,000: FOOD_BEVERAGE
  - Otherwise: OTHERS

### 4. Transformer (`etl/transformer.py`)
Performs type conversion and feature engineering:

**Type Conversions:**
- transaction_date → `datetime.date`
- amount → `float`
- risk_score → `float` or `None`

**Derived Features:**
- `is_large_transaction`: True if amount > 5,000,000
- `is_crossborder`: True if currency != IDR
- `transaction_day`: Day of week (Monday, Tuesday, etc.)
- `amount_log`: Natural logarithm of amount

## Utility Module

### Async API Caller (`utils/async_api.py`)
- Implements async API calls using `aiohttp`
- Retry logic with decorator (3 attempts, 1 second delay)
- Timeout handling (10 seconds)
- Fetches from: https://dummyjson.com/quotes/random
- Supports fetching multiple quotes concurrently

## Banking Validation Rules Summary

| Field | Rule | Action on Violation |
|-------|------|---------------------|
| transaction_id | Pattern: TXNxxxxxxxxx | Mark as invalid |
| transaction_date | Valid date format | Mark as invalid |
| amount | Not negative, not empty | Mark as invalid |
| amount | > 10,000,000 | Flag as anomaly |
| currency | IDR, USD, or SGD | Mark as invalid |
| direction | DEBIT or CREDIT | Mark as invalid |
| account_type | SAVINGS, CURRENT, CREDIT_CARD, LOAN | Mark as invalid |

## Running the ETL

### Prerequisites
```bash
pip install aiohttp pytest pytest-asyncio
```

### Sample Usage
```python
from etl import load_csv, validate_data, clean_data, transform_data

# Load data
data = load_csv('data/banking_transactions.csv')

# Validate
validated_data = validate_data(data)

# Clean
cleaned_data = clean_data(validated_data)

# Transform
transformed_data = transform_data(cleaned_data)

# Process results
for row in transformed_data:
    print(row)
```

### Running Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_loader.py

# Run with coverage
pytest --cov=etl --cov=utils

# Run async tests
pytest -v tests/test_utils.py
```

## Sample Data Format

Create `data/banking_transactions.csv` with the following structure:
```csv
transaction_id,transaction_date,customer_id,account_id,amount,currency,direction,account_type,merchant_category,risk_score
TXN123456789,2024-01-01,CUST001,ACC001,5000000,IDR,DEBIT,SAVINGS,RETAIL,0.5
TXN987654321,01/02/2024,CUST002,ACC002,15000000,USD,CREDIT,CURRENT,FOOD_BEVERAGE,0.8
```

## Error Handling

The pipeline uses custom exception classes for different error scenarios:
- `LoaderException`: General loading errors
- `EmptyRowException`: Empty rows detected
- `WrongColumnCountException`: Inconsistent column count
- `MissingMandatoryColumnsException`: Missing required columns
- `ValidationException`: Validation errors
- `APIException`: API call failures

## Possible Improvements

1. **Data Quality**
   - Add more sophisticated imputation methods (e.g., using ML models)
   - Implement data profiling to detect outliers and data drift
   - Add support for handling duplicate transactions

2. **Performance**
   - Implement batch processing for large datasets
   - Add parallel processing for validation and cleaning
   - Use pandas for more efficient data manipulation
   - Implement streaming for very large files

3. **Validation**
   - Add cross-field validation (e.g., check if debit/credit matches amount sign)
   - Implement business rule validation (e.g., transaction limits per customer)
   - Add support for custom validation rules configuration

4. **Features**
   - Add more derived features (e.g., time-based features, customer behavior patterns)
   - Implement feature scaling and normalization
   - Add feature selection mechanisms

5. **Monitoring & Logging**
   - Add structured logging with different log levels
   - Implement metrics collection (e.g., validation failure rates)
   - Add data quality dashboards
   - Create alerts for anomalies

6. **Testing**
   - Add integration tests for the full ETL pipeline
   - Implement property-based testing
   - Add performance benchmarks
   - Create data quality tests

7. **Infrastructure**
   - Add support for different data sources (databases, APIs, cloud storage)
   - Implement data versioning
   - Add support for incremental loads
   - Create data lineage tracking

8. **Configuration**
   - Externalize validation rules to configuration files
   - Add support for environment-specific settings
   - Implement feature flags for gradual rollout

9. **API Utility**
   - Add support for different API endpoints
   - Implement rate limiting
   - Add caching mechanism for API responses
   - Support for authentication methods

10. **Documentation**
    - Add API documentation with examples
    - Create data dictionary
    - Add architecture diagrams
    - Create user guides for different personas

## License
This project is for assessment purposes.