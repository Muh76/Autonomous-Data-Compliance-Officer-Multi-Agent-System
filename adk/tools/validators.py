"""Data validation utilities."""

from typing import Any, Dict, List
from pydantic import BaseModel, ValidationError


def validate_data(model: BaseModel, data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate data against a Pydantic model.
    
    Args:
        model: Pydantic model class
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, errors)
    """
    try:
        model(**data)
        return True, []
    except ValidationError as e:
        errors = [str(err) for err in e.errors()]
        return False, errors


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> tuple[bool, List[str]]:
    """
    Validate that required fields are present.
    
    Args:
        data: Data dictionary
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if field not in data]
    return len(missing) == 0, missing




