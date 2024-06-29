#!/usr/bin/env python

import json
from copy import deepcopy

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


class ICFP:
    """
    The ICFP class is a parser for the ICFP programming language. It can encode and parse ICFP tokens.


    Example usage:
        echo 'SB%,,/}Q/2,$_' | python icfp_parser.py --parse

    """

    def __init__(self):
        self.debug_mode = True

        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
        int_chars = ''.join(chr(i) for i in range(33, 127))  # ASCII characters from 33 to 126
        self.char_to_base94 = {char: idx for idx, char in enumerate(chars)}
        self.base94_to_char = {idx: char for idx, char in enumerate(chars)}

        self.int_to_char = {idx: char for idx, char in enumerate(int_chars)}
        self.char_to_int = {char: int(idx) for idx, char in enumerate(int_chars)}

    def debug(self, msg):
        if self.debug_mode:
            print(msg)

    def encode_boolean(self, ast):
        return "T" if ast["value"] else "F"

    def parse_boolean(self, token, tokens):
        return { "type": "boolean", "value": (token == "T") }, tokens

    def interp_boolean(self, ast, env):
        return ast

    def encode_integer(self, ast):
        base94 = self.to_base94(ast["value"])
        return "I" + base94

    def parse_integer(self, token, tokens):
        base94 = token[1:]
        return { "type": "integer", "value": self.from_base94(base94) }, tokens

    def interp_integer(self, ast, env):
        return ast

    def raw_encode_string(self, value):
        encoded_body = ''.join(chr(self.char_to_base94[char] + 33) for char in value)
        return "S" + encoded_body

    def encode_string(self, ast):
        value = ast["value"]
        return self.raw_encode_string(value)

    def raw_parse_string(self, token):
        encoded_body = token[1:]
        return ''.join(self.base94_to_char[ord(char) - 33] for char in encoded_body)

    def parse_string(self, token, tokens):
        encoded_body = token[1:]
        return { "type": "string", "value": ''.join(self.base94_to_char[ord(char) - 33] for char in encoded_body) }, tokens

    def interp_string(self, ast, env):
        return ast

    def encode_unary_operator(self, ast):
        op = ast["op"]
        operand = ast["left"]
        return f"U{op} {self.encode(operand)}"

    def parse_unary_operator(self, op, tokens):
        op = op[1:]
        operand, tokens = self.parse(tokens)
        return { "type": "unary", "op": op, "left": operand }, tokens

    def interp_unary_operator(self, ast, env):
        op = ast["op"]
        operand = self.interp(ast["left"], env)
        operand_value = operand["value"]

        if op == '-':
            return { "type": "integer", "value": -operand_value }
        elif op == '!':
            return { "type": "boolean", "value": not operand_value }
        elif op == '#':
            operand = self.encode_string(operand)
            operand = operand[1:]
            return { "type": "integer", "value": self.from_base94(operand) }
        elif op == '$':
            operand = self.encode_integer(operand)
            operand = operand[1:]
            operand = "S" + operand
            return { "type": "string", "value": self.raw_parse_string(operand) }
        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def encode_binary_operator(self, ast):
        op = ast["op"]
        left = ast["left"]
        right = ast["right"]
        return f"B{op} {self.encode(left)} {self.encode(right)}"

    def parse_binary_operator(self, token, tokens):
        op = token[1:]
        left, tokens = self.parse(tokens)
        right, tokens = self.parse(tokens)
        return { "type": "binop", "op": op, "left": left, "right": right }, tokens

    def replace_var(self, ast, target_var, new_value):
        # print(f"replace_var. Lambda body: {json.dumps(ast)}")
        # print(f"replace_var. Target var: {target_var}")
        # print(f"replace_var. New value: {json.dumps(new_value)}")
        if ast["type"] == "var":
            if ast["var"] == target_var:
                return new_value
            else:
                return ast
        elif ast["type"] == "binop":
            left = self.replace_var(ast["left"], target_var, new_value)
            right = self.replace_var(ast["right"], target_var, new_value)
            return { "type": "binop", "op": ast["op"], "left": left, "right": right }
        elif ast["type"] == "unary":
            left = self.replace_var(ast["left"], target_var, new_value)
            return { "type": "unary", "op": ast["op"], "left": left }
        elif ast["type"] == "if":
            condition = self.replace_var(ast["condition"], target_var, new_value)
            true_branch = self.replace_var(ast["true"], target_var, new_value)
            false_branch = self.replace_var(ast["false"], target_var, new_value)
            return { "type": "if", "condition": condition, "true": true_branch, "false": false_branch }
        elif ast["type"] == "lambda":
            if ast["var"] == target_var:
                # This lambda overrides the target_var, so don't go deeper
                return ast
            else:
                return { "type": "lambda", "var": ast["var"], "body": self.replace_var(ast["body"], target_var, new_value) }
        else:
            # The rest are constants
            return ast



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
    #
    # Did you know that the binary call-by-name application operator `$` has
    # two siblings? The binary operator `~` (lazy application) is a
    # call-by-need variant on the `$` operator, and the binary operator `!`
    # (strict application) is the call-by-value variant. Smart usage of these
    # can help you save many beta reductions!
    def interp_binary_operator(self, ast, env):
        op = ast["op"]

        if op == "$":
            # Left is a lambda, right is a value
            lambda_ast = self.interp(ast["left"], env)
            if lambda_ast["type"] != "lambda":
                raise ValueError(f"Expected lambda, got {lambda_ast}")
            lambda_var = lambda_ast["var"]
            lambda_body = lambda_ast["body"]
            arg = ast["right"]

            # Traverse the lambda_body and replace all vars that match the lambda var with the argument
            result = self.replace_var(lambda_body, lambda_var, arg)

            # env = deepcopy(env)
            # env[lambda_var] = arg
            result = self.interp(result, env)
            return result

        left = self.interp(ast["left"], env)
        right = self.interp(ast["right"], env)
        # print(f"binary op: {op}")
        # print(f"left: {json.dumps(left)}")
        # print(f"right: {json.dumps(right)}")
        left_value = left["value"]
        right_value = right["value"]

        if op == "+":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "integer", "value": left_value + right_value }
        elif op == "-":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "integer", "value": left_value - right_value }
        elif op == "*":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "integer", "value": left_value * right_value }
        elif op == "/":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            # return { "type": "integer", "value": left_value // right_value }
            return { "type": "integer", "value": integer_divide_toward_zero(left_value, right_value) }
        elif op == "%":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "integer", "value": remainder(left_value, right_value) }
        elif op == "<":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "boolean", "value": left_value < right_value }
        elif op == ">":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return { "type": "boolean", "value": left_value > right_value }
        elif op == "=":
            if left["type"] == "integer" and right["type"] == "integer":
                return { "type": "boolean", "value": left_value == right_value }
            if left["type"] == "string" and right["type"] == "string":
                return { "type": "boolean", "value": left_value == right_value }
            if left["type"] == "boolean" and right["type"] == "boolean":
                return { "type": "boolean", "value": left_value == right_value }
            raise ValueError(f"Expected integers or strings or booleans, got {left} and {right}")
        elif op == "|":
            if left["type"] != "boolean" or right["type"] != "boolean":
                raise ValueError(f"Expected boolean, got {left} and {right}")
            return { "type": "boolean", "value": left_value or right_value }
        elif op == "&":
            if left["type"] != "boolean" or right["type"] != "boolean":
                raise ValueError(f"Expected boolean, got {left} and {right}")
            return { "type": "boolean", "value": left_value and right_value }
        elif op == ".":
            if left["type"] != "string" or right["type"] != "string":
                raise ValueError(f"Expected string, got {left} and {right}")
            return { "type": "string", "value": left_value + right_value }
        elif op == "T":
            if left["type"] != "integer":
                raise ValueError(f"Expected integer, got {left}")
            if right["type"] != "string":
                raise ValueError(f"Expected integer, got {right}")
            return { "type": "string", "value": right_value[:left_value] }
        elif op == "D":
            if left["type"] != "integer":
                raise ValueError(f"Expected integer, got {left}")
            if right["type"] != "string":
                raise ValueError(f"Expected integer, got {right}")
            return { "type": "string", "value": right_value[left_value:] }
        else:
            raise ValueError(f"Unknown binary operator: {op}")

    def parse_lambda(self, token, tokens):
        param = token[1:]
        var_num = self.from_base94(param)
        body, tokens = self.parse(tokens)
        return { "type": "lambda", "var": var_num, "body": body }, tokens

    def interp_lambda(self, ast, env):
        return ast

    def encode_lambda(self, ast):
        return f"L{self.to_base94(ast['var'])} {self.encode(ast['body'])}"

    def parse_variable(self, token, tokens):
        body = token[1:]
        var_num = self.from_base94(body)
        return { "type": "var", "var": var_num }, tokens

    def interp_variable(self, ast, env):
        # return env[ast["var"]]
        return ast

    def encode_variable(self, ast):
        return f"v{self.to_base94(ast['var'])}"

    def parse_if(self, token, tokens):
        condition, tokens = self.parse(tokens)
        true_branch, tokens = self.parse(tokens)
        false_branch, tokens = self.parse(tokens)
        return { "type": "if", "condition": condition, "true": true_branch, "false": false_branch }, tokens

    def encode_if(self, ast):
        return f"? {self.encode(ast['condition'])} {self.encode(ast['true'])} {self.encode(ast['false'])}"

    def interp_if(self, ast, env):
        condition = self.interp(ast["condition"], env)
        if condition["value"]:
            return self.interp(ast["true"], env)
        else:
            return self.interp(ast["false"], env)

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

    def encode(self, ast):
        if ast["type"] == "string":
            return self.encode_string(ast)
        elif ast["type"] == "integer":
            return self.encode_integer(ast)
        elif ast["type"] == "boolean":
            return self.encode_boolean(ast)
        elif ast["type"] == "unary":
            return self.encode_unary_operator(ast)
        elif ast["type"] == "binop":
            return self.encode_binary_operator(ast)
        elif ast["type"] == "lambda":
            return self.encode_lambda(ast)
        elif ast["type"] == "var":
            return self.encode_variable(ast)
        elif ast["type"] == "if":
            return self.encode_if(ast)
        else:
            raise ValueError(f"Unknown type: {ast['type']}")

    def parse(self, tokens):
        if len(tokens) == 0:
            return [], tokens
        token = tokens.pop(0)
        if token.startswith("T") or token.startswith("F"):
            return self.parse_boolean(token, tokens)
        elif token.startswith("I"):
            return self.parse_integer(token, tokens)
        elif token.startswith("S"):
            return self.parse_string(token, tokens)
        elif token.startswith("U"):
            return self.parse_unary_operator(token, tokens)
        elif token.startswith("B"):
            return self.parse_binary_operator(token, tokens)
        elif token.startswith("L"):
            return self.parse_lambda(token, tokens)
        elif token.startswith("v"):
            return self.parse_variable(token, tokens)
        elif token.startswith("?"):
            return self.parse_if(token, tokens)
        else:
            raise ValueError(f"Unknown token type: {token}")

    def interp(self, ast, env = {}):
        # env = deepcopy(env)
        # env["depth"] = env.get("depth", 0) + 1
        # self.debug(f"{env['depth'] * 2 * ' '}env: {json.dumps(env)}")
        # self.debug(f"{env['depth'] * 2 * ' '}interp: {json.dumps(ast)}")

        result = None
        if ast["type"] == "boolean":
            result = self.interp_boolean(ast, env)
        elif ast["type"] == "integer":
            result = self.interp_integer(ast, env)
        elif ast["type"] == "string":
            result = self.interp_string(ast, env)
        elif ast["type"] == "unary":
            result = self.interp_unary_operator(ast, env)
        elif ast["type"] == "binop":
            result = self.interp_binary_operator(ast, env)
        elif ast["type"] == "lambda":
            result = self.interp_lambda(ast, env)
        elif ast["type"] == "var":
            result = self.interp_variable(ast, env)
        elif ast["type"] == "if":
            result = self.interp_if(ast, env)
        else:
            raise ValueError(f"Unknown type: {ast['type']}")

        while result["type"] != "string" and result["type"] != "integer" and result["type"] != "boolean" and result["type"] != "lambda" and result["type"] != "var":
            result = self.interp(result, env)

        # self.debug(f"{env['depth'] * 2 * ' '}result: {json.dumps(result)}")
        return result

    def interp_from_string(self, input):
        ast, _ = self.parse(input.split(' '))
        # print("Parse: ", json.dumps(ast))
        return self.interp(ast)

if __name__ == "__main__":
  #  Handle PIPED input and a --encode or --parse flag
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument("--encode", action="store_true")
  parser.add_argument("--parse", action="store_true")
  parser.add_argument("--interp", action="store_true")
  parser.add_argument("--debug", action="store_true")
  args = parser.parse_args()

  icfp = ICFP()

  if args.debug:
      icfp.debug_mode = True

  if args.interp:
      result = icfp.interp_from_string(input())
      if args.encode:
          print(icfp.encode(result))
      else:
          print(result)
  elif args.encode:
      print(icfp.raw_encode_string(input()))
  elif args.parse:
      ast, _ = icfp.parse(input().split(' '))
      print(json.dumps(ast))
      # print(icfp.encode(result))
  else:
      print("Please specify --encode or --parse")
      exit(1)
