import pytest

from icfp_interp import ICFP

@pytest.fixture
def icfp():
    return ICFP()

def assert_interp(icfp, input, expected_output):
    result, rest = icfp.interp_from_string(input)
    assert result == expected_output
    assert rest == []

def test_basic_boolean(icfp):
    assert_interp(icfp, "T", True)
    assert_interp(icfp, "F", False)

def test_basic_string(icfp):
    assert_interp(icfp, "S(%,,/", "hello")

def test_basic_integer(icfp):
    assert_interp(icfp, "I/6", 1337)

def test_basic_unary(icfp):
    assert_interp(icfp, "U- I/6", -1337)
    assert_interp(icfp, "U! T", False)
    assert_interp(icfp, "U! F", True)
    assert_interp(icfp, "U# S4%34", 15818151)
    assert_interp(icfp, "U$ I4%34", "test")

# def test_basic_binop(icfp):
#     assert_interp(icfp, "U! T", False)
#     assert_interp(icfp, "U! F", True)

