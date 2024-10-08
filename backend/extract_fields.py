import json
import os
from openai import OpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import yaml
import csv
import re

load_dotenv()

# Load configuration
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ExtractField:
    def __init__(self):
        self.prompt_template = PromptTemplate.from_template(config["prompt_template"])

    def extract_field_value(self, required_field, similar_content, query, max_retries=3):
        """
        Sends a prompt to the LLM and retries if the response is not in the expected JSON format.
        Returns the extracted field value or 'null' if not found.
        """
        prompt = self.prompt_template.format(
            required_field=required_field, similar_content=similar_content, query=query
        )

        print(f"\nQuery For LLM: {query}")

        # print(f"------------------------------Prompt: {prompt}------------------------------")

        for attempt in range(max_retries):
            # Create a chat completion using the OpenAI client
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            # Extract the content from the response
            response_text = response.choices[0].message.content.strip()

            print(f"Response Text: {response_text}")

            try:
                match = re.search(r'<extracted>(.*?)</extracted>', response_text, re.DOTALL)

                print(f"MATCH: {match}")

                if match:
                    extracted_json_text = match.group(1).strip()
                else:
                    raise ValueError("<extracted> not found.")
                response_json = json.loads(extracted_json_text)

                # Check if the response is in the expected format
                # print(f"Response JSON: {response_json}")        
                if "value" in response_json and "field_value_found" in response_json:
                    return response_json
            except json.JSONDecodeError:
                print(f"---------------------------------JSON format error in response: {response_text}---------------------------------")
                # Retry in case of a JSON format error

        # If all attempts fail, return a default response
        return {"value": "null", "field_value_found": False, "page_number": 0}

    def write_to_csv(self, extracted_data, output_file="output.csv"):
        """
        Writes the extracted field values into a CSV file.
        """
        with open(output_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=extracted_data.keys())
            writer.writeheader()
            writer.writerow(extracted_data)
