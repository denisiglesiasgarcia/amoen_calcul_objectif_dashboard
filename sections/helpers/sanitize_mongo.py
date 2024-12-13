from datetime import datetime
from sections.helpers.admin.admin_db_mgmt import DataValidator
import pandas as pd
from typing import Optional, Dict, Any, Union, Type
import logging
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def safe_convert_to_float(value, default=0.0):
    """
    Convert a value to float. Returns default if conversion fails.

    Args:
        value: Number to convert (str, int, float, or None)
        default: Value to return if conversion fails

    Returns:
        float: Converted number or default value

    Examples:
        >>> to_float("1.23")
        1.23
        >>> to_float("bad")
        0.0
        >>> to_float(None)
        0.0
    """
    if value is None:
        return default

    try:
        return float(str(value).strip().replace(",", "."))
    except:
        return default


class DataSanitizer:
    """Handles sanitization of database records."""

    @staticmethod
    def _convert_date(value: Any) -> Optional[datetime]:
        """
        Convert various date formats to datetime.

        Args:
            value: Value to convert

        Returns:
            datetime object or None if conversion fails
        """
        if value is None or pd.isna(value):
            return None

        try:
            if isinstance(value, (datetime, pd.Timestamp)):
                return pd.Timestamp(value).to_pydatetime()
            elif isinstance(value, str):
                return pd.to_datetime(value).to_pydatetime()
            return None
        except Exception as e:
            logger.warning(f"Date conversion failed: {str(e)}")
            return None

    @staticmethod
    def _convert_numeric(
        value: Any, type_: Type[Union[int, float]]
    ) -> Union[int, float]:
        """
        Convert value to specified numeric type.

        Args:
            value: Value to convert
            type_: Target numeric type (int or float)

        Returns:
            Converted numeric value or 0 if conversion fails
        """
        if value is None or pd.isna(value):
            return type_(0)

        try:
            if isinstance(value, (int, float, str)):
                return type_(value)
            return type_(0)
        except (ValueError, TypeError) as e:
            logger.warning(f"Numeric conversion failed: {str(e)}")
            return type_(0)

    @staticmethod
    def _get_default_value(type_: Type) -> Any:
        """
        Get default value for a given type.

        Args:
            type_: Type to get default value for

        Returns:
            Default value for the specified type
        """
        defaults = {float: 0.0, int: 0, str: "", datetime: None, bool: False}
        return defaults.get(type_, None)

    @classmethod
    def _sanitize_field(
        cls, key: str, value: Any, field_type: Type, schema: Dict[str, Any]
    ) -> Any:
        """
        Sanitize a single field according to its type and schema.

        Args:
            key: Field name
            value: Field value
            field_type: Expected type
            schema: Field schema

        Returns:
            Sanitized value
        """
        try:
            if value is None and not schema.get("required", False):
                return None

            if field_type == datetime:
                return cls._convert_date(value)
            elif field_type == float:
                val = cls._convert_numeric(value, float)
                min_val = schema.get("min")
                max_val = schema.get("max")
                if min_val is not None:
                    val = max(min_val, val)
                if max_val is not None:
                    val = min(max_val, val)
                return val
            elif field_type == int:
                val = cls._convert_numeric(value, int)
                min_val = schema.get("min")
                max_val = schema.get("max")
                if min_val is not None:
                    val = max(min_val, val)
                if max_val is not None:
                    val = min(max_val, val)
                return val
            elif field_type == str:
                return str(value) if value is not None else ""
            elif field_type == bool:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "y")
                return bool(value)
            else:
                return value

        except Exception as e:
            logger.warning(f"Field sanitization failed for {key}: {str(e)}")
            return cls._get_default_value(field_type)


def sanitize_db(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitizes and validates database records according to the schema.

    Args:
        data: Dictionary containing database record fields

    Returns:
        Sanitized dictionary with validated data types and values
    """
    if not data:
        logger.warning("Received empty data for sanitization")
        return None

    try:
        # Handle ObjectId and create a copy
        formatted_data = {}
        if "_id" in data:
            formatted_data["_id"] = (
                str(data["_id"]) if isinstance(data["_id"], ObjectId) else data["_id"]
            )

        # First pass: Use DataValidator for schema-defined fields
        converted_data, validation_errors = DataValidator.validate_and_convert(data)
        if validation_errors:
            for error in validation_errors:
                logger.warning(f"Validation warning: {error}")

        # Update formatted data with validated fields
        formatted_data.update(converted_data)

        # Second pass: Handle remaining fields
        for key, value in data.items():
            if key not in formatted_data and key != "_id":
                schema = DataValidator.SCHEMA.get(key, {})
                field_type = schema.get("type", str)

                sanitized_value = DataSanitizer._sanitize_field(
                    key, value, field_type, schema
                )
                formatted_data[key] = sanitized_value

        # Ensure all required fields have values
        for field, schema in DataValidator.SCHEMA.items():
            if schema.get("required", False) and (
                field not in formatted_data or formatted_data[field] is None
            ):
                formatted_data[field] = DataSanitizer._get_default_value(schema["type"])

        # Validate percentage fields sum
        percentage_fields = [
            f for f in formatted_data.keys() if f.startswith("sre_pourcentage_")
        ]
        if percentage_fields:
            total = sum(formatted_data.get(f, 0) for f in percentage_fields)
            if abs(total - 100) > 0.01:
                logger.warning(
                    f"Percentage fields sum warning: total is {total}% (should be 100%)"
                )

        return formatted_data

    except Exception as e:
        logger.error(f"Database sanitization failed: {str(e)}")
        return data  # Return original data if sanitization fails
