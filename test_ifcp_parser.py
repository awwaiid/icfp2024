import pytest

from icfp_parser import ICFP


@pytest.fixture
def icfp():
    return ICFP()



def test_unary_integer_negation(icfp):
    input_token = "U- I$"
    expected_output = -3
    decoded = icfp.decode(input_token)
    assert decoded == ("U-", expected_output)
    encoded = icfp.encode(decoded)
    assert encoded == input_token

def test_unary_boolean_not(icfp):
    input_token = "U! T"
    expected_output = False
    decoded = icfp.decode(input_token)
    assert decoded == ("U!", expected_output)
    encoded = icfp.encode(decoded)
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

if __name__ == "__main__":
    pytest.main()
