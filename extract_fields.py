import json
import csv
import os
from database import DatabaseManager
from openai import OpenAI
from langchain_core.prompts import PromptTemplate
from process_docs import ProcessDocuments
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


class ExtractField:
    def __init__(self):
        self.prompt_template = PromptTemplate.from_template(
            """
            You are an AI assistant specializing in extracting specific fields from business contracts. 
            Your task is to retrieve the requested field value from the provided contract content.

            Context:
            - The documents you are analyzing are legally binding contracts between businesses or entities.
            - Fields you are tasked with extracting include key contract details such as dates, company names, terms, parties involved, and other important business information.
            - Your role is to accurately extract these values without any assumptions or additional commentary.

            Instructions:
            1. Based on the provided field name and the relevant contract content, extract the value for the specified field in the following format:
            {{ "value": "[Extracted value]", "field_value_found": true }} if the value is found.
            2. If the value is not present in the provided content or cannot be determined, return:
            {{ "value": "null", "field_value_found": false }}.
            3. Return the output in plain text, not as a code cell or in markdown.
            4. Do not hallucinate or invent any information. If the content does not contain the answer, return "null" as the value.
            5. Ensure your response is based only on the provided contract content and related field.
            6. Return the output only in the JSON format described above, with no additional text or explanations.

            Required Field: {required_field}
            Relevant Contract Content: {similar_content}

            Return only the value in the strict JSON format.
            """
        )

    def extract_field_value(self, required_field, similar_content, max_retries=3):
        """
        Sends a prompt to the LLM and retries if the response is not in the expected JSON format.
        Returns the extracted field value or 'null' if not found.
        """
        prompt = self.prompt_template.format(
            required_field=required_field, similar_content=similar_content
        )

        for attempt in range(max_retries):
            # Create a chat completion using the OpenAI client
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Ensure the model name is correct
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            # Extract the content from the response
            response_text = response.choices[0].message.content.strip()

            print(f"Response: {response_text}\n\n\n")

            try:
                response_json = json.loads(response_text)

                # Check if the response is in the expected format
                if "value" in response_json and "field_value_found" in response_json:
                    return response_json
            except json.JSONDecodeError:
                print(f"Attempt {attempt + 1} failed: Invalid JSON format.")
                # Retry in case of a JSON format error

        # If all attempts fail, return a default value
        return {"value": "null", "field_value_found": False}

    def write_to_csv(self, extracted_data, output_file="output.csv"):
        """
        Writes the extracted field values into a CSV file.
        """
        with open(output_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=extracted_data.keys())
            writer.writeheader()
            writer.writerow(extracted_data)
