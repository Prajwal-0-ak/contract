
import os
from pydantic_settings import BaseSettings
from typing import List, Dict, ClassVar

class Settings(BaseSettings):
    """
        1. Configuration settings for the Contract Analysis System Backend using Pydantic's BaseSettings.
        2. Manages project metadata, database paths and URLs for SOW and MSA contracts, 
        3. Milvus database settings, model names, embedding parameters, prompt templates, and field definitions for extraction guidelines.
        4. Ensures centralized management of essential configuration parameters.
    """
    PROJECT_NAME: str = "Contract Analysis System"
    VERSION: str = "1.0.0"

    BASE_DIR: ClassVar[str] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DB_DIR: ClassVar[str] = os.path.join(BASE_DIR, 'db')

    SOW_DATABASE_URL: str = f"sqlite:///{os.path.join(DB_DIR, 'sow_contracts.sqlite')}"
    MSA_DATABASE_URL: str = f"sqlite:///{os.path.join(DB_DIR, 'msa_contracts.sqlite')}"
 
    MILVUS_URI: str = os.path.join(DB_DIR, 'milvus_test.db')
    MILVUS_COLLECTION_NAME: str = "contract_collection"
    
    EMBEDDING_MODEL_NAME: str = "jinaai/jina-embeddings-v2-small-en"
    RERANKER_MODEL_NAME: str = "jinaai/jina-reranker-v2-base-multilingual"
    
    DIMENSION: int = 512
    CHUNK_SIZE: int = 2048
    CHUNK_OVERLAP: int = 25
    
    # Prompt Template
    PROMPT_TEMPLATE: str = """
    You are a Data Engineer, specializing in extracting specific fields from business or financial contracts. So, your task is to retrieve the requested field value from the provided contract content. Make sure 

    Context:
    - The documents you are analyzing are legally binding contracts between businesses or entities.
    - Fields you are tasked with extracting include key contract details such as dates, company names, terms, parties involved, and other important financial information.
    - Your role is to accurately extract these values without any assumptions or additional commentary.

    Instructions:
    1. Before doing anything, you MUST think step by step like so:
    <steps>
    Step 1:
    <your thoughts>

    Step2:
    <your thoughts>
    ...
    </steps>

    And then based on the provided field name and the relevant contract content, extract the value for the specified field like so:

    <extracted>
    {{ "value": "[Extracted value]", "field_value_found": true, "page_number": "[Page No of The Chunk In Which The Extracted Field Is Present]" }} if the value is found.
    </extracted>

    This SHOULD be your OUTPUT FORMAT.

    2. If the value is not present in the provided content or cannot be determined, return:
      <extracted>
        {{ "value": "null", "field_value_found": false, "page_number": "0" }}
      </extracted>
    3. Make sure page_number corresponds to the chunk where the field value is located. Make sure single page_number is returned.  
    4. Return the output in plain text, not as a code cell or in markdown.
    5. Do not hallucinate or invent any information. If the content does not contain the answer, return "null" as the value.
    6. Ensure your response is based only on the provided contract content's and related field.
    7. Return the output ONLY in the format described above.

    Points To Remember while extracting {required_field} : {points_to_remember}
    Required Field: {required_field}
    Query: {query}
    Relevant Contract Content: {similar_content}
    """

    # SOW Fields to Extract
    SOW_FIELDS_TO_EXTRACT: List[str] = [
        "client_company_name", "currency", "sow_start_date", "sow_end_date",
        "cola", "credit_period", "inclusive_or_exclusive_gst", "sow_value",
        "sow_no", "type_of_billing", "po_number", "amendment_no",
        "billing_unit_type_and_rate_cost", "particular_role_rate"
    ]

    # SOW Queries for Each Field
    SOW_QUERY_FOR_EACH_FIELD: Dict[str, str] = {
        "client_company_name": "What is the name of the client company or recipient of services in the contract?",
        "currency": "What is amount mentioned in the contract? Is it in USD($) OR INR(₹)?.",
        "sow_start_date": "What is the start date or effective date of the Statement of Work (SOW) as mentioned in the document?. It may be written as effective from.",
        "sow_end_date": "When does the term of the Statement of Work (SOW) end? Identify the exact end date or any expiration date mentioned in the document.",
        "cola": "What is the cost of living adjustment (COLA) mentioned in the contract?",
        "credit_period": "Invoice will be raised on the last day of the month and the payment to be made net 45 days of receiving invoice. What is the credit period mentioned in the contract?",
        "inclusive_or_exclusive_gst": "What are the terms regarding the inclusion or exclusion of GST in the pricing structure, as detailed in the amendment or Statement of Work (SOW)?",
        "sow_value": "Can you extract the total monetary value or sow value specified for the services in the contract's Statement of Work (SOW) or any amendments?",
        "sow_no": "What is the Statement of Work (SOW) number mentioned in the document?",
        "type_of_billing": "What is the billing or project type mentioned in this contract?",
        "po_number": "What is the Purchase Order (PO) number mentioned in the document?",
        "amendment_no": "What is the Amendment Number mentioned in the document? Your response should be the Amendment Number.",
        "billing_unit_type_and_rate_cost": "What is the unit type mentioned for billing in this contract? Look for terms like 'per FTE', 'per bag', 'per transaction' or per something along with cost associated with it.",
        "particular_role_rate": "What is the rate for particular role mentioned in the contract? For example, 'What is the rate for Associates mentioned in the contract?' or 'What is the rate for Senior Associates mentioned in the contract?' or 'What is the rate for Team Lead or QA mentioned in the contract?' etc."
    }

    # SOW Points to Remember
    SOW_POINTS_TO_REMEMBER: Dict[str, str] = {
        "client_company_name": "The service provider is Next Wealth, so the other party is the client. Next Wealth is the service provider name so it is not the client company name.",
        "currency": "Your unit value should be in 'USD' OR 'INR'?",
        "sow_start_date": "\n1. Make sure you do not return some unrelated date as the effective start date. \n2. The format should be YYYY-MM-DD. \n3. If date is not specified, then return 'null'.",
        "sow_end_date": "\n1. Make sure you do not return some unrelated date as the end date. \n2. The format should be YYYY-MM-DD. \n3. If date is not specified, then return 'null'.",
        "cola": "Your response should be a numerical value. Its full form is Cost of Living Adjustment. It general in terms of percentage.",
        "credit_period": "\n1. Your response should be a numerical value. \n2. It is the number of days after the invoice is raised. \n3. It is present in the payment terms section in this manner: 'Invoice will be raised on the last day of the month and the payment to be made net 45 days of receiving invoice.'",
        "inclusive_or_exclusive_gst": "\n1. Your response should be 'Inclusive' or 'Exclusive'. \n2. Only if the content is not sufficient to determine the answer, return 'Exclusive'. But never return NULL for this field.",
        "sow_value": "Your response should be a numerical value. It is the total monetary value or sow value specified for the services in the contract's Statement of Work (SOW) or any amendments.",
        "sow_no": "\n1. Your response should be the SOW number. \n2. It is present in the title section of the contract. \n3. Do not mistakenly return the amendment number or some other number as the SOW number.",
        "type_of_billing": "\n1. Your response should be 'Transaction Based' or 'FTE Based'. \n2. In case of 'Transaction Based', the unit type is 'per transaction' or 'per run' or 'per batch' or 'per unit' or 'per SKU' or 'per batch' etc will be mentioned. \n3. In case of 'FTE Based', the unit type is 'per FTE' will be mentioned.",
        "po_number": "\n1. Your response should be the PO number. \n2. Do not mistakenly return the amendment number or some other number as the PO number.",
        "amendment_no": "\n1. Your response should be the Amendment Number. \n2. Do not mistakenly return the SOW number or some other number as the amendment number.",
        "billing_unit_type_and_rate_cost": "\n1. Your response should be the relevant unit type along with the cost or rate. \n2. The unit type is the value mentioned after the word 'per'. \n3. The cost or rate is the value mentioned after the unit type. \n4. If there are more than one unit type and cost or rate, then return them in the following manner: 'per sample - 1000, per item - 5000', etc.",
        "particular_role_rate": "\n1. Your response should be the rate for the particular role mentioned in the contract. \n2. The rate is the value mentioned after the word 'per'. \n3. If there are more than one rate, then return them in the following manner: 'Associate - 1000, Senior Associate - 5000', etc."
    }

    SOW_QUERIES: Dict[str, List[str]] = {
        "client_company_name": [
            "Identify the name of the client company or recipient of services in the contract. The service provider is Next Wealth, so the other party is the client.",
            "What is the name of the recipient company? Next Wealth is the service provider name so extract the recipient company name."
        ],
        "currency": [
            "What is amount mentioned in the contract? Is it in USD($) OR INR(₹)?",
            "What is the currency unit in USD($) or INR(₹) paid for an FTE per month?"
        ],
        "sow_start_date": [
            "What is the start date or effective date of the Statement of Work (SOW) as mentioned in the document? Look for terms such as 'SOW Effective Date' or any specific commencement date",
            "This Statement of Work no. 1 (“SOW”), effective as of 31st July 2023, is by and between Infostretch  Corporation  (India)  Private  Limited"
        ],
        "sow_end_date": [
            "When does the term of the Statement of Work (SOW) end? Identify the exact end date or any expiration date mentioned in the document. Look for phrases such as 'continue to be in force until' or 'terminate'.",
            "What is the termination date of the SOW, including any specific conditions or notice period required for termination?"
        ],
        "cola": [
            "What is the cost of living adjustment (COLA) mentioned in the contract?"
        ],
        "credit_period": [
            "Invoice will be raised on the last day of the month and the payment to be made net 45 days of receiving invoice.",
            "Credit period is 45 days from the date of invoice. What is the credit period mentioned in the contract?"
        ],
        "inclusive_or_exclusive_gst": [
            "What are the terms regarding the inclusion or exclusion of GST in the pricing structure, as detailed in the amendment or Statement of Work (SOW)?",
            "Can you identify any clauses in the amendment or SOW that specify whether applicable taxes, including GST, are included or excluded in the quoted service rates?",
            "Does the document clarify if the fees or charges mentioned are inclusive or exclusive of GST? Look for relevant sections in the SOW or amendment."
        ],
        "sow_value": [
            "Can you extract the total monetary value or sow value specified for the services in the contract's Statement of Work (SOW) or any amendments?",
            "What is the final contract value as described in the SOW, including adjustments, if applicable, in the amendments?",
            "What is the total value of the Statement of Work (SOW), including all relevant costs or services, as outlined in the contract and amendments?"
        ],
        "sow_no": [
            "What is the Statement of Work (SOW) number mentioned in the document? Identify the unique identifier for the SOW, often found in the title or first section of the contract.",
            "Extract the Statement of Work Number (SOW No.) associated with the agreement or amendment, usually found at the beginning of the document.",
            "In which section is the Statement of Work number (SOW No.) mentioned? It's typically present in the opening paragraph or title of the agreement."
        ],
        "type_of_billing": [
            "What is the billing or project type mentioned in this contract? Identify if the payment model is based on 'per task,' 'per unit,' or 'per transaction' (e.g., 'per SKU,' 'per batch') or if it's based on 'per FTE' (Full-Time Equivalent), such as 'per FTE per hour' or 'per FTE per month'.",
            "Does the contract mention a billing structure based on 'per transaction' (e.g., 'per run,' 'per batch,' 'per unit') or a 'per FTE' model (e.g., 'per FTE per hour,' 'per FTE per month')? Extract the relevant details indicating whether the project is transaction-based or FTE-based.",
            "Identify the project or billing type in the contract. Is it based on 'per task,' 'per item,' 'per transaction' pricing (e.g., 'per SKU,' 'per batch') or 'FTE-based' pricing (e.g., 'per FTE per month' or 'per FTE per hour')? Extract the section that describes the billing model."
        ],
        "po_number": [
            "What is the Purchase Order (PO) number mentioned in the document? Look for fields labeled as 'PURCHASE ORDER #,' 'PO NUMBER,' or 'PURCHASE ORDER', typically accompanied by order dates or other related information.",
            "Can you extract the PO number from the contract? It might be listed under terms like 'PURCHASE ORDER #,' 'PO NUMBER,' or a similar identifier, often followed by a date or other order details.",
            "Identify the Purchase Order (PO) number in the contract. It could appear as 'PURCHASE ORDER #,' 'PO NUMBER,' or related terms and may be located alongside fields like 'ORDER DATE' or 'PAYMENT TERMS.'"
        ],
        "amendment_no": [
            "What is the Amendment Number mentioned in the document? Look for terms like 'Amendment #,' 'AMENDMENT NO,' or similar phrases, which typically appear alongside the Statement of Work Number or related contract details.",
            "Can you identify the Amendment Number in the contract? It may be found as 'Amendment #,' 'AMENDMENT NO,' or other variations, often associated with a Statement of Work Number or contract value adjustments.",
            "Extract the Amendment Number from the document. It might be indicated as 'Amendment #,' 'AMENDMENT NO,' or relevant terms and is usually linked to contract changes or the Statement of Work Number."
        ],
        "billing_unit_type_and_rate_cost": [
            "What is the unit type mentioned for billing in this contract? Look for terms like 'per FTE', 'per bag', 'per transaction' or per something. Your response should be the relevant unit type along with the cost or rate.",
            "Can you identify the unit type and cost or rate for billing in the contract? Look for terms like 'per FTE', 'per bag', 'per transaction' or per something and the associated cost or rate.",
            "Identify the unit type and cost or rate for billing in the contract. Is it 'per FTE' or 'per bag' or 'per transaction' or per something and the associated cost or rate? Extract the relevant details indicating the billing model and its associated cost or rate."
        ],
        "particular_role_rate": [
            "What is the rate for particular role mentioned in the contract? For example, 'What is the rate for Associates mentioned in the contract?' or 'What is the rate for Senior Associates mentioned in the contract?' or 'What is the rate for Team Lead or QA mentioned in the contract?' etc.",
            "Identify the rate for a specific role mentioned in the contract. For example, 'What is the rate for Associates mentioned in the contract?' or 'What is the rate for Senior Associates mentioned in the contract?' or 'What is the rate for Team Lead or QA mentioned in the contract?' etc.",
            "Extract the rate for a particular role from the contract. For example, 'What is the rate for Associates mentioned in the contract?' or 'What is the rate for Senior Associates mentioned in the contract?' or 'What is the rate for Team Lead or QA mentioned in the contract?' etc."
        ]
    }

    # MSA Fields to Extract
    MSA_FIELDS_TO_EXTRACT: List[str] = [
        "client_company_name", "currency", "msa_start_date", "msa_end_date",
        "info_security", "insurance_required", "limitation_of_liability", "data_processing_agreement"
    ]

    # MSA Queries for Each Field
    MSA_QUERY_FOR_EACH_FIELD: Dict[str, str] = {
        "client_company_name": "What is the name of the client company or recipient of services in the contract?",
        "currency": "What is amount mentioned in the contract? Is it in USD($) OR INR(₹)?.",
        "msa_start_date": "What is the start date or effective date of the Master Service Agreement (MSA) as mentioned in the document?. It may be written as effective from.",
        "msa_end_date": "When does the term of the Master Service Agreement (MSA) end? Identify the exact end date or any expiration date mentioned in the document.",
        "info_security": "Is there any information security clause or requirement mentioned in the contract?",
        "insurance_required": "What are the insurance requirements specified in the contract?",
        "limitation_of_liability": "What is the limit of liability mentioned in the contract?",
        "data_processing_agreement": "Is there a Data Processing Agreement (DPA) mentioned in the contract? If yes, extract the relevant details."
    }

    # MSA Points to Remember
    MSA_POINTS_TO_REMEMBER: Dict[str, str] = {
        "client_company_name": "The service provider is Next Wealth, so the other party is the client. Next Wealth is the service provider name so it is not the client company name.",
        "currency": "Your unit value should be in 'USD' OR 'INR'?",
        "msa_start_date": "\n1. Make sure you do not return some unrelated date as the effective start date.\n2. The format should be YYYY-MM-DD.\n3. If date is not specified, then return 'null'.",
        "msa_end_date": "\n1. Make sure you do not return some unrelated date as the end date.\n2. The format should be YYYY-MM-DD.\n3. If date is not specified, then return 'null'.",
        "info_security": "\n1. Your response should be just 'Specified' or 'Not Specified'.\n2. If there is 'information security' clause or keyword, then return 'Specified' otherwise 'Not Specified'.\n3. Most of the time, it is 'Not Specified'.",
        "insurance_required": "\n<Very_Important>\n1. From the provided content, you are going to extract the multiple fields related to insurance specified in the contract.\n2. Following are fields that you need to extract: 'insurance_required', 'type_of_insurance_required', 'is_cyber_insurance_required', 'cyber_insurance_amount', 'is_workman_compensation_insurance_required', 'workman_compensation_insurance_amount', 'other_insurance_required', 'other_insurance_amount'.\n3. If the content is not sufficient to determine the answer, return 'null' for each field.\n4. There are chances that particular insurance is required, but the amount is not specified. In such cases, return 'null' for the amount field and 'Yes' for the insurance required field.\n5. Example output:\n{\n  'insurance_required': {'value': 'Yes', 'page_number': 12},\n  'type_of_insurance_required': {'value': ['General Liability', 'Cyber Liability', 'Professional Liability'], 'page_number': 12},\n  'is_cyber_insurance_required': {'value': 'Yes', 'page_number': 12},\n  'cyber_insurance_amount': {'value': 'null', 'page_number': 12},\n  'is_workman_compensation_insurance_required': {'value': 'No', 'page_number': 12},\n  'workman_compensation_insurance_amount': {'value': 'null', 'page_number': 12},\n  'other_insurance_required': {'value': 'Professional Liability', 'page_number': 12},\n  'other_insurance_amount': {'value': '$2,000,000', 'page_number': 12}\n}\n6. Make sure you return the output in the above format. But do not return the example output.\n7. 'type_of_insurance_required' field should be a list of insurance types. This can be one or more than one. These types can be anything like 'General Liability', 'Cyber Liability', 'Professional Liability' etc. Give names to the types as mentioned in the content.\n</Very_Important>",
        "limitation_of_liability": "\n1. Your response should be 'Yes' or 'No'.\n2. If there is 'limitation of liability' clause or keyword, then return 'Yes' otherwise 'No'.",
        "data_processing_agreement": "\n1. Your response should be 'Yes' or 'No'.\n2. If there is 'Data Processing Agreement' clause or keyword, then return 'Yes' otherwise 'No'."
    }

    MSA_QUERIES: Dict[str, List[str]] = {
        "client_company_name": [
            "Identify the name of the client company or recipient of services in the contract. The service provider is Next Wealth, so the other party is the client.",
            "What is the name of the recipient company? Next Wealth is the service provider name so extract the recipient company name."
        ],
        "currency": [
            "What is amount mentioned in the contract? Is it in USD($) OR INR(₹)?",
            "What is the currency unit in USD($) or INR(₹) paid for an FTE per month?"
        ],
        "msa_start_date": [
            "What is the start date or effective date of the Master Service Agreement (MSA) as mentioned in the document? Look for terms such as 'MSA Effective Date' or any specific commencement date",
            "What is the start date of the Master Service Agreement (MSA)?"
        ],
        "msa_end_date": [
            "When does the term of the Master Service Agreement (MSA) end? Identify the exact end date or any expiration date mentioned in the document. Look for phrases such as 'continue to be in force until' or 'terminate'.",
            "What is the termination date of the MSA, including any specific conditions or notice period required for termination?"
        ],
        "info_security": [
            "Is there any information security clause or requirement mentioned in the contract?",
            "Can you identify any clauses related to information security in the contract? If so, provide the details."
        ],
        "insurance_required": [
            "What are the details regarding insurance specified in the contract?"
        ],
        "limitation_of_liability": [
            "What is the limit of liability mentioned in the contract?",
            "Can you identify the maximum liability amount specified in the contract terms?"
        ],
        "data_processing_agreement": [
            "Is there a Data Processing Agreement (DPA) mentioned in the contract? If yes, extract the relevant details.",
            "Can you identify any clauses related to Data Processing Agreement (DPA) in the contract? If so, provide the details."
        ]
    }
    
    # Additional Configurations (If any)
    class Config:
        case_sensitive = True

settings = Settings()