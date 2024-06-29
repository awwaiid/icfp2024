import requests

from icfp_interp import ICFP


class Client:
    url = "https://boundvariable.space/communicate"
    headers = {"Authorization": "Bearer 9272ed8c-a55f-4dbd-b50f-2970446a6c09"}

    def call(self, prompt):
        icfp = ICFP()
        if prompt[0] == "`":
            encoded_prompt = prompt[1:]
        else:
            encoded_prompt = icfp.raw_encode_string(prompt)
        response = requests.post(self.url, headers=self.headers, data=encoded_prompt)
        # print(f"raw response: {response.text}")
        result = icfp.interp_from_string(response.text)

        return response, result["value"]
