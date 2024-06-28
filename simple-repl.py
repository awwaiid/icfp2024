#!/usr/bin/env python


import sys
import os
from subprocess import Popen, PIPE, STDOUT
from client import Client

client = Client()


# p = Popen(['myapp'], stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
# stdout_data = p.communicate(input='data_to_write')[0]
def main():
    while True:
        english = input(">>> ")
        # print(f"english: {english}")
        # Send this to the stdin of the encoder
        try:
            response, decoded = client.call(english)
            os.makedirs("courses", exist_ok=True)
            # write the response to a file
            normalize_prompt = english.replace(" ", "_")

            with open(f"courses/{normalize_prompt}.txt", "w") as f:
                f.write(decoded)
            print(f"{decoded}")
        except Exception as e:
            response = str(e)
            error = True

            print(f"Error: {error}")
            print(f"Response: {response}")

            # make a directory to store the response
            os.makedirs("responses", exist_ok=True)
            # write the response to a file
            normalize_prompt = english.replace(" ", "_")
            with open(f"responses/{normalize_prompt}.txt", "w") as f:
                f.write(response)


main()
