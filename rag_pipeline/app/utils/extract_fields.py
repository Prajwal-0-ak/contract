
import json
import os
from dotenv import load_dotenv
import yaml
import re
from openai import OpenAI
from langchain.prompts import PromptTemplate

from app.core.config import settings

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

class ExtractField:
    """
    Provides functionality to extract specific field values from given content using a Language Model (LLM). 
    This class formats prompts based on required fields and handles retries in case of extraction failures.

    Attributes:
        prompt_template (PromptTemplate): Template used for formatting prompts based on provided settings.

    Methods:
        extract_field_value(required_field, similar_content, query, points_to_remember, max_retries=3):
            Extracts the value of a specified field from the given content using the LLM.
            
            Parameters:
                required_field (str): The name of the field to extract.
                similar_content (str): Content similar to the target content to provide context.
                query (str): The query or question to guide the extraction process.
                points_to_remember (str): Key points that the LLM should keep in mind during extraction.
                max_retries (int, optional): The maximum number of retry attempts in case of failure. Defaults to 3.
            
            Returns:
                dict: A dictionary containing the extracted field value, a boolean indicating 
                      if the field value was found, and the page number.
    """
    def __init__(self):
        self.prompt_template = PromptTemplate.from_template(settings.PROMPT_TEMPLATE)

    def extract_field_value(self, required_field, similar_content, query, points_to_remember, max_retries=3):

        prompt = self.prompt_template.format(
            required_field=required_field,
            similar_content=similar_content,
            query=query,
            points_to_remember=points_to_remember
        )

        for attempt in range(max_retries):
            try:
                # Create a chat completion using the OpenAI API
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ]
                )

                # Extract the content from the response
                response_text = response.choices[0].message.content.strip()

                # Use regex to extract the JSON part between <extracted> tags
                match = re.search(r'<extracted>(.*?)</extracted>', response_text, re.DOTALL)
                if match:
                    extracted_json_text = match.group(1).strip()
                else:
                    raise ValueError("<extracted> not found in the response.")

                # Convert the extracted text to JSON
                response_json = json.loads(extracted_json_text)
                return response_json

            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                if attempt == max_retries - 1:
                    print("Max retries reached. Returning default response.")
                    return {"value": "null", "field_value_found": False, "page_number": 0}
                else:
                    continue