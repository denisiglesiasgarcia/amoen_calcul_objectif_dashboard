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


def debug_dataframe(df: pd.DataFrame) -> None:
    """
    Print debug information about DataFrame columns and types.
    """
    print("\nDEBUG INFO:")
    print("Column names and types:")
    for col in df.columns:
        print(f"Column: '{col}' | Type: {type(col)} | Content type: {df[col].dtype}")

    # Check for problematic characters
    for col in df.columns:
        if any(char in str(col) for char in "[]*/\\?:"):
            print(f"Problematic column found: '{col}'")

    return df


class ExcelExportError(Exception):
    """Custom exception for Excel export errors with detailed messaging"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


def clean_excel_column_name(name: str) -> str:
    """
    Clean column names to be Excel-compatible.
    """
    # Convert to string and clean invalid characters
    name = str(name).strip()

    # Replace problematic characters with underscores
    cleaned = re.sub(r"[\[\]*/\\?:]", "", name)  # Remove problematic characters
    cleaned = re.sub(r"\s+", "_", cleaned)  # Replace spaces with underscores
    cleaned = re.sub(r"_+", "_", cleaned)  # Replace multiple underscores with single
    cleaned = cleaned.strip("_")  # Remove leading/trailing underscores

    # Ensure the name isn't empty
    if not cleaned:
        cleaned = "Column"

    # Ensure the name starts with a letter
    if not cleaned[0].isalpha():
        cleaned = "Col_" + cleaned

    return cleaned


def clean_dataframe_for_excel(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for Excel export by cleaning column names and data.

    Args:
        df: Input DataFrame

    Returns:
        pd.DataFrame: Cleaned DataFrame ready for Excel export
    """
    # Make a deep copy to avoid modifying the original
    df = df.copy()

    # Clean column names
    df.columns = [clean_excel_column_name(col) for col in df.columns]

    # Handle missing values and problematic data types
    df = df.replace({np.nan: "", None: "", "nan": "", "None": "", "NaT": ""})

    # Convert problematic types to strings
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).replace("nan", "").replace("None", "")

    return df


def validate_data(data: Union[pd.DataFrame, Dict[str, Any]]) -> pd.DataFrame:
    """
    Validate and convert input data to DataFrame with comprehensive error checking.
    """
    try:
        # Check for None or empty input
        if data is None:
            raise ExcelExportError("Input data cannot be None")

        if isinstance(data, dict) and not data:
            raise ExcelExportError("Input dictionary is empty")

        if isinstance(data, dict):
            processed_items = []
            for k, v in data.items():
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
                else:
                    processed_value = str(v)

                processed_items.append({"Key": k, "Value": processed_value})

            df = pd.DataFrame(processed_items)
        elif isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ExcelExportError(
                f"Unsupported data type: {type(data)}. Expected DataFrame or dictionary."
            )

        # Final validation
        if df.empty:
            raise ExcelExportError("Resulting DataFrame is empty")

        # Add debug information before cleaning
        print("\nBefore cleaning:")
        debug_dataframe(df)

        # Clean DataFrame for Excel
        df = clean_dataframe_for_excel(df)

        # Add debug information after cleaning
        print("\nAfter cleaning:")
        debug_dataframe(df)

        return df

    except ExcelExportError:
        raise
    except Exception as e:
        raise ExcelExportError(f"Data validation failed: {str(e)}", original_error=e)


def convert_df_to_excel(data: Union[pd.DataFrame, Dict[str, Any]]) -> bytes:
    """
    Convert data to Excel bytes with enhanced error handling and formatting.
    """
    output = None
    try:
        # Create a copy of the data to avoid modifying the original
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            df = pd.DataFrame(data)

        # Clean column names explicitly before Excel conversion
        cleaned_columns = {col: clean_excel_column_name(col) for col in df.columns}
        df = df.rename(columns=cleaned_columns)

        # Handle missing values
        df = df.replace({np.nan: "", None: "", "nan": "", "None": "", "NaT": "", "[": "", "]": ""})

        # Create Excel file in memory
        output = BytesIO()

        # Write to Excel with formatting
        with pd.ExcelWriter(output, engine="openpyxl", mode="wb") as writer:
            # Write DataFrame
            df.to_excel(writer, index=False, sheet_name="Sheet1")

            # Get worksheet
            worksheet = writer.sheets["Sheet1"]

            # Format columns
            for idx, col in enumerate(df.columns):
                # Get maximum content length
                content_length = max(df[col].astype(str).str.len().max(), len(str(col)))

                # Set column width (with minimum and maximum limits)
                width = min(max(content_length + 2, 8), 50)
                col_letter = chr(65 + idx)
                worksheet.column_dimensions[col_letter].width = width

            # Style header row
            for cell in worksheet[1]:
                cell.style = "Headline 3"

        excel_data = output.getvalue()

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
    """
    try:
        # Validate filename
        filename = str(filename)
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        # Display original data
        st.dataframe(data, use_container_width=True, hide_index=True)

        # Generate Excel file with cleaned column names
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
