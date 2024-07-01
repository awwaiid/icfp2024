import pytest

from icfp_interp import ICFP

@pytest.fixture
def icfp():
    return ICFP()

def assert_interp(icfp, input, expected_output):
    result = icfp.interp_from_string(input)
    print(f"result: {result}")
    value = result["value"]
    assert value == expected_output

def assert_eval(icfp, input, expected_output):
    result = icfp.eval_from_string(input)
    print(f"result: {result}")
    assert result == expected_output

def test_basic_boolean(icfp):
    assert_interp(icfp, "T", True)
    assert_interp(icfp, "F", False)

def test_eval_basic_boolean(icfp):
    assert_eval(icfp, "T", True)
    assert_eval(icfp, "F", False)

def test_basic_string(icfp):
    assert_interp(icfp, "S(%,,/", "hello")

def test_eval_basic_string(icfp):
    assert_eval(icfp, "S(%,,/", "hello")

def test_basic_integer(icfp):
    assert_interp(icfp, "I/6", 1337)

def test_eval_basic_integer(icfp):
    assert_eval(icfp, "I/6", 1337)

def test_basic_unary(icfp):
    assert_interp(icfp, "U- I/6", -1337)
    assert_interp(icfp, "U! T", False)
    assert_interp(icfp, "U! F", True)
    assert_interp(icfp, "U# S4%34", 15818151)
    assert_interp(icfp, "U$ I4%34", "test")

def test_eval_basic_unary(icfp):
    assert_eval(icfp, "U- I/6", -1337)
    assert_eval(icfp, "U! T", False)
    assert_eval(icfp, "U! F", True)
    assert_eval(icfp, "U# S4%34", 15818151)
    assert_eval(icfp, "U$ I4%34", "test")

def test_nested_unary(icfp):
    assert_interp(icfp, "U- U- I/6", 1337)
    assert_interp(icfp, "U! U! T", True)
    assert_interp(icfp, "U! U! F", False)
    assert_interp(icfp, "U$ U# S4%34", "test")
    assert_interp(icfp, "U# U$ I4%34", 15818151)

def test_eval_nested_unary(icfp):
    assert_eval(icfp, "U- U- I/6", 1337)
    assert_eval(icfp, "U! U! T", True)
    assert_eval(icfp, "U! U! F", False)
    assert_eval(icfp, "U$ U# S4%34", "test")
    assert_eval(icfp, "U# U$ I4%34", 15818151)

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

def test_eval_basic_binop(icfp):
    assert_eval(icfp, "B+ I# I$", 5)
    assert_eval(icfp, "B- I$ I#", 1)
    assert_eval(icfp, "B* I$ I#", 6)
    assert_eval(icfp, "B/ U- I( I#", -3)
    assert_eval(icfp, "B% U- I( I#", -1)
    assert_eval(icfp, "B< I$ I#", False)
    assert_eval(icfp, "B> I$ I#", True)
    assert_eval(icfp, "B= I$ I#", False)
    assert_eval(icfp, "B| T F", True)
    assert_eval(icfp, "B& T F", False)
    assert_eval(icfp, "B. S4% S34", "test")
    assert_eval(icfp, "BT I$ S4%34", "tes")
    assert_eval(icfp, "BD I$ S4%34", "t")

def test_basic_apply(icfp):
    assert_interp(icfp, "B$ L\" v\" B- I( I#", 5)
    assert_interp(icfp, "B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK", "Hello World!")

    # (apply (lambda v0 (+ v0 v0)) (* 3 2))
    assert_interp(icfp, "B$ L\" B+ v\" v\" B* I$ I#", 12)

    # (apply (lambda v2 (apply (lambda v0 (+ v0 v0)) (* 3 2))) v23)
    assert_interp(icfp, "B$ L# B$ L\" B+ v\" v\" B* I$ I# v8", 12)

def test_eval_basic_apply(icfp):
    assert_eval(icfp, "B$ L\" v\" B- I( I#", 5)
    assert_eval(icfp, "B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK", "Hello World!")

    # (apply (lambda v0 (+ v0 v0)) (* 3 2))
    assert_eval(icfp, "B$ L\" B+ v\" v\" B* I$ I#", 12)

    # (apply (lambda v2 (apply (lambda v0 (+ v0 v0)) (* 3 2))) v23)
    assert_eval(icfp, "B$ L# B$ L\" B+ v\" v\" B* I$ I# v8", 12)

def test_conditional(icfp):
    assert_interp(icfp, "? T I$ I#", 3)
    assert_interp(icfp, "? F I$ I#", 2)

def test_eval_conditional(icfp):
    assert_eval(icfp, "? T I$ I#", 3)
    assert_eval(icfp, "? F I$ I#", 2)

def test_lambda_shadowing(icfp):
    # (apply (lambda v0 (* (apply (lambda v0 (+ v0 v0)) v0) v0)) 3)
    # (\x. (apply (\x. (+ x x)) x) x) 3
    assert_interp(icfp, "B$ L\" B* v\" v\" I$", 9)
    assert_interp(icfp, "B$ L\" B* B$ L\" B+ v\" v\" v\" v\" I$", 18)

