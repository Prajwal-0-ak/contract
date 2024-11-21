
from datetime import datetime
import os
from app.core.config import settings
from app.utils.utilities import load_documents
from app.utils.extract_fields import ExtractField
from app.database.db_manager import DatabaseManager
from app.utils.util import convert_list_to_xml

# Import the database sessions and models
from app.database.connection import SOWSessionLocal, MSASessionLocal
from app.models.models import SOWContract, MSAContract

from sqlalchemy.orm import Session

class DocumentProcessor:
    """
    Handles processing of documents by extracting relevant fields and storing them in the database.
    """

    def __init__(self):
        # Initialize configuration settings
        self.embedding_model_name = settings.EMBEDDING_MODEL_NAME
        self.reranker_model_name = settings.RERANKER_MODEL_NAME
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.extractor = ExtractField()
        
        # Initialize the database manager with Milvus settings
        self.db_manager = DatabaseManager(
            model_name=settings.EMBEDDING_MODEL_NAME,
            milvus_uri=settings.MILVUS_URI,
            collection_name=settings.MILVUS_COLLECTION_NAME,
            dimension=settings.DIMENSION,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        self.config = settings

    def process(self, pdfType: str, file_location: str):
        """
        Processes the specified document by extracting required fields and saving the data.

        Args:
            pdfType (str): The type of PDF document ('SOW' or 'MSA').
            file_location (str): The file path to the document.

        Returns:
            list: A list of dictionaries containing extracted field data.
        """
        # Load and process the document
        pages = load_documents(file_location)
        self.db_manager.setup_milvus()
        self.db_manager.chunk_and_insert(pages)

        # Initialize extracted data storage
        extracted_data = {}
        if pdfType.upper() == "SOW":
            fields_to_extract = self.config.SOW_FIELDS_TO_EXTRACT
            queries = self.config.SOW_QUERIES
            queries_for_each_field = self.config.SOW_QUERY_FOR_EACH_FIELD
            points_to_remember = self.config.SOW_POINTS_TO_REMEMBER
        elif pdfType.upper() == "MSA":
            fields_to_extract = self.config.MSA_FIELDS_TO_EXTRACT
            queries = self.config.MSA_QUERIES
            queries_for_each_field = self.config.MSA_QUERY_FOR_EACH_FIELD
            points_to_remember = self.config.MSA_POINTS_TO_REMEMBER
        else:
            raise ValueError(f"Invalid pdfType: {pdfType}")

        # Extract each field from the document
        for field in fields_to_extract:
            field_value_found = False
            query_for_llm = queries_for_each_field.get(field, "")
            field_points_to_remember = points_to_remember.get(field, "")
            k_value = 10 if field == 'insurance_required' else 5

            # Iterate through queries to find the field value
            for query in queries.get(field, [query_for_llm]):
                if not field_value_found:
                    try:
                        similar_content = self.db_manager.retrieve_similar_content(query, k=k_value)
                        xml_content = convert_list_to_xml(similar_content)

                        response = self.extractor.extract_field_value(
                            field,
                            xml_content,
                            query=query_for_llm,
                            points_to_remember=field_points_to_remember
                        )

                        if field == 'insurance_required':
                            insurance_fields = [
                                "insurance_required",
                                "type_of_insurance_required",
                                "is_cyber_insurance_required",
                                "cyber_insurance_amount",
                                "is_workman_compensation_insurance_required",
                                "workman_compensation_insurance_amount",
                                "other_insurance_required",
                                "other_insurance_amount"
                            ]
                            # Extract multiple insurance-related fields
                            for insurance_field in insurance_fields:
                                if insurance_field in response:
                                    extracted_data[insurance_field] = {
                                        "value": response[insurance_field]["value"],
                                        "page_number": response[insurance_field]["page_number"]
                                    }
                            field_value_found = True
                            break
                        else:
                            if response.get("field_value_found"):
                                extracted_data[field] = {
                                    "value": response.get("value"),
                                    "page_number": response.get("page_number")
                                }
                                field_value_found = True
                                break
                    except Exception as e:
                        print(f"An error occurred while extracting field '{field}': {e}")

            # Set default value if field not found
            if not field_value_found:
                extracted_data[field] = {
                    "value": "null",
                    "page_number": 0
                }

        # Clean up Milvus collection after processing
        self.db_manager.delete_collection()

        # Prepare the final extracted data
        final_extracted_data = [
            {
                "field": field_name,
                "value": field_info.get("value", ""),
                "page_num": field_info.get("page_number", "0")
            }
            for field_name, field_info in extracted_data.items()
        ]

        # Determine the appropriate database session and model based on pdfType
        if pdfType.upper() == "SOW":
            db_session = SOWSessionLocal()
            contract_model = SOWContract
        elif pdfType.upper() == "MSA":
            db_session = MSASessionLocal()
            contract_model = MSAContract
        else:
            raise ValueError(f"Invalid pdfType: {pdfType}")

        try:
            # Prepare data for database insertion
            contract_data = {
                "file_name": os.path.basename(file_location),
                "upload_date": datetime.now(),
                "processed": True
            }

            # Map extracted fields to contract model attributes
            for item in final_extracted_data:
                field_name = item["field"]
                value = item["value"]
                if hasattr(contract_model, field_name):
                    if field_name == "type_of_insurance_required":
                        contract_data[field_name] = ", ".join(value) if isinstance(value, list) and value != "null" else value
                    else:
                        contract_data[field_name] = value

            # Create and save the new contract record
            contract = contract_model(**contract_data)
            db_session.add(contract)
            db_session.commit()
            db_session.refresh(contract)
        except Exception as e:
            print(f"An error occurred while saving to the database: {e}")
        finally:
            db_session.close()

        # Output extracted data for debugging
        print(f"\n\nExtracted data: {final_extracted_data}")

        # Return the extracted data
        return final_extracted_data