import requests

from icfp_parser import ICFP


class Client:
    url = "https://boundvariable.space/communicate"
    headers = {"Authorization": "Bearer 9272ed8c-a55f-4dbd-b50f-2970446a6c09"}

    def call(self, prompt):
        icfp = ICFP()
        encoded_prompt = icfp.encode(prompt)
        response = requests.post(self.url, headers=self.headers, data=encoded_prompt)
        decoded_response = icfp.decode(response.text)

        return response, decoded_response
