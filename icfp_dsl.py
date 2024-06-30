import json
from icfp_interp import ICFP
icfp = ICFP()

def c(value):
    if type(value) == int:
        return { "type": "integer", "value": value }
    elif type(value) == str:
        return { "type": "string", "value": value }
    elif type(value) == bool:
        return { "type": "boolean", "value": value }
    else:
        raise ValueError("Unsupported type")

def plus(a, b):
    return { "type": "binop", "op": "+", "left": a, "right": b }

def minus(a, b):
    return { "type": "binop", "op": "-", "left": a, "right": b }

def times(a, b):
    return { "type": "binop", "op": "*", "left": a, "right": b }

def div(a, b):
    return { "type": "binop", "op": "/", "left": a, "right": b }

def mod(a, b):
    return { "type": "binop", "op": "%", "left": a, "right": b }

def lt(a, b):
    return { "type": "binop", "op": "<", "left": a, "right": b }

def gt(a, b):
    return { "type": "binop", "op": ">", "left": a, "right": b }

def eq(a, b):
    return { "type": "binop", "op": "=", "left": a, "right": b }

def or_(a, b):
    return { "type": "binop", "op": "|", "left": a, "right": b }

def and_(a, b):
    return { "type": "binop", "op": "&", "left": a, "right": b }

def concat(a, b):
    return { "type": "binop", "op": ".", "left": a, "right": b }

def take(a, b):
    return { "type": "binop", "op": "T", "left": a, "right": b }

def drop(a, b):
    return { "type": "binop", "op": "D", "left": a, "right": b }

def apply(a, b):
    return { "type": "binop", "op": "$", "left": a, "right": b }

def lambda_(a, b):
    return { "type": "lambda", "var": a, "body": b }

def if_(a, b, c):
    return { "type": "if", "cond": a, "then": b, "else": c }

def var(n):
    return { "type": "var", "var": n }


# RDLLLUUURRRRRDLULLLDLLDRURURRRRDRDRDLLDDLURRLLDLLLLLULDULULURULRURURURRRRRRRRDRDRDDDDLDRDLDRUUUUUUUUUULDLDLRDRDRDDDLDLDLDRUURURUUULULULULLLLLLLDLDLDDDRDRDRRRRRURUUDDLDLLLLLULULUUURURURRRRRRRRUDDDRDRDDDLDLDLDLLLLLLLLLLULDLUURULUUUUURDUURULLDRRURDLDLDLDDDDRDRDRLULULUUUURURURUR

def str_double(s):
    return apply(lambda_(1, concat(var(1), var(1))), s)

def str_trip(s):
    return apply(lambda_(1, concat(var(1), concat(var(1), var(1)))), s)

def str_quad(s):
    return apply(lambda_(1, concat(concat(var(1), var(1)), concat(var(1), var(1)))), s)

def y_comb(f):
    return apply(lambda_(1, apply(f, apply(var(1), var(1)))), lambda_(1, apply(f, apply(var(1), var(1)))))

def repeat_letter(letter, n):
    return apply(apply(y_comb(lambda_(1, lambda_(2, concat(var(2), var(1))))), c(letter)), c(n))

def echo(v):
    return concat(c("echo "), v)

print(icfp.encode(echo(repeat_letter("L", 3))))

# print(json.dumps(str_double(c("LLLLLLLLLLLLLL"))))
#  print(icfp.encode(str_double(c("LLLLLLL"))))

# print(icfp.encode(c("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")))
#
# print(icfp.encode(str_double(c("LLLLLLLLLLLLLLLL"))))
# print(icfp.interp_from_string(icfp.encode(str_double(c("LLLLLLLLLLLLLLLL"))))["value"])
#
# print(icfp.encode(str_double(str_double(c("LLLLLLLLLLL")))))
# print(icfp.interp_from_string(icfp.encode(str_double(str_double(c("LLLLLLLLLLL")))))["value"])
#
# print(icfp.encode(str_trip(c("LLLLLLLLLL"))))
# print(icfp.interp_from_string(icfp.encode(str_trip(c("LLLLLLLLLL"))))["value"])
#
# print(icfp.encode(str_quad(c("LLLLLL"))))
# print(icfp.interp_from_string(icfp.encode(str_quad(c("LLLLLL"))))["value"])