def test_eval_lambda_shadowing(icfp):
    # (apply (lambda v0 (* (apply (lambda v0 (+ v0 v0)) v0) v0)) 3)
    # (\x. (apply (\x. (+ x x)) x) x) 3
    assert_eval(icfp, "B$ L\" B* v\" v\" I$", 9)
    assert_eval(icfp, "B$ L\" B* B$ L\" B+ v\" v\" v\" v\" I$", 18)

def test_y_combinator(icfp):
    # (apply (lambda v0 (* (apply (lambda v0 (+ v0 v0)) v0) v0)) 3)
    # (\x. (apply (\x. (+ x x)) x) x) 3
    assert_interp(icfp, "B$ L\" B* v\" v\" I$", 9)
    assert_interp(icfp, "B$ L\" B* B$ L\" B+ v\" v\" v\" v\" I$", 18)

def test_eval_y_combinator(icfp):
    # (apply (lambda v0 (* (apply (lambda v0 (+ v0 v0)) v0) v0)) 3)
    # (\x. (apply (\x. (+ x x)) x) x) 3
    assert_eval(icfp, "B$ L\" B* v\" v\" I$", 9)
    assert_eval(icfp, "B$ L\" B* B$ L\" B+ v\" v\" v\" v\" I$", 18)

def test_language_test(icfp):
    input_token = "? B= B$ B$ B$ B$ L$ L$ L$ L# v$ I\" I# I$ I% I$ ? B= B$ L$ v$ I+ I+ ? B= BD I$ S4%34 S4 ? B= BT I$ S4%34 S4%3 ? B= B. S4% S34 S4%34 ? U! B& T F ? B& T T ? U! B| F F ? B| F T ? B< U- I$ U- I# ? B> I$ I# ? B= U- I\" B% U- I$ I# ? B= I\" B% I( I$ ? B= U- I\" B/ U- I$ I# ? B= I# B/ I( I$ ? B= I' B* I# I$ ? B= I$ B+ I\" I# ? B= U$ I4%34 S4%34 ? B= U# S4%34 I4%34 ? U! F ? B= U- I$ B- I# I& ? B= I$ B- I& I# ? B= S4%34 S4%34 ? B= F F ? B= I$ I$ ? T B. B. SM%,&k#(%#+}IEj}3%.$}z3/,6%},!.'5!'%y4%34} U$ B+ I# B* I$> I1~s:U@ Sz}4/}#,!)-}0/).43}&/2})4 S)&})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}k})3}./4}#/22%#4 S5.!29}k})3}./4}#/22%#4 S5.!29}_})3}./4}#/22%#4 S5.!29}a})3}./4}#/22%#4 S5.!29}b})3}./4}#/22%#4 S\").!29}i})3}./4}#/22%#4 S\").!29}h})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}r})3}./4}#/22%#4 S\").!29}p})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}l})3}./4}#/22%#4 S\").!29}N})3}./4}#/22%#4 S\").!29}>})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4"

    assert_interp(icfp, input_token, 'Self-check OK, send `solve language_test 4w3s0m3` to claim points for it')

def test_eval_language_test(icfp):
    input_token = "? B= B$ B$ B$ B$ L$ L$ L$ L# v$ I\" I# I$ I% I$ ? B= B$ L$ v$ I+ I+ ? B= BD I$ S4%34 S4 ? B= BT I$ S4%34 S4%3 ? B= B. S4% S34 S4%34 ? U! B& T F ? B& T T ? U! B| F F ? B| F T ? B< U- I$ U- I# ? B> I$ I# ? B= U- I\" B% U- I$ I# ? B= I\" B% I( I$ ? B= U- I\" B/ U- I$ I# ? B= I# B/ I( I$ ? B= I' B* I# I$ ? B= I$ B+ I\" I# ? B= U$ I4%34 S4%34 ? B= U# S4%34 I4%34 ? U! F ? B= U- I$ B- I# I& ? B= I$ B- I& I# ? B= S4%34 S4%34 ? B= F F ? B= I$ I$ ? T B. B. SM%,&k#(%#+}IEj}3%.$}z3/,6%},!.'5!'%y4%34} U$ B+ I# B* I$> I1~s:U@ Sz}4/}#,!)-}0/).43}&/2})4 S)&})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}q})3}./4}#/22%#4 S\").!29}k})3}./4}#/22%#4 S5.!29}k})3}./4}#/22%#4 S5.!29}_})3}./4}#/22%#4 S5.!29}a})3}./4}#/22%#4 S5.!29}b})3}./4}#/22%#4 S\").!29}i})3}./4}#/22%#4 S\").!29}h})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}m})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}c})3}./4}#/22%#4 S\").!29}r})3}./4}#/22%#4 S\").!29}p})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}{})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}d})3}./4}#/22%#4 S\").!29}l})3}./4}#/22%#4 S\").!29}N})3}./4}#/22%#4 S\").!29}>})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4"

    assert_eval(icfp, input_token, 'Self-check OK, send `solve language_test 4w3s0m3` to claim points for it')

# def test_compile(icfp):
    # assert icfp.compile_from_string("B. S! S\"") == 

#     y_combinator = 'L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v#'
#
#     L$
#
# f"B. SF B$ B$ L\" B$ {y_combinator} 

# L$ L# ? B= v# I" v" B. v" B$ v$ B- v# I" Sl I#,'
