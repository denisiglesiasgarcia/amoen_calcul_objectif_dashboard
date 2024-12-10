import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
from typing import Union, Dict, Any, Optional
from datetime import datetime
import logging
import traceback
import re

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExcelExportError(Exception):
    """Custom exception for Excel export errors with detailed messaging"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


def clean_excel_column_name(name: str) -> str:
    """
    Clean column names to be Excel-compatible.

    Args:
        name: Original column name

    Returns:
        str: Cleaned column name suitable for Excel
    """
    # Convert to string if not already
    name = str(name)

    # Replace invalid Excel characters
    cleaned = re.sub(r"[\[\]*/\\?:]+", "_", name)

    # Remove leading/trailing spaces and underscores
    cleaned = cleaned.strip(" _")

    # Ensure name isn't empty after cleaning
    if not cleaned:
        cleaned = "Column"

    return cleaned


def validate_data(data: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
    """
    Validate and convert input data to DataFrame with comprehensive error checking.

    Args:
        data: Input data (DataFrame or dictionary)

    Returns:
        pd.DataFrame: Validated and processed DataFrame

    Raises:
        ExcelExportError: If validation fails
    """
    try:
        # Check for None or empty input
        if data is None:
            raise ExcelExportError("Input data cannot be None")

        if isinstance(data, dict) and not data:
            raise ExcelExportError("Input dictionary is empty")

        if isinstance(data, dict):
            # Process dictionary items with type checking
            processed_items = []
            for k, v in data.items():
                # Validate key
                if not isinstance(k, (str, int, float)):
                    k = str(k)

                # Process value based on type
                if v is None:
                    processed_value = ""
                elif isinstance(v, (dict, list)):
                    processed_value = str(v)
                elif isinstance(v, (datetime, pd.Timestamp)):
                    processed_value = v.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(v, (int, float)):
                    processed_value = v
                elif isinstance(v, bool):
                    processed_value = str(v)
                else:
                    processed_value = str(v)

                processed_items.append({"Key": k, "Value": processed_value})

            df = pd.DataFrame(processed_items)

        elif isinstance(data, pd.DataFrame):
            # Deep copy to avoid modifying original
            df = data.copy()

            # Handle missing values consistently
            df = df.replace({np.nan: "", None: "", "nan": "", "None": "", "NaT": ""})

            # Convert any remaining problematic types
            for col in df.columns:
                if df[col].dtype == "object":
                    df[col] = df[col].apply(lambda x: str(x) if x != "" else "")

        else:
            raise ExcelExportError(
                f"Unsupported data type: {type(data)}. Expected DataFrame or dictionary."
            )

        # Final validation
        if df.empty:
            raise ExcelExportError("Resulting DataFrame is empty")

        # Clean and validate column names
        df.columns = [clean_excel_column_name(col) for col in df.columns]

        return df

    except ExcelExportError:
        raise
    except Exception as e:
        raise ExcelExportError(f"Data validation failed: {str(e)}", original_error=e)


def convert_df_to_excel(data: Union[pd.DataFrame, Dict[str, Any]]) -> bytes:
    """
    Convert data to Excel bytes with enhanced error handling and formatting.

    Args:
        data: Input data (DataFrame or dictionary)

    Returns:
        bytes: Excel file as bytes

    Raises:
        ExcelExportError: If conversion fails
    """
    output = None
    try:
        # Validate and process input data
        df = validate_data(data)

        # Create Excel file in memory
        output = BytesIO()

        # Write to Excel with formatting
        with pd.ExcelWriter(output, engine="openpyxl", mode="wb") as writer:
            # Write DataFrame
            df.to_excel(writer, index=False, sheet_name="Sheet1", float_format="%.2f")

            # Get worksheet
            worksheet = writer.sheets["Sheet1"]

            # Format columns
            for idx, col in enumerate(df.columns):
                column = df[col]
                # Calculate max length considering header and content
                max_length = max(
                    max(column.astype(str).apply(len).max(), len(str(col)))
                    + 2,  # Add padding
                    5,  # Minimum width
                )
                # Cap maximum width
                max_length = min(max_length, 50)

                # Set column width
                worksheet.column_dimensions[chr(65 + idx)].width = max_length

            # Style header row
            for cell in worksheet[1]:
                cell.style = "Headline 3"

        # Get Excel data
        excel_data = output.getvalue()

        # Verify output
        if not excel_data:
            raise ExcelExportError("Generated Excel file is empty")

        return excel_data

    except ExcelExportError:
        raise
    except Exception as e:
        raise ExcelExportError(f"Excel conversion failed: {str(e)}", original_error=e)
    finally:
        if output:
            output.close()


def display_dataframe_with_excel_download(
    data: Union[pd.DataFrame, Dict[str, Any]], filename: str = "data.xlsx"
) -> None:
    """
    Display data in Streamlit with Excel download button and error handling.

    Args:
        data: Input data (DataFrame or dictionary)
        filename: Name of the Excel file for download
    """
    try:
        # Validate filename
        if not isinstance(filename, str):
            filename = str(filename)
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        # Process data
        display_df = validate_data(data)

        # Display data
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Generate Excel file
        excel_data = convert_df_to_excel(data)

        # Create download button
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    except ExcelExportError as e:
        error_msg = f"Error: {e.message}"
        if e.original_error:
            logger.error(f"{error_msg}\nOriginal error: {traceback.format_exc()}")
        else:
            logger.error(error_msg)
        st.error(error_msg)
