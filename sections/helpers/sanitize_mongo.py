from datetime import datetime
from sections.helpers.admin.admin_db_mgmt import DataValidator
import pandas as pd
import streamlit as st

def sanitize_db(data):
    if not data:
        return None

    # Create a copy to avoid modifying the original
    formatted_data = {}

    for key, value in data.items():
        try:
            # Handle ObjectId separately
            if key == "_id":
                formatted_data[key] = str(value)
                continue

            # Skip if field not in schema
            if key not in DataValidator.SCHEMA:
                formatted_data[key] = value
                continue

            field_type = DataValidator.SCHEMA[key]["type"]

            # Special handling for empty/null date values
            if field_type == datetime:
                if value in [None, "", "NaT", "NaN", pd.NaT] or pd.isna(value):
                    formatted_data[key] = None
                elif isinstance(value, (datetime, pd.Timestamp)):
                    formatted_data[key] = value
                elif isinstance(value, str):
                    try:
                        if value.strip():  # Check if string is not just whitespace
                            formatted_data[key] = pd.to_datetime(value)
                        else:
                            formatted_data[key] = None
                    except Exception as e:
                        print(f"Error parsing date field '{key}': {str(e)}")
                        formatted_data[key] = None
                else:
                    formatted_data[key] = None
                continue

            # Handle None values based on field type
            if value is None or pd.isna(value) or value == "":
                if field_type == float:
                    formatted_data[key] = 0.0
                elif field_type == int:
                    formatted_data[key] = 0
                else:
                    formatted_data[key] = value
                continue

            # Convert other types
            if field_type == float:
                try:
                    formatted_data[key] = float(value)
                except (ValueError, TypeError):
                    formatted_data[key] = 0.0

            elif field_type == int:
                try:
                    formatted_data[key] = int(value)
                except (ValueError, TypeError):
                    formatted_data[key] = 0

            elif field_type == str:
                formatted_data[key] = str(value) if value is not None else ""

            else:
                formatted_data[key] = value

            # Validate against schema constraints for numeric fields
            if field_type in (float, int):
                min_value = DataValidator.SCHEMA[key].get("min")
                max_value = DataValidator.SCHEMA[key].get("max")

                if min_value is not None and formatted_data[key] < min_value:
                    formatted_data[key] = min_value

                if max_value is not None and formatted_data[key] > max_value:
                    formatted_data[key] = max_value

        except Exception as e:
            st.warning(f"Error processing field '{key}': {str(e)}")
            # Set safe default values
            if field_type == float:
                formatted_data[key] = 0.0
            elif field_type == int:
                formatted_data[key] = 0
            elif field_type == datetime:
                formatted_data[key] = None
            else:
                formatted_data[key] = value

    # Handle required fields
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


# Helper function to check if a value represents an empty date
def is_empty_date(value):
    """
    Check if a value represents an empty/null date.

    Args:
        value: The value to check

    Returns:
        bool: True if the value represents an empty date, False otherwise
    """
    if value is None:
        return True
    if pd.isna(value):
        return True
    if isinstance(value, str) and not value.strip():
        return True
    if value in ["NaT", "NaN"]:
        return True
    return False
