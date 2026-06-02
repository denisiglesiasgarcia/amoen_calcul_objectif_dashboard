# sections/helpers/sanitize_mongo.py

import logging
import math
from datetime import datetime
from typing import Any, Dict, Optional, Type, Union

from bson import ObjectId
from dateutil import parser as dateutil_parser

from sections.helpers.admin.admin_db_mgmt import DataValidator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _is_null(value: Any) -> bool:
    """Return True for None or float NaN; False otherwise."""
    if value is None:
        return True
    try:
        return math.isnan(float(value))
    except (TypeError, ValueError):
        return False


class DataSanitizer:
    """Handles sanitization of database records."""

    @staticmethod
    def _convert_date(value: Any) -> Optional[datetime]:
        """
        Convert various date formats to datetime.

        Supports datetime instances and ISO/common string formats.
        Returns None on failure or null input.
        """
        if _is_null(value):
            return None
        try:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                return dateutil_parser.parse(value)
            return None
        except (ValueError, OverflowError) as e:
            logger.warning("Date conversion failed: %s", e)
            return None

    @staticmethod
    def _convert_numeric(
        value: Any, type_: Type[Union[int, float]]
    ) -> Union[int, float]:
        """
        Convert value to the specified numeric type.

        Returns 0 (cast to type_) on null or conversion failure.
        """
        if _is_null(value):
            return type_(0)
        try:
            if isinstance(value, (int, float, str)):
                return type_(value)
            return type_(0)
        except (ValueError, TypeError) as e:
            logger.warning("Numeric conversion failed: %s", e)
            return type_(0)

    @staticmethod
    def _get_default_value(type_: Type) -> Any:
        """Return the default sentinel value for a given type."""
        defaults: Dict[Type, Any] = {
            float: 0.0,
            int: 0,
            str: "",
            datetime: None,
            bool: False,
        }
        return defaults.get(type_)

    @classmethod
    def _sanitize_field(
        cls, key: str, value: Any, field_type: Type, schema: Dict[str, Any]
    ) -> Any:
        """
        Sanitize a single field according to its declared type and schema.

        Applies min/max clamping for numeric types.
        """
        try:
            if value is None and not schema.get("required", False):
                return None

            if field_type is datetime:
                return cls._convert_date(value)

            if field_type is float:
                val = cls._convert_numeric(value, float)
                min_val = schema.get("min")
                max_val = schema.get("max")
                if min_val is not None:
                    val = max(min_val, val)
                if max_val is not None:
                    val = min(max_val, val)
                return val

            if field_type is int:
                val = cls._convert_numeric(value, int)
                min_val = schema.get("min")
                max_val = schema.get("max")
                if min_val is not None:
                    val = max(min_val, val)
                if max_val is not None:
                    val = min(max_val, val)
                return val

            if field_type is str:
                return str(value) if value is not None else ""

            if field_type is bool:
                if isinstance(value, str):
                    return value.lower() in ("true", "1", "yes", "y")
                return bool(value)

            return value

        except Exception as e:  # noqa: BLE001
            logger.warning("Field sanitization failed for %s: %s", key, e)
            return cls._get_default_value(field_type)


def sanitize_db(data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Sanitize and validate a MongoDB document against the schema.

    Returns the sanitized dict, or the original dict if sanitization fails.
    """
    if not data:
        logger.warning("Received empty data for sanitization")
        return None

    try:
        formatted_data: Dict[str, Any] = {}

        # Normalise ObjectId to string
        if "_id" in data:
            formatted_data["_id"] = (
                str(data["_id"]) if isinstance(data["_id"], ObjectId) else data["_id"]
            )

        # First pass: schema-validated fields via DataValidator
        converted_data, validation_errors = DataValidator.validate_and_convert(data)
        for error in validation_errors:
            logger.warning("Validation warning: %s", error)
        formatted_data.update(converted_data)

        # Second pass: remaining fields not covered by DataValidator
        for key, value in data.items():
            if key in formatted_data or key == "_id":
                continue
            schema = DataValidator.SCHEMA.get(key, {})
            field_type = schema.get("type", str)
            formatted_data[key] = DataSanitizer._sanitize_field(
                key, value, field_type, schema
            )

        # Ensure required fields are always present
        for field, schema in DataValidator.SCHEMA.items():
            if schema.get("required", False) and (
                field not in formatted_data or formatted_data[field] is None
            ):
                formatted_data[field] = DataSanitizer._get_default_value(schema["type"])

        # Warn if sre_pourcentage_* fields do not sum to 100
        pct_fields = [k for k in formatted_data if k.startswith("sre_pourcentage_")]
        if pct_fields:
            total = sum(formatted_data.get(f, 0) for f in pct_fields)
            if abs(total - 100) > 0.01:
                logger.warning(
                    "Percentage fields sum to %.2f%% (expected 100%%)", total
                )

        return formatted_data

    except Exception as e:  # noqa: BLE001
        logger.error("Database sanitization failed: %s", e)
        return data  # Return original on unexpected failure
