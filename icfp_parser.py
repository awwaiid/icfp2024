class ICFP:
    """
    The ICFP class is a parser for the ICFP programming language. It can encode and decode ICFP tokens.


    Example usage:
        echo 'SB%,,/}Q/2,$_' | python icfp_parser.py --decode

    """

    def __init__(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
        int_chars = ''.join(chr(i) for i in range(33, 127))  # ASCII characters from 33 to 126
        self.char_to_base94 = {char: idx for idx, char in enumerate(chars)}
        self.base94_to_char = {idx: char for idx, char in enumerate(chars)}

        self.int_to_char = {idx: char for idx, char in enumerate(int_chars)}
        self.char_to_int = {char: idx for idx, char in enumerate(int_chars)}

    def encode_boolean(self, value):
        return "T" if value else "F"

    def decode_boolean(self, token):
        return token == "T"

    def encode_integer(self, value):
        base94 = self.to_base94(value)
        return "I" + base94

    def decode_integer(self, token):
        base94 = token[1:]
        return self.from_base94(base94)

    def encode_string(self, value):
        encoded_body = ''.join(chr(self.char_to_base94[char] + 33) for char in value)
        return "S" + encoded_body

    def decode_string(self, token):
        encoded_body = token[1:]
        return ''.join(self.base94_to_char[ord(char) - 33] for char in encoded_body)

    def encode_unary_operator(self, op, operand):
        return f"U{op} {self.encode(operand)}"

    def decode_unary_operator(self, token):
        op = token[1]
        operand_token = token[3:]
        operand = self.decode(operand_token)

        if op == '-':
            return -operand
        elif op == '!':
            return not operand
        elif op == '#':
            return self.from_base94(self.decode_string(operand_token))
        elif op == '$':
            return self.encode_string(self.decode_integer(operand_token))
        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def encode_binary_operator(self, op, left, right):
        return f"B{op} {self.encode(left)} {self.encode(right)}"

    def decode_binary_operator(self, token):
        op = token[1]
        tokens = token[3:].split(' ', 1)
        left = self.decode(tokens[0])
        right = self.decode(tokens[1])
        return f"B{op}", left, right

    def to_base94(self, value):
        if value == 0:
            return "!"
        result = []
        while value > 0:
            result.append(self.int_to_char[value % 94])
            value //= 94
        return ''.join(reversed(result))

    def from_base94(self, base94):
        value = 0
        for char in base94:
            value = value * 94 + self.char_to_int[char]
        return value


    def encode(self, value, op=None):
        if op is not None:
            if isinstance(value, str):
                return self.encode_unary_operator(op, value)
            elif isinstance(value, tuple):
                return self.encode_binary_operator(op, value[0], value[1])
            else:
                raise ValueError("Unsupported type")
        if isinstance(value, bool):
            return self.encode_boolean(value)
        elif isinstance(value, int):
            return self.encode_integer(value)
        elif isinstance(value, str):
            return self.encode_string(value)
        else:
            raise ValueError("Unsupported type")

    def decode(self, token):
        if token.startswith("T") or token.startswith("F"):
            return self.decode_boolean(token)
        elif token.startswith("I"):
            return self.decode_integer(token)
        elif token.startswith("S"):
            return self.decode_string(token)
        elif token.startswith("U"):
            return self.decode_unary_operator(token)
        elif token.startswith("B"):
            return self.decode_binary_operator(token)
        else:
            raise ValueError("Unknown token type")


if __name__ == "__main__":
  #  Handle PIPED input and a --encode or --decode flag
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--encode", action="store_true")
  parser.add_argument("--decode", action="store_true")
  args = parser.parse_args()

  icfp = ICFP()

  if args.encode:
      print(icfp.encode(input()))
  elif args.decode:
      print(icfp.decode(input()))
  else:
      print("Please specify --encode or --decode")
      exit(1)
