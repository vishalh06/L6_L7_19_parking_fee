"""Hypothesis fuzz properties and regression cases. Author: Vishal H."""

import importlib.util
from pathlib import Path
import string

import pytest
from hypothesis import given, settings, strategies as st

# Load the sibling file explicitly, so Lab 6's identically named module cannot
# be imported by accident when both labs are collected in one pytest session.
_spec = importlib.util.spec_from_file_location(
    "lab7_parking_fee", Path(__file__).with_name("parking_fee.py")
)
parking_fee = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parking_fee)
minutes_parked = parking_fee.minutes_parked
hourly_rate = parking_fee.hourly_rate
format_plate = parking_fee.format_plate

settings.register_profile("lab7", max_examples=500, deadline=None,
                          derandomize=True, database=None,
                          report_multiple_bugs=False)
settings.load_profile("lab7")

SCALARS = st.one_of(st.none(), st.booleans(), st.integers(), st.floats(),
                    st.text(), st.binary())
INPUTS = st.one_of(SCALARS, st.lists(SCALARS, max_size=8),
                   st.dictionaries(st.text(max_size=12), SCALARS, max_size=5))
NON_TEXT = st.one_of(st.none(), st.booleans(), st.integers(), st.floats(),
                     st.binary(), st.lists(SCALARS, max_size=8))


@given(INPUTS)
def test_minutes_parked_no_crash(value):
    result = minutes_parked(value)
    assert result is None or (type(result) is int and 0 <= result <= 1439)


@given(INPUTS)
def test_hourly_rate_no_crash(value):
    assert hourly_rate(value) in (None, 10, 30, 60)


@given(INPUTS)
def test_format_plate_no_crash(value):
    result = format_plate(value)
    assert result is None or (
        isinstance(result, str) and len(result) == 13
        and result[2] == result[5] == result[8] == " "
    )


@given(st.integers(0, 1439), st.integers(0, 1439))
def test_time_arithmetic(entry, exit_time):
    value = f"{entry // 60:02}:{entry % 60:02}-{exit_time // 60:02}:{exit_time % 60:02}"
    expected = exit_time - entry if exit_time >= entry else None
    assert minutes_parked(value) == expected


@given(st.sampled_from([("bike", 10), ("car", 30), ("truck", 60)]),
       st.sampled_from([str.lower, str.upper, str.title]),
       st.sampled_from(["", " ", "\t", "\n"]))
def test_supported_vehicle_normalization(vehicle_and_rate, transform, padding):
    vehicle, expected = vehicle_and_rate
    assert hourly_rate(padding + transform(vehicle) + padding) == expected


@given(st.text().filter(lambda value: value.strip().lower()
                       not in {"bike", "car", "truck"}))
def test_unknown_vehicles_are_rejected(value):
    assert hourly_rate(value) is None


@st.composite
def plates(draw):
    letters = st.text(alphabet=string.ascii_letters, min_size=2, max_size=2)
    digits2 = st.text(alphabet=string.digits, min_size=2, max_size=2)
    digits4 = st.text(alphabet=string.digits, min_size=4, max_size=4)
    groups = [draw(letters), draw(digits2), draw(letters), draw(digits4)]
    return groups


@given(plates(), st.sampled_from(["", " ", "-", "\t"]))
def test_valid_plate_format_and_idempotence(groups, separator):
    expected = " ".join(groups).upper()
    assert format_plate(separator.join(groups)) == expected
    assert format_plate(expected) == expected


@given(NON_TEXT)
def test_non_string_inputs_are_rejected(value):
    assert minutes_parked(value) is None
    assert hourly_rate(value) is None
    assert format_plate(value) is None


@pytest.mark.parametrize("value, expected", [
    ("09:30-11:45", 135), ("00:00-00:00", 0), ("00:00-23:59", 1439),
    (" 09:30 - 11:45 ", 135), ("23:59-00:00", None),
    ("24:00-25:00", None), ("09:60-11:45", None),
    ("09:30-11:60", None), ("09:30-24:00", None),
    ("9:30-11:45", None), ("09:30", None), ("09:30-11:45-12:00", None),
    ("-1:00-11:00", None), ("０９:３０-１１:４５", None),
    ("09:30-11:45\x00", None), ("", None), (None, None),
    ("0" * 10000, None),
])
def test_time_regressions(value, expected):
    assert minutes_parked(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("bike", 10), (" CAR ", 30), ("Truck", 60), ("bus", None),
    ("", None), (None, None), (17, None), ([], None),
    ("car\x00", None), ("cаr", None), ("car" * 10000, None),
])
def test_vehicle_regressions(value, expected):
    assert hourly_rate(value) == expected


@pytest.mark.parametrize("value, expected", [
    ("ka01ab1234", "KA 01 AB 1234"), ("KA 01 AB 1234", "KA 01 AB 1234"),
    (" ka-01-ab-1234 ", "KA 01 AB 1234"),
    ("", None), ("A", None), (None, None), (123, None),
    ("KA01AB123", None), ("KA01AB12345", None), ("KA01AB1234!", None),
    ("1101AB1234", None), ("KAABAB1234", None),
    ("KA01AB１２３４", None), ("ß01AB1234", None),
    ("KA01AB1234\x00", None), ("a" * 10000, None),
])
def test_plate_regressions(value, expected):
    assert format_plate(value) == expected


def test_cli_valid_inputs(monkeypatch, capsys):
    answers = iter(["09:30-11:45", "car", "ka01ab1234"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    parking_fee.main()
    output = capsys.readouterr().out
    assert "Minutes Parked: 135" in output
    assert "Hourly Rate: 30" in output
    assert "Formatted Plate: KA 01 AB 1234" in output


def test_cli_invalid_inputs_continue(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: "")
    parking_fee.main()
    assert capsys.readouterr().out.count("Invalid input") == 3


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_cli_cancelled_input(monkeypatch, capsys, error):
    def cancel(prompt):
        raise error
    monkeypatch.setattr("builtins.input", cancel)
    parking_fee.main()
    assert "Input cancelled." in capsys.readouterr().out
