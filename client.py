import requests

from icfp_interp import ICFP


class Client:
    url = "https://boundvariable.space/communicate"
    headers = {"Authorization": "Bearer 9272ed8c-a55f-4dbd-b50f-2970446a6c09"}

    def __init__(self):
        self.icfp = ICFP()

    def call(self, prompt):
        if prompt == "":
            return None, ""
        if prompt[0] == "`":
            encoded_prompt = prompt[1:]
        else:
            encoded_prompt = self.attempt_pack(prompt)
        print(f"encoded prompt: {encoded_prompt}")
        response = requests.post(self.url, headers=self.headers, data=encoded_prompt)
        print(f"raw response: {response.text}")
        # result = self.icfp.interp_from_string(response.text)["value"]
        result = self.icfp.eval_from_string(response.text)

        return response, result

    def attempt_pack(self, prompt):
        # call the pack method, and if the output of pack is shorter than stanard encode use the packed version
        encoded_prompt = self.icfp.raw_encode_string(prompt)

        packed_prompt = self.pack(prompt)

        if len(packed_prompt) < len(encoded_prompt):
            print("SENDING PACKED")
            return packed_prompt
        else:
            return encoded_prompt

    def pack(self, prompt):
        # pack the prompt
        # prompt = "hello"
        print("Prompt: ", prompt)
        # Determine a list of unique characters mantaining the order of appearance
        unique_chars = []
        for char in prompt:
            if char not in unique_chars:
                unique_chars.append(char)
        n_of_chars = len(unique_chars)
        lookup_map = "".join(unique_chars)
        encoded_map = self.icfp.raw_encode_string(lookup_map)

        # Build a dict of unique characters to their index in the encoded_map
        lookup_dict = {}
        for i, char in enumerate(unique_chars):
            lookup_dict[char] = i

        # Reverse the prompt
        packed_output = 0
        for char in prompt:
            # Find the index of the character in the lookup_dict
            index = lookup_dict[char]

            # For each iteration, shift the packed_output by n_of_chars bits to the left
            # and add the index of the character to the packed_output
            # This is equivalent to multiplying the packed_output by n_of_chars and adding the index

            packed_output = packed_output * n_of_chars + index

        encoded_packed_output = self.icfp.raw_encode_integer((packed_output))

        encoded_n_of_chars = self.icfp.raw_encode_integer(n_of_chars)

        encoded_first_char = self.icfp.raw_encode_string(unique_chars[0])

        template = f'B$ B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L" L# ? B= v# I! {encoded_first_char} B. B$ v" B/ v# {encoded_n_of_chars} BT I" BD B% v# {encoded_n_of_chars} {encoded_map} {encoded_packed_output}'
        print("Template: ", template)

        # print(self.icfp.interp_from_string(template))
        return template
