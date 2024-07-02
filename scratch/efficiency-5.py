def Y(f):
    return (lambda x: f(lambda y: x(x)(y)))(lambda x: f(lambda y: x(x)(y)))

def main_function():
    def church_numeral(n):
        return lambda f: lambda x: f(n(f)(x))

    def is_prime(n):
        if n <= 1:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def collatz_step(n):
        return n // 2 if n % 2 == 0 else 3 * n + 1

    def find_special_number(start):
        def inner(n):
            if n > 1000000 and is_prime(n) and is_prime(n + 1):
                return n
            return inner(collatz_step(n))
        return Y(inner)(start)

    # The main logic, corresponding to the root of the JSON structure
    result = (lambda f: lambda x: f(f)(x))(
        lambda self: lambda n:
            find_special_number(church_numeral(2)(lambda x: x + 1)(0))
    )(5)  # The '5' here is arbitrary, as it's not used in the main logic

    return result

# Run the main function
print(main_function())
