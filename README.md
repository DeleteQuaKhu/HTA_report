def excel_round(number, ndigits=0):
    factor = 10 ** ndigits
    # Multiply the number to shift the decimal place
    shifted_number = number * factor
    # Apply Excel-like rounding: away from zero when halfway
    if shifted_number - int(shifted_number) == 0.5:
        if number >= 0:
            return (int(shifted_number) + 1) / factor
        else:
            return (int(shifted_number) - 1) / factor
    else:
        return round(number, ndigits)
