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

def test_nested_unary(icfp):
    assert_interp(icfp, "U- U- I/6", 1337)
    assert_interp(icfp, "U! U! T", True)
    assert_interp(icfp, "U! U! F", False)
    assert_interp(icfp, "U$ U# S4%34", "test")
    assert_interp(icfp, "U# U$ I4%34", 15818151)

# +	Integer addition	B+ I# I$ -> 5
# -	Integer subtraction	B- I$ I# -> 1
# *	Integer multiplication	B* I$ I# -> 6
# /	Integer division (truncated towards zero)	B/ U- I( I# -> -3
# %	Integer modulo	B% U- I( I# -> -1
# <	Integer comparison	B< I$ I# -> false
# >	Integer comparison	B> I$ I# -> true
# =	Equality comparison, works for int, bool and string	B= I$ I# -> false
# |	Boolean or	B| T F -> true
# &	Boolean and	B& T F -> false
# .	String concatenation	B. S4% S34 -> "test"
# T	Take first x chars of string y	BT I$ S4%34 -> "tes"
# D	Drop first x chars of string y	BD I$ S4%34 -> "t"
# $	Apply term x to y (see Lambda abstractions)
def test_basic_binop(icfp):
    assert_interp(icfp, "B+ I# I$", 5)
    assert_interp(icfp, "B- I$ I#", 1)
    assert_interp(icfp, "B* I$ I#", 6)
    assert_interp(icfp, "B/ U- I( I#", -3)
    assert_interp(icfp, "B% U- I( I#", -1)
    assert_interp(icfp, "B< I$ I#", False)
    assert_interp(icfp, "B> I$ I#", True)
    assert_interp(icfp, "B= I$ I#", False)
    assert_interp(icfp, "B| T F", True)
    assert_interp(icfp, "B& T F", False)
    assert_interp(icfp, "B. S4% S34", "test")
    assert_interp(icfp, "BT I$ S4%34", "tes")
    assert_interp(icfp, "BD I$ S4%34", "t")
    # assert_interp(icfp, "B$ U- I( I#", -1337)



