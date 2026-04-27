from app.core.sa_id import parse_sa_id, get_risk_group, luhn_check

def test_luhn_valid():
    assert luhn_check("9001155001083") == True

def test_luhn_invalid():
    assert luhn_check("9001155001084") == False

def test_parse_valid_id():
    result = parse_sa_id("9001155001083")
    assert result["valid"] == True
    assert result["age"] == 36
    assert result["gender"] == "male"

def test_parse_invalid_length():
    result = parse_sa_id("123")
    assert result["valid"] == False

def test_risk_groups():
    assert get_risk_group(25) == 1
    assert get_risk_group(40) == 2
    assert get_risk_group(60) == 3
    assert get_risk_group(17) == 0  # ineligible