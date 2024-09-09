import os
from process_docs import ProcessDocuments
from database import DatabaseManager
from extract_fields import ExtractField


def main():
    process_docs = ProcessDocuments()
    db_manager = DatabaseManager()
    extractor = ExtractField()

    # Load documents from the 'contract_files' folder
    docs = process_docs.load_documents()

    # Chunk and insert the documents into the database
    process_docs.chunk_and_insert(db_manager, docs)

    fields_to_extract = [
        "start_date",
        "company_name",
        "service_provider_name",
        "service_description",
        "service_charges",
        "end_date",
    ]
    queries_json = {
        "start_date": [
            "What is the effective start date of the agreement or contract?",
        ],
        "company_name": [
            "What is the name of the company or legal entity that is party to this contract?",
        ],
        "service_provider_name": [
            "What is the name of the service provider or vendor mentioned in the contract?",
        ],
        "service_description": [
            "What services are being provided under this contract?"
        ],
        "service_charges": [
            "What are the service charges or payment terms outlined in this contract?"
        ],
        "end_date": [
            "What is the termination or end date of the contract?",
        ],
    }

    extracted_data = {}

    for field in fields_to_extract:
        field_value_found = False
        for query in queries_json[field]:
            if not field_value_found:
                query_embedding = process_docs.embedding.embed_query(query)
                similar_content = db_manager.retrieve_similar_content(
                    query_embedding, top_k=5
                )
                response = extractor.extract_field_value(field, similar_content)

                if response["field_value_found"]:
                    extracted_data[field] = response["value"]
                    field_value_found = True
                    break

        if not field_value_found:
            extracted_data[field] = "null"

    extractor.write_to_csv(extracted_data)


if __name__ == "__main__":
    main()
