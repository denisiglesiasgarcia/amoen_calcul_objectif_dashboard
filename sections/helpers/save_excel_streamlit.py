# sections/helpers/save_excel_streamlit.py

import pandas as pd
from io import BytesIO
import streamlit as st


def convert_df_to_excel(df, sheet_name="Sheet1"):
    """
    Convert a DataFrame to Excel bytes for download with formatting preserved.

    Args:
        df (pd.DataFrame): DataFrame to convert
        sheet_name (str): Name of the sheet in Excel file

    Returns:
        bytes: Excel file as bytes
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            sheet_name=sheet_name,
            index=False,
            float_format="%.2f",  # Format numbers to 2 decimal places
        )

        # Auto-adjust columns' width
        worksheet = writer.sheets[sheet_name]
        for idx, col in enumerate(df.columns):
            series = df[col]
            max_length = (
                max(
                    series.astype(str).apply(len).max(),  # Length of largest value
                    len(str(series.name)),  # Length of column name
                )
                + 2
            )  # Add a little extra space
            worksheet.column_dimensions[chr(65 + idx)].width = max_length

    return output.getvalue()


# Example usage in your Streamlit app:
def display_dataframe_with_excel_download(df, filename="data.xlsx"):
    """
    Display a DataFrame in Streamlit with an Excel download button.

    Args:
        df (pd.DataFrame): DataFrame to display and make downloadable
        filename (str): Name of the file to be downloaded
    """
    # Display the dataframe
    st.dataframe(df)

    # Add download button
    excel_data = convert_df_to_excel(df)
    st.download_button(
        label="📥 Download as Excel",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
