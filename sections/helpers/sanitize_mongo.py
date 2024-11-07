from datetime import datetime
from sections.helpers.admin.admin_db_mgmt import DataValidator
import pandas as pd
from typing import Optional, Dict, Any, Union


def sanitize_db(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitizes and validates database records according to the schema.

    Args:
        data: Dictionary containing database record fields

    Returns:
        Sanitized dictionary with validated data types and values
    """
    if not data:
        return None

    # Create a copy to avoid modifying the original
    formatted_data = {}

    # Helper function to convert dates
    def convert_date(value: Any) -> Optional[datetime]:
        if value is None or pd.isna(value):
            return None
        if isinstance(value, (datetime, pd.Timestamp)):
            return pd.Timestamp(value).to_pydatetime()
        if isinstance(value, str):
            try:
                return pd.to_datetime(value).to_pydatetime()
            except (ValueError, TypeError):
                return None
        return None

    # Helper function to convert numeric values
    def convert_numeric(value: Any, type_: type) -> Union[int, float]:
        if value is None or pd.isna(value):
            return type_(0)
        try:
            return type_(value)
        except (ValueError, TypeError):
            return type_(0)

    # Process each field according to its type
    for key, value in data.items():
        try:
            # Skip MongoDB ID field
            if key == "_id":
                formatted_data[key] = str(value)
                continue

            # Skip if field not in schema
            if key not in DataValidator.SCHEMA:
                formatted_data[key] = value
                continue

            field_type = DataValidator.SCHEMA[key]["type"]

            # Handle different field types
            if field_type == datetime:
                formatted_data[key] = convert_date(value)
            elif field_type == float:
                formatted_data[key] = convert_numeric(value, float)
            elif field_type == int:
                formatted_data[key] = convert_numeric(value, int)
            elif field_type == str:
                formatted_data[key] = str(value) if value is not None else ""
            else:
                formatted_data[key] = value

            # Apply constraints from schema
            if field_type in (float, int):
                min_value = DataValidator.SCHEMA[key].get("min")
                max_value = DataValidator.SCHEMA[key].get("max")

                if min_value is not None and formatted_data[key] < min_value:
                    formatted_data[key] = field_type(min_value)
                if max_value is not None and formatted_data[key] > max_value:
                    formatted_data[key] = field_type(max_value)

        except Exception as e:
            print(f"Error processing field '{key}': {str(e)}")
            # Set safe default values
            if field_type == float:
                formatted_data[key] = 0.0
            elif field_type == int:
                formatted_data[key] = 0
            elif field_type == datetime:
                formatted_data[key] = None
            elif field_type == str:
                formatted_data[key] = ""
            else:
                formatted_data[key] = value

    # Ensure required fields are present
    for field, schema in DataValidator.SCHEMA.items():
        if schema.get("required", False) and field not in formatted_data:
            if schema["type"] == float:
                formatted_data[field] = 0.0
            elif schema["type"] == int:
                formatted_data[field] = 0
            elif schema["type"] == datetime:
                formatted_data[field] = None
            elif schema["type"] == str:
                formatted_data[field] = ""

    return formatted_data
