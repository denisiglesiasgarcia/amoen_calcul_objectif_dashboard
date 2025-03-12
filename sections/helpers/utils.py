# /sections/helpers/utils.py


def get_rounded_float(dictionary, key, decimals=2):
    """
    Get value from dictionary, convert to float, and round to specified decimals.
    Returns 0.0 if value is missing or conversion fails.

    Args:
        dictionary: Dictionary to get value from
        key: Dictionary key to look up
        decimals: Number of decimal places (default: 2)

    Returns:
        float: Rounded number or 0.0
    """
    try:
        # Get the value with a default of 0
        value = dictionary.get(key)

        # If value is None, return 0
        if value is None:
            return 0.0

        # Convert to string, clean it, and convert to float
        cleaned_value = str(value).strip().replace(",", ".")

        # Convert to float and round
        return round(float(cleaned_value), decimals)

    except Exception as e:
        print(f"Error converting {key}: {value}, Error: {str(e)}")  # Debug print
        return 0.0
