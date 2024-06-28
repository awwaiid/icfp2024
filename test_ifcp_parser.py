import pytest

from icfp_parser import ICFP

@pytest.fixture
def icfp():
    return ICFP()


def test_language_test(icfp):
    input_token = "? B= B$ B$ B$ B$ L$ L$ L$ L# v$ I\" I# I$ I% I$ ? B= B$ L$ v$ I+ I+ ? B= BD I$ S4%34 S4 ? B= BT I$ S4%34 S4%3 ? B= B. S4% S34 S4%34 ? U! B& T F ? B& T T ? U! B| F F ? B| F T ? B< U- I$ U- I# ? B> I$ I# ? B= U- I\" B% U- I$ I# ? B= I\" B% I( I$ ? B= U- I\" B/ U- I$ I# ? B= I# B/ I( I$ ? B= I' B* I# I$ ? B= I$ B+ I\" I# ? B= U$ I4%34 S4%34 ? B= U# S4%34 I4%34 ? U! F ? B= U- I$ B- I# I& ? B= I$ B- I& I# ? B= S4%34 S4%34 ? B= F F ? B= I$ I$ ? T B. B. SM%,&k#(%#+}IEj}3%.$}z3/,6%},!.'5!'%y4%34} U$ B+ I# B* I$> I1~s:U@ Sz}4/}#,!)-}0/).43}&/2})4 S)&})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}k})3}./4}#/22%#4 S5.!29}k})3}./4}#/22%#4 S5.!29}_})3}./4}#/22%#4 S5.!29}a})3}./4}#/22%#4 S5.!29}b})3}./4}#/22%#4 S\").!29}i})3}./4}#/22%#4 S\").!29}h})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}r})3}./4}#/22%#4 S\").!29}p})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}l})3}./4}#/22%#4 S\").!29}N})3}./4}#/22%#4 S\").!29}>})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4"

    decoded = icfp.decode(input_token)
    encoded = icfp.encode(decoded)

    assert encoded == input_token



def test_unary_integer_negation(icfp):
    input_token = "U- I$"
    expected_output = -3
    decoded = icfp.decode(input_token)
    assert decoded ==  expected_output
    encoded = icfp.encode(decoded, "-")
    assert encoded == input_token

def test_unary_boolean_not(icfp):
    input_token = "U! T"
    expected_output = False
    decoded = icfp.decode(input_token)
    assert decoded == ("U!", expected_output)
    encoded = icfp.encode(decoded, "!")
    assert encoded == input_token

def test_unary_string_to_int(icfp):
    input_token = "U# S4%34"
    expected_output = 15818151
    decoded = icfp.decode(input_token)
    assert decoded == ("U#", expected_output)
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_unary_int_to_string(icfp):
    input_token = "U$ I4%34"
    expected_output = "test"
    decoded = icfp.decode(input_token)
    assert decoded == ("U$", expected_output)
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_basic_string(icfp):
    input_token = "SB%,,/}Q/2,$_"
    expected_output = "Hello World!"
    decoded = icfp.decode(input_token)
    assert decoded == expected_output
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_basic_true_boolean(icfp):
    input_token = "T"
    expected_output = True
    decoded = icfp.decode(input_token)
    assert decoded == expected_output
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_basic_false_boolean(icfp):
    input_token = "F"
    expected_output = False
    decoded = icfp.decode(input_token)
    assert decoded == expected_output
    encoded = icfp.encode(decoded)
    assert encoded == input_token


def test_basic_integer(icfp):
    input_token = "I/6"
    expected_output = 1337
    decoded = icfp.decode(input_token)
    assert decoded == expected_output
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_encode_decode_integer(icfp):
    assert icfp.encode(1337) == "I/6"
    assert icfp.decode("I/6") == 1337
    assert icfp.encode(0) == "I!"
    assert icfp.decode("I!") == 0

