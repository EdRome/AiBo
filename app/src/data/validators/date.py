import re
import pandas as pd

def validate_date(data):
    date_columns = []
    date_pattern_hyphen = r'^\d{4}-\d{2}-\d{2}$'
    date_time_pattern_hyphen = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    date_pattern_slash = r'^\d{2}/\d{2}/\d{4}$'
    date_time_pattern_slash = r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$'

    for col in data.columns:
        # Intentar convertir la columna a datetime, ignorando errores
        try:
            # Verificar si la columna es una fecha o una fecha y hora
            is_date = data[col].apply(
                lambda x: re.match(date_pattern_hyphen, x) or 
                        re.match(date_time_pattern_hyphen, x) or 
                        re.match(date_pattern_slash, x) or 
                        re.match(date_time_pattern_slash, x)
            )

            # Si más del 80% de los valores son fechas válidas, consideramos que es columna de fecha
            if is_date.notna().mean() > 0.8:
                date_columns.append(col)
        except Exception:
            pass

    return date_columns

def validate_date_2(data):
    date_columns = []
    date_patterns = {
        "date_pattern_year_first_hyphen" : r'^\d{4}-\d{2}-\d{2}$',
        "date_pattern_year_first_slash" : r'^\d{4}/\d{2}/\d{2}$',

        "date_pattern_year_last_hyphen" : r'^\d{2}-\d{2}-\d{4}$',
        "date_pattern_year_last_slash" : r'^\d{2}/\d{2}/\d{4}$',

        "date_time_seconds_pattern_year_first_hyphen": r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
        "date_time_seconds_pattern_year_first_slash": r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$',

        "date_time_seconds_pattern_year_last_hyphen" : r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2}$',
        "date_time_seconds_pattern_year_last_slash" : r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$',

        "date_time_pattern_year_first_hyphen" : r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$',
        "date_time_pattern_year_first_slash" : r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$',

        "date_time_pattern_year_last_hyphen" : r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$',
        "date_time_pattern_year_last_slash" : r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}$', 
    }

    for col in data.columns:
        key_match = ""
        pattern_match = ""
        try:
            for key, pattern in date_patterns.items():
                _match = re.match(pattern, data[col][0])
                if _match:
                    key_match = key
                    pattern_match = pattern
                    break

            if key_match:
                is_date = data[col].apply(lambda x: re.match(pattern_match, x))
                if is_date.notna().mean() > 0.8:
                    date_columns.append(col)
        except Exception as e:
            print("Error en column:", col, "con error:", e)

    return date_columns