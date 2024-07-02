
import sys
sys.set_int_max_str_digits(0)
sys.setrecursionlimit(100000)

def remainder(n, d):
    return (-1 if n < 0 else 1) * (abs(n) % abs(d))

def integer_divide_toward_zero(a, b):
    # Perform regular integer division
    result = a // b
    # Adjust the result if necessary
    if (a < 0) != (b < 0) and a % b != 0:
        result += 1
    return result


# print(("L" + ((lambda v1: (lambda v1: (lambda v2: (v1)((v2)(v2)))(lambda v2: (v1)((v2)(v2))))(lambda v3: lambda v2: (v1 if (v2 == 1) else (v1 + (v3)((v2 - 1))))))("."))(199)))



print(

    (lambda: "L" +
        (lambda: "a" + "b")()
    )()
)


