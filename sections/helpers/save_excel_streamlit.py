# /sections/helpers/save_excel_streamlit.py

import pandas as pd
from io import BytesIO
import streamlit as st
from typing import Union, Dict, Any, Optional
import logging
import traceback
import re

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ExcelExportError(Exception):
    """Custom exception for Excel export errors"""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class DataFrameFormatter:
    """Handles DataFrame formatting and type conversion"""

    @staticmethod
    def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convert datetime columns to formatted strings"""
        for col in df.select_dtypes(include=["datetime64"]).columns:
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        return df

    @staticmethod
    def convert_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
        """Convert numeric-like object columns to proper numeric types"""
        for col in df.select_dtypes(include=["object"]).columns:
            # Try to convert to numeric
            numeric_series = pd.to_numeric(df[col], errors="coerce")
            # If at least 90% of non-null values were converted successfully, keep the conversion
            if numeric_series.notna().sum() >= df[col].notna().sum() * 0.9:
                df[col] = numeric_series
        return df

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names to be Excel-compatible"""

        def clean_name(name: str) -> str:
            # Remove or replace invalid characters
            cleaned = re.sub(r"[^\w\s-]", "", str(name))
            # Replace spaces with underscores
            cleaned = re.sub(r"\s+", "_", cleaned)
            # Ensure name starts with a letter
            if cleaned and not cleaned[0].isalpha():
                cleaned = "col_" + cleaned
            # Ensure name isn't empty
            return cleaned or "column"

        df.columns = [clean_name(col) for col in df.columns]
        return df

    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Replace missing values with appropriate defaults"""
        # Define replacement map for different dtypes
        replacement_map = {
            "object": "",
            "float64": 0.0,
            "int64": 0,
            "datetime64[ns]": None,
            "bool": False,
        }

        for col in df.columns:
            dtype_str = str(df[col].dtype)
            replace_value = replacement_map.get(dtype_str, "")
            df[col] = df[col].fillna(replace_value)

        return df


def prepare_dataframe_for_display(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare DataFrame for display by ensuring consistent data types.

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with consistent types and formatted values
    """
    try:
        df = df.copy()

        # Clean column names
        df = DataFrameFormatter.clean_column_names(df)

        # Convert datetime columns
        df = DataFrameFormatter.convert_datetime_columns(df)

        # Convert numeric columns
        df = DataFrameFormatter.convert_numeric_columns(df)

        # Handle missing values
        df = DataFrameFormatter.handle_missing_values(df)

        return df

    except Exception as e:
        logger.error(f"Error preparing DataFrame for display: {str(e)}")
        logger.error(traceback.format_exc())
        raise ExcelExportError(
            "Failed to prepare DataFrame for display", original_error=e
        )


def convert_df_to_excel(data: Union[pd.DataFrame, Dict[str, Any]]) -> bytes:
    """
    Convert DataFrame or dictionary to Excel bytes.

    Args:
        data: Input data (DataFrame or dictionary)

    Returns:
        Excel file as bytes
    """
    try:
        # Convert to DataFrame if necessary
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        # Prepare data for Excel
        df = prepare_dataframe_for_display(df)

        # Create Excel in memory
        output = BytesIO()

        try:
            # Write to Excel
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")

            # Get the Excel data
            excel_data = output.getvalue()

            return excel_data

        finally:
            output.close()

    except Exception as e:
        logger.error(f"Excel conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        raise ExcelExportError(f"Excel conversion failed: {str(e)}", original_error=e)


def display_dataframe_with_excel_download(
    data: Union[pd.DataFrame, Dict[str, Any]], filename: str = "data.xlsx"
) -> None:
    """
    Display DataFrame and provide Excel download button.

    Args:
        data: Input data (DataFrame or dictionary)
        filename: Name of the Excel file for download
    """
    try:
        # Input validation
        if data is None:
            st.error("No data provided")
            return

        # Convert to DataFrame if necessary
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        if df.empty:
            st.info("No data to display")
            return

        # Prepare DataFrame for display
        display_df = prepare_dataframe_for_display(df)

        # Display the DataFrame
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Generate Excel file
        excel_data = convert_df_to_excel(df)

        # Ensure filename has .xlsx extension
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

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

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        st.error(error_msg)
