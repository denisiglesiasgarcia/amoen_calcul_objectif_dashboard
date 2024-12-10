import pandas as pd
import numpy as np
from io import BytesIO
import streamlit as st
from typing import Union, Dict, Any, Optional
from datetime import datetime
import logging
import traceback
import re

# Configure logging
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


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame column names to be Excel-compatible"""
    df = df.copy()

    def clean_name(name):
        # Convert to string and clean
        name = str(name)
        # Remove any non-alphanumeric characters (except underscores)
        cleaned = re.sub(r"[^\w\s]", "", name)
        # Replace spaces with underscores
        cleaned = re.sub(r"\s+", "_", cleaned)
        # Ensure it starts with a letter
        if not cleaned or not cleaned[0].isalpha():
            cleaned = "col_" + cleaned
        return cleaned

    df.columns = [clean_name(col) for col in df.columns]
    return df


def handle_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Handle data types and missing values in DataFrame"""
    df = df.copy()

    # Replace various null values with empty strings
    df = df.replace({np.nan: "", None: "", "nan": "", "None": "", "NaT": ""})

    # Convert datetime columns to string format
    datetime_columns = df.select_dtypes(include=["datetime64"]).columns
    for col in datetime_columns:
        df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S")

    return df


def convert_df_to_excel(data: Union[pd.DataFrame, Dict[str, Any]]) -> bytes:
    """Convert data to Excel bytes"""
    try:
        # Convert to DataFrame if necessary
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        # Clean column names
        df = clean_column_names(df)

        # Handle data types
        df = handle_data_types(df)

        # Create Excel in memory
        output = BytesIO()

        # Simple Excel export
        df.to_excel(output, index=False)

        # Get the Excel data
        excel_data = output.getvalue()
        output.close()

        if not excel_data:
            raise ExcelExportError("Generated Excel file is empty")

        return excel_data

    except Exception as e:
        logger.error(f"Excel conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        raise ExcelExportError(f"Excel conversion failed: {str(e)}", original_error=e)


def display_dataframe_with_excel_download(
    data: Union[pd.DataFrame, Dict[str, Any]], filename: str = "data.xlsx"
) -> None:
    """Display data in Streamlit with Excel download button"""
    try:
        # Validate filename
        if not isinstance(filename, str):
            filename = str(filename)
        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        # Display the DataFrame
        if isinstance(data, dict):
            display_df = pd.DataFrame([data])
        else:
            display_df = pd.DataFrame(data)

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
