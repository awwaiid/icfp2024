#!/bin/env python


import sys
import os
from subprocess import Popen, PIPE, STDOUT

        # p = Popen(['myapp'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        # stdout_data = p.communicate(input='data_to_write')[0]
def main():
    while True:
        english = input(">>> ")
        # print(f"english: {english}")
        # Send this to the stdin of the encoder
        p = Popen(['python', 'icfp_parser.py', '--encode'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        encoded, error = p.communicate(input=english)
        if error:
            print(f"Error: {error}")
        # print(f"encoded: {encoded}")
        # Send this to the stdin of the server
        p = Popen(['curl', '--silent', '-H', 'Authorization: Bearer 9272ed8c-a55f-4dbd-b50f-2970446a6c09', '-X', 'POST', '-d', '@-', 'https://boundvariable.space/communicate'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        response, error = p.communicate(input=encoded)
        if error:
            print(f"Error: {error}")
        # print(f"Response: {response}")
        # Send this to the stdin of the decoder
        p = Popen(['python', 'icfp_parser.py', '--decode'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
        decoded, error = p.communicate(input=response)
        if error:
            print(f"Error: {error}")
        print(f"{decoded}")


main()
