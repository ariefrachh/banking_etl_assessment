import csv
import logging
from typing import List, Dict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LoaderException(Exception):
    """Custom exception for loader errors"""
    pass


class EmptyRowException(LoaderException):
    """Exception for empty rows"""
    pass


class WrongColumnCountException(LoaderException):
    """Exception for wrong column count"""
    pass


class MissingMandatoryColumnsException(LoaderException):
    """Exception for missing mandatory columns"""
    pass


def load_csv(path: str) -> List[Dict]:
    """
    Load CSV file and return list of dictionaries
    
    Args:
        path: Path to CSV file
        
    Returns:
        List of dictionaries representing rows
        
    Raises:
        LoaderException: If file cannot be loaded
        EmptyRowException: If empty rows detected
        WrongColumnCountException: If row has wrong column count
        MissingMandatoryColumnsException: If mandatory columns missing
    """
    mandatory_columns = [
        'transaction_id',
        'transaction_date',
        'customer_id',
        'account_id',
        'amount',
        'currency'
    ]
    
    try:
        # First pass: validate with raw CSV reader
        with open(path, 'r', encoding='utf-8') as file:
            raw_reader = csv.reader(file)
            header = next(raw_reader)
            expected_col_count = len(header)
            
            # Check mandatory columns in header
            missing_cols = set(mandatory_columns) - set(header)
            if missing_cols:
                logger.error(f"Missing mandatory columns: {missing_cols}")
                raise MissingMandatoryColumnsException(f"Missing mandatory columns: {missing_cols}")
            
            # Validate each row for column count and empty rows
            for idx, raw_row in enumerate(raw_reader, start=2):
                # Check for empty rows
                if all(v == '' or v is None for v in raw_row):
                    logger.warning(f"Empty row detected at line {idx}")
                    raise EmptyRowException(f"Empty row detected at line {idx}")
                
                # Check column count
                if len(raw_row) != expected_col_count:
                    logger.error(f"Wrong column count at line {idx}: expected {expected_col_count}, got {len(raw_row)}")
                    raise WrongColumnCountException(f"Wrong column count at line {idx}")
        
        # Second pass: read as dictionary (we know it's valid)
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            result = list(reader)
            
        logger.info(f"Successfully loaded {len(result)} rows from {path}")
        return result
            
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise LoaderException(f"File not found: {path}")
    except Exception as e:
        if isinstance(e, LoaderException):
            raise
        logger.error(f"Error loading CSV: {str(e)}")
        raise LoaderException(f"Error loading CSV: {str(e)}")