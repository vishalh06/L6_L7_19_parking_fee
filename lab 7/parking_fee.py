"""Parking input validation for Lab 7. Author: Vishal H.

Invalid values return None. Times refer to the same calendar day; an exit
earlier than entry is rejected because dates are not part of this interface.
Plates use the lab's AA00AA0000 layout (not every Indian plate category).
"""

import re

RATES = {"bike": 10, "car": 30, "truck": 60}
_TIME_RANGE = re.compile(
    r"([0-9]{2}):([0-9]{2})\s*-\s*([0-9]{2}):([0-9]{2})"
)
_PLATE = re.compile(r"[A-Za-z]{2}[0-9]{2}[A-Za-z]{2}[0-9]{4}")


def minutes_parked(times):
    """Return same-day elapsed minutes, or None for an invalid time range."""
    if not isinstance(times, str) or len(times) > 64:
        return None
    match = _TIME_RANGE.fullmatch(times.strip())
    if match is None:
        return None
    h1, m1, h2, m2 = map(int, match.groups())
    if h1 > 23 or h2 > 23 or m1 > 59 or m2 > 59:
        return None
    elapsed = (h2 * 60 + m2) - (h1 * 60 + m1)
    return elapsed if elapsed >= 0 else None


def hourly_rate(vehicle):
    """Return the supported vehicle's hourly rate, or None if unsupported."""
    if not isinstance(vehicle, str) or len(vehicle) > 32:
        return None
    return RATES.get(vehicle.strip().lower())


def format_plate(plate):
    """Normalize a compact or space/hyphen-separated AA00AA0000 plate."""
    if not isinstance(plate, str) or len(plate) > 32:
        return None
    compact = re.sub(r"[ \t\r\n\f\v-]", "", plate)
    # Validate before uppercasing, which can expand some Unicode characters.
    if _PLATE.fullmatch(compact) is None:
        return None
    p = compact.upper()
    return f"{p[:2]} {p[2:4]} {p[4:6]} {p[6:]}"


def main():
    cases = (
        ("minutes_parked", "Enter entry and exit time (e.g. 09:30-11:45): ",
         minutes_parked, "Minutes Parked"),
        ("hourly_rate", "Enter vehicle type (bike/car/truck): ",
         hourly_rate, "Hourly Rate"),
        ("format_plate", "Enter a number plate (e.g. ka01ab1234): ",
         format_plate, "Formatted Plate"),
    )
    for name, prompt, function, label in cases:
        print(f"==== Running {name} ====")
        try:
            value = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nInput cancelled.")
            return
        result = function(value)
        print(f"{label}: {result if result is not None else 'Invalid input'}\n")


if __name__ == "__main__":
    main()
