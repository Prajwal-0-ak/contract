
import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent.resolve()
sys.path.append(str(current_dir.parent))

from app.utils.document_processor import DocumentProcessor

def main():
    """
    Test script to process a manually placed MSA PDF file,
    extract fields, print the results, and update the SQLite database.
    """
    # Define the contract_files directory path
    contract_files_dir = os.path.join(current_dir, "contract_files")
    
    # Specify the PDF filename
    pdf_filename = "WMGTS.pdf"  # Change this to your actual file name
    pdf_path = os.path.join(contract_files_dir, pdf_filename)
    
    # Verify that the PDF file exists
    if not os.path.isfile(pdf_path):
        print(f"Error: The file '{pdf_filename}' does not exist in '{contract_files_dir}'.")
        print("Please place the PDF file in the 'contract_files/' directory and try again.")
        return
    
    # Define the contract type
    pdf_type = "SOW"
    
    # Initialize the DocumentProcessor
    try:
        processor = DocumentProcessor()
        print("Initialized DocumentProcessor.")
    except Exception as e:
        print(f"Error initializing DocumentProcessor: {e}")
        return
    
    # Process the PDF
    try:
        print(f"Processing the PDF file '{pdf_filename}' as '{pdf_type}'...")
        extracted_data = processor.process(pdf_type, pdf_path)
        print("Processing completed successfully.")
    except Exception as e:
        print(f"Error during processing: {e}")
        return
    
    # Print the extracted data
    print("\n=== Extracted Data ===")
    for item in extracted_data:
        field = item.get("field", "N/A")
        value = item.get("value", "N/A")
        page_num = item.get("page_num", "N/A")
        print(f"Field: {field}\nValue: {value}\nPage Number: {page_num}\n---------------------------")
    
    # Indicate that the SQLite database has been updated
    print("The SQLite database has been updated with the extracted data.")

    # ----------------------
    # Instructions to Test the RAG Pipeline
    # ----------------------
    #
    # 1. **Ensure Configuration:**
    #    - Verify that the RAG Pipeline is correctly configured in your application settings.
    #    - Check that all necessary environment variables (e.g., `OPENAI_API_KEY`) are set.
    #
    # 2. **Prepare Test PDF:**
    #    - Place a sample MSA PDF file (e.g., `WMGTS.pdf`) in the `rag_pipeline/contract_files/` directory.
    #    - Ensure the PDF file is properly formatted and contains the fields you intend to extract.
    #
    # 3. **Update Test Script (if needed):**
    #    - If using a different PDF file, update the `pdf_filename` variable accordingly.
    #
    # 4. **Activate Virtual Environment:**
    #    - Navigate to the `backend/` directory.
    #    - Activate the virtual environment:
    #      ```bash
    #      source venv/bin/activate  # On Windows: venv\Scripts\activate
    #      ```
    #
    # 5. **Install Dependencies:**
    #    - Ensure all backend dependencies are installed:
    #      ```bash
    #      pip install -r requirements.txt
    #      ```
    #
    # 6. **Run the Test Script:**
    #    - Execute the test script to process the PDF:
    #      ```bash
    #      cd rag_pipeline/tests
    #      python test_app.py
    #      ```
    #
    # 7. **Verify Output:**
    #    - Check the console output for extracted data.
    #    - Ensure that the fields are correctly printed and that the SQLite database has been updated.
    #
    # 8. **Troubleshoot (if necessary):**
    #    - If errors occur, review the error messages for clues.
    #    - Ensure file paths and permissions are correctly set.
    #    - Confirm that the `DocumentProcessor` is functioning as expected.

if __name__ == "__main__":
    main()