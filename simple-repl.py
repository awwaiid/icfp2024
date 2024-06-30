#!/usr/bin/env python


import sys
import os
from client import Client

client = Client()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simple REPL for the encoder")
    parser.add_argument(
        "--command", help="Execute a single command and exit", type=str, required=False
    )
    parser.add_argument("--save", action="store_true", help="Save the output to a file")
    args = parser.parse_args()
    if args.command:
        response, result = client.call(args.command)
        print(result)
        sys.exit()
    while True:
        english = input(">>> ")
        if english == "```":
            multiline = []
            while True:
                line = input("... ")
                if line == "```":
                    break
                multiline.append(line)
            english = "\n".join(multiline)
        # print(f"english: {english}")
        # Send this to the stdin of the encoder
        try:
            response, result = client.call(english)
            os.makedirs("courses", exist_ok=True)
            # write the response to a file
            if args.save:
                normalize_prompt = english.replace(" ", "_")
                with open(f"courses/{normalize_prompt}.txt", "w") as f:
                    f.write(result)
            # normalize_prompt = english.replace(" ", "_")

            # with open(f"courses/{normalize_prompt}.txt", "w") as f:
            #     f.write(result)
            print(result)
        except Exception as e:
            response = str(e)
            error = True

            print(f"Error: {error}")
            print(f"Response: {response}")

            # make a directory to store the response
            os.makedirs("responses", exist_ok=True)
            # write the response to a file
            # normalize_prompt = english.replace(" ", "_")
            # with open(f"responses/{normalize_prompt}.txt", "w") as f:
            #     f.write(response)


main()
