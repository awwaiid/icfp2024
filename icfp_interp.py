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
        int_chars = "".join(
            chr(i) for i in range(33, 127)
        )  # ASCII characters from 33 to 126
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
        return {"type": "boolean", "value": (token == "T")}, tokens

    def interp_boolean(self, ast, env):
        return ast

    def encode_integer(self, ast):
        base94 = self.to_base94(ast["value"])
        return "I" + base94

    def raw_encode_integer(self, val):
        base94 = self.to_base94(val)
        return "I" + base94

    def parse_integer(self, token, tokens):
        base94 = token[1:]
        return {"type": "integer", "value": self.from_base94(base94)}, tokens

    def interp_integer(self, ast, env):
        return ast

    def raw_encode_string(self, value):
        encoded_body = "".join(chr(self.char_to_base94[char] + 33) for char in value)
        return "S" + encoded_body

    def encode_string(self, ast):
        value = ast["value"]
        return self.raw_encode_string(value)

    def raw_parse_string(self, token):
        encoded_body = token[1:]
        return "".join(self.base94_to_char[ord(char) - 33] for char in encoded_body)

    def parse_string(self, token, tokens):
        encoded_body = token[1:]
        return {
            "type": "string",
            "value": "".join(
                self.base94_to_char[ord(char) - 33] for char in encoded_body
            ),
        }, tokens

    def interp_string(self, ast, env):
        return ast

    def encode_unary_operator(self, ast):
        op = ast["op"]
        operand = ast["left"]
        return f"U{op} {self.encode(operand)}"

    def parse_unary_operator(self, op, tokens):
        op = op[1:]
        operand, tokens = self.parse(tokens)
        return {"type": "unary", "op": op, "left": operand}, tokens

    def interp_unary_operator(self, ast, env):
        op = ast["op"]
        operand = self.interp(ast["left"], env)
        operand_value = operand["value"]

        if op == "-":
            return {"type": "integer", "value": -operand_value}
        elif op == "!":
            return {"type": "boolean", "value": not operand_value}
        elif op == "#":
            operand = self.encode_string(operand)
            operand = operand[1:]
            return {"type": "integer", "value": self.from_base94(operand)}
        elif op == "$":
            operand = self.encode_integer(operand)
            operand = operand[1:]
            operand = "S" + operand
            return {"type": "string", "value": self.raw_parse_string(operand)}
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
        return {"type": "binop", "op": op, "left": left, "right": right}, tokens

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
            return {"type": "binop", "op": ast["op"], "left": left, "right": right}
        elif ast["type"] == "unary":
            left = self.replace_var(ast["left"], target_var, new_value)
            return {"type": "unary", "op": ast["op"], "left": left}
        elif ast["type"] == "if":
            condition = self.replace_var(ast["condition"], target_var, new_value)
            true_branch = self.replace_var(ast["true"], target_var, new_value)
            false_branch = self.replace_var(ast["false"], target_var, new_value)
            return {
                "type": "if",
                "condition": condition,
                "true": true_branch,
                "false": false_branch,
            }
        elif ast["type"] == "lambda":
            if ast["var"] == target_var:
                # This lambda overrides the target_var, so don't go deeper
                return ast
            else:
                return {
                    "type": "lambda",
                    "var": ast["var"],
                    "body": self.replace_var(ast["body"], target_var, new_value),
                }
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
            return {"type": "integer", "value": left_value + right_value}
        elif op == "-":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return {"type": "integer", "value": left_value - right_value}
        elif op == "*":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return {"type": "integer", "value": left_value * right_value}
        elif op == "/":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            # return { "type": "integer", "value": left_value // right_value }
            return {
                "type": "integer",
                "value": integer_divide_toward_zero(left_value, right_value),
            }
        elif op == "%":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return {"type": "integer", "value": remainder(left_value, right_value)}
        elif op == "<":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return {"type": "boolean", "value": left_value < right_value}
        elif op == ">":
            if left["type"] != "integer" or right["type"] != "integer":
                raise ValueError(f"Expected integer, got {left} and {right}")
            return {"type": "boolean", "value": left_value > right_value}
        elif op == "=":
            if left["type"] == "integer" and right["type"] == "integer":
                return {"type": "boolean", "value": left_value == right_value}
            if left["type"] == "string" and right["type"] == "string":
                return {"type": "boolean", "value": left_value == right_value}
            if left["type"] == "boolean" and right["type"] == "boolean":
                return {"type": "boolean", "value": left_value == right_value}
            raise ValueError(
                f"Expected integers or strings or booleans, got {left} and {right}"
            )
        elif op == "|":
            if left["type"] != "boolean" or right["type"] != "boolean":
                raise ValueError(f"Expected boolean, got {left} and {right}")
            return {"type": "boolean", "value": left_value or right_value}
        elif op == "&":
            if left["type"] != "boolean" or right["type"] != "boolean":
                raise ValueError(f"Expected boolean, got {left} and {right}")
            return {"type": "boolean", "value": left_value and right_value}
        elif op == ".":
            if left["type"] != "string" or right["type"] != "string":
                raise ValueError(f"Expected string, got {left} and {right}")
            return {"type": "string", "value": left_value + right_value}
        elif op == "T":
            if left["type"] != "integer":
                raise ValueError(f"Expected integer, got {left}")
            if right["type"] != "string":
                raise ValueError(f"Expected integer, got {right}")
            return {"type": "string", "value": right_value[:left_value]}
        elif op == "D":
            if left["type"] != "integer":
                raise ValueError(f"Expected integer, got {left}")
            if right["type"] != "string":
                raise ValueError(f"Expected integer, got {right}")
            return {"type": "string", "value": right_value[left_value:]}
        else:
            raise ValueError(f"Unknown binary operator: {op}")

    def parse_lambda(self, token, tokens):
        param = token[1:]
        var_num = self.from_base94(param)
        body, tokens = self.parse(tokens)
        return {"type": "lambda", "var": var_num, "body": body}, tokens

    def interp_lambda(self, ast, env):
        return ast

    def encode_lambda(self, ast):
        return f"L{self.to_base94(ast['var'])} {self.encode(ast['body'])}"

    def parse_variable(self, token, tokens):
        body = token[1:]
        var_num = self.from_base94(body)
        return {"type": "var", "var": var_num}, tokens

    def interp_variable(self, ast, env):
        # return env[ast["var"]]
        return ast

    def encode_variable(self, ast):
        return f"v{self.to_base94(ast['var'])}"

    def parse_if(self, token, tokens):
        condition, tokens = self.parse(tokens)
        true_branch, tokens = self.parse(tokens)
        false_branch, tokens = self.parse(tokens)
        return {
            "type": "if",
            "condition": condition,
            "true": true_branch,
            "false": false_branch,
        }, tokens

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
        return "".join(reversed(result))

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

    def interp(self, ast, env={}):
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

        while (
            result["type"] != "string"
            and result["type"] != "integer"
            and result["type"] != "boolean"
            and result["type"] != "lambda"
            and result["type"] != "var"
        ):
            print(f"result: {json.dumps(result)}")
            result = self.interp(result, env)

        # self.debug(f"{env['depth'] * 2 * ' '}result: {json.dumps(result)}")
        return result

    def interp_from_string(self, input):
        ast, _ = self.parse(input.split(" "))
        # print("Parse: ", json.dumps(ast))
        return self.interp(ast)

    # Translate from the ICFP language to the Python language
    def compile(self, ast):
        source = ""
        if ast["type"] == "string":
            source = '(lambda: "' + ast["value"] + '")'
        elif ast["type"] == "integer":
            source = "(lambda: " + str(ast["value"]) + ")"
        elif ast["type"] == "boolean":
            source = "lambda: True" if ast["value"] else "lambda: False"
        elif ast["type"] == "unary":
            source = self.compile_unary(ast)
        elif ast["type"] == "binop":
            source = self.compile_binop(ast)
        elif ast["type"] == "lambda":
            source = self.compile_lambda(ast)
        elif ast["type"] == "var":
            source = self.compile_var(ast)
        elif ast["type"] == "if":
            source = self.compile_if(ast)
        else:
            raise ValueError(f"Unknown type: {ast['type']}")
        return f"{source}"

    def compile_unary(self, ast):
        op = ast["op"]
        operand = self.compile(ast["left"])
        if op == "-":
            return f"lambda: -{operand}"
        elif op == "!":
            return f"lambda: not {operand}"
        elif op == "#":
            return f"lambda: from_base94({operand})"
        elif op == "$":
            return f"lambda: encode_string({operand})"
        else:
            raise ValueError(f"Unknown unary operator: {op}")

    def compile_binop(self, ast):
        op = ast["op"]
        left = self.compile(ast["left"])
        right = self.compile(ast["right"])
        if op == "+":
            return f"(lambda: {left}() + {right}())"
        elif op == "-":
            return f"(lambda: {left}() - {right}())"
        elif op == "*":
            return f"(lambda: {left}() * {right}())"
        elif op == "/":
            return f"(lambda: integer_divide_toward_zero({left}(), {right}())"
        elif op == "%":
            return f"remainder({left}, {right})"
        elif op == "<":
            return f"({left} < {right})"
        elif op == ">":
            return f"({left} > {right})"
        elif op == "=":
            return f"({left} == {right})"
        elif op == "|":
            return f"({left} or {right})"
        elif op == "&":
            return f"({left} and {right})"
        elif op == ".":
            return f"(lambda: {left}() + {right}())"
        elif op == "T":
            return f"{right}[:{left}]"
        elif op == "D":
            return f"{right}[{left}:]"
        elif op == "$":
            return f"(lambda: ({left})({right}))"
        else:
            raise ValueError(f"Unknown binary operator: {op}")

    def compile_lambda(self, ast):
        var = ast["var"]
        body = self.compile(ast["body"])
        return f"lambda v{var}: {body}"

    def compile_var(self, ast):
        return f"v{ast['var']}"

    def compile_if(self, ast):
        condition = self.compile(ast["condition"])
        true_branch = self.compile(ast["true"])
        false_branch = self.compile(ast["false"])
        return f"(lambda: ({true_branch}() if {condition}() else {false_branch}()))"

    def compile_from_string(self, input):
        ast, _ = self.parse(input.split(" "))
        return self.compile(ast) + "()"

    def compile_eval(self, input):
        proggie = self.compile_from_string(input)
        result = eval(proggie)
        return result


