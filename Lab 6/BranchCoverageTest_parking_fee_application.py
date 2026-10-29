import pytest

from parking_fee import parking_fee, find_slot, monthly_pass


def test_unknown_vehicle():
    with pytest.raises(ValueError, match="unknown vehicle"):
        parking_fee("bus", 60, False, False)


def test_negative_duration():
    with pytest.raises(ValueError, match="invalid duration"):
        parking_fee("car", -1, False, False)


def test_free_short_stay():
    assert parking_fee("car", 20, False, False) == 0


def test_partial_hour():
    assert parking_fee("car", 61, False, False) == 60


def test_ev_discount():
    assert parking_fee("car", 61, True, False) == 30


def test_lost_ticket():
    assert parking_fee("bike", 61, False, True) == 220


def test_parking_full():
    assert find_slot("car", 0, False) == "full"


def test_disabled_parking():
    assert find_slot("car", 5, True) == "ground floor"


def test_truck_parking():
    assert find_slot("truck", 5, False) == "basement"


def test_regular_parking():
    assert find_slot("car", 5, False) == "any floor"


def test_resident_bike_pass():
    assert monthly_pass("bike", True) == 400


def test_resident_car_pass():
    assert monthly_pass("car", True) == 1200


def test_unsupported_monthly_pass():
    with pytest.raises(ValueError, match="no pass for this vehicle"):
        monthly_pass("truck", False)

def test_exact_hour():
    assert parking_fee("car", 60, False, False) == 30


def test_ev_truck_has_no_discount():
    assert parking_fee("truck", 60, True, False) == 60


def test_non_resident_bike_pass():
    assert monthly_pass("bike", False) == 500


def test_non_resident_car_pass():
    assert monthly_pass("car", False) == 1500


@pytest.mark.parametrize("minutes", [0, 30])
def test_free_parking_boundaries(minutes):
    assert parking_fee("car", minutes, False, False) == 0


def test_first_paid_minute():
    assert parking_fee("car", 31, False, False) == 30


def test_lost_ticket_during_free_stay():
    assert parking_fee("car", 20, False, True) == 200


def test_full_parking_takes_priority():
    assert find_slot("truck", 0, True) == "full"


def test_disabled_parking_takes_priority_over_truck():
    assert find_slot("truck", 1, True) == "ground floor"


def test_negative_free_slots():
    assert find_slot("car", -1, False) == "full"