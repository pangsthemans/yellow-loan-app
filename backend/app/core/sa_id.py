from datetime import date, datetime


def luhn_check(id_number: str) -> bool:
    """Validate SA ID number using Luhn algorithm."""
    total = 0
    reverse_digits = id_number[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def parse_sa_id(id_number: str) -> dict:
    """
    Parse and validate a South African ID number.
    Format: YYMMDD SSSS C A Z
      - YYMMDD: date of birth
      - SSSS: sequence number (females 0000-4999, males 5000-9999)
      - C: citizenship (0 = SA citizen, 1 = permanent resident)
      - A: usually 8 or 9
      - Z: checksum digit
    Returns dict with valid, dob, age, gender, or raises ValueError.
    """
    if not id_number.isdigit() or len(id_number) != 13:
        return {"valid": False, "error": "ID number must be exactly 13 digits"}

    if not luhn_check(id_number):
        return {"valid": False, "error": "ID number failed checksum validation"}

    yy = int(id_number[0:2])
    mm = int(id_number[2:4])
    dd = int(id_number[4:6])

    current_year = date.today().year
    century = 1900 if yy >= (current_year % 100) else 2000
    year = century + yy

    try:
        dob = date(year, mm, dd)
    except ValueError:
        return {"valid": False, "error": "ID number contains invalid date of birth"}

    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    gender_digits = int(id_number[6:10])
    gender = "male" if gender_digits >= 5000 else "female"

    citizenship_digit = int(id_number[10])
    citizenship = "citizen" if citizenship_digit == 0 else "permanent_resident"

    return {
        "valid": True,
        "dob": dob,
        "age": age,
        "gender": gender,
        "citizenship": citizenship,
    }


def get_risk_group(age: int) -> int:
    """Return risk group 1-3 based on age."""
    if 18 <= age <= 30:
        return 1
    elif 31 <= age <= 50:
        return 2
    elif 51 <= age <= 65:
        return 3
    return 0  # ineligible