if __name__ == "__main__":
    #  Handle PIPED input and a --encode or --parse flag
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--encode", action="store_true")
    parser.add_argument("--parse", action="store_true")
    parser.add_argument("--interp", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--eval", action="store_true")
    parser.add_argument("--graph", action="store_true")
    args = parser.parse_args()

    icfp = ICFP()

    if args.debug:
        icfp.debug_mode = True

    if args.interp:
        result = icfp.interp_from_string(input())
        if args.encode:
            print(icfp.encode(result))
        else:
            print(result["value"])
    elif args.compile:
        result = icfp.compile_from_string(input())
        print(result)
    elif args.eval:
        result = icfp.compile_eval(input())
        print(result)
    elif args.encode:
        print(icfp.raw_encode_string(input()))
    elif args.parse:
        ast, _ = icfp.parse(input().split(" "))
        print(json.dumps(ast))

    elif args.graph:
        from graphviz import Digraph

        # Parse the input
        ast, _ = icfp.parse(input().split(" "))
        dot = Digraph()

        def add_node(node):
            node_id = str(id(node))  # Unique identifier for the node

            if node["type"] == "string":
                dot.node(node_id, f'String: "{node["value"]}"')
            elif node["type"] == "integer":
                dot.node(node_id, f'Integer: {node["value"]}')
            elif node["type"] == "boolean":
                dot.node(node_id, f'Boolean: {node["value"]}')
            elif node["type"] == "unary":
                dot.node(node_id, f'Unary: {node["op"]}')
                add_node(node["left"])
                dot.edge(node_id, str(id(node["left"])))
            elif node["type"] == "binop":
                dot.node(node_id, f'Binary: {node["op"]}')
                add_node(node["left"])
                add_node(node["right"])
                dot.edge(node_id, str(id(node["left"])))
                dot.edge(node_id, str(id(node["right"])))
            elif node["type"] == "lambda":
                dot.node(node_id, f'Lambda: {node["var"]}')
                add_node(node["body"])
                dot.edge(node_id, str(id(node["body"])))
            elif node["type"] == "var":
                dot.node(node_id, f'Var: {node["var"]}')
            elif node["type"] == "if":
                dot.node(node_id, f"If")
                add_node(node["condition"])
                add_node(node["true"])
                add_node(node["false"])
                dot.edge(node_id, str(id(node["condition"])))
                dot.edge(node_id, str(id(node["true"])))
                dot.edge(node_id, str(id(node["false"])))

        # Add the root node to the graph
        add_node(ast)

        # Output the dot source
        print(dot.source)
        exit(0)
    else:
        print("Please specify action")
        exit(1)
