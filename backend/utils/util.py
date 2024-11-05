import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import yaml
config = yaml.safe_load(open("config.yaml", "r"))

reranker_model_name = config["reranker_model_name"]

tokenizer = AutoTokenizer.from_pretrained(reranker_model_name, trust_remote_code=True)
model = AutoModelForSequenceClassification.from_pretrained(reranker_model_name, trust_remote_code=True)
model.eval()

def rerank_chunks(chunks, query):
    """
    Rerank the given chunks based on their relevance to the query.
    
    Parameters:
    - chunks: List of dictionaries containing text and page number.
    - query: The input query string for reranking.
    
    Returns:
    - List of top 5 ranked chunks in the same format as input.
    """
    # Create pairs of (query, chunk) for reranking
    pairs = [[query, chunk['text']] for chunk in chunks]
    
    # Tokenize pairs for reranking
    inputs = tokenizer(pairs, padding=True, truncation=True, return_tensors='pt', max_length=512)
    
    # Get reranking scores from the model
    with torch.no_grad():
        outputs = model(**inputs, return_dict=True).logits.view(-1, ).float()
    
    # Get top 5 indices based on scores
    top_indices = torch.argsort(outputs, descending=True)[:5]
    
    # Return top 5 chunks in original format
    top_chunks = [chunks[i] for i in top_indices]
    
    return top_chunks
    
def convert_list_to_xml(data_list):
    """
    Convert a list of dictionaries containing 'text' and 'page_number' to an XML-like format.

    Args:
        data_list (list): A list of dictionaries where each dictionary contains 'text' and 'page_number'.

    Returns:
        str: The converted data in XML-like format.
    """
    # Initialize the XML-like string
    xml_output = "<Context>\n"

    # Iterate over the data list and construct the XML-like format
    for i, item in enumerate(data_list, start=1):
        text = item['text']
        page_number = item['page_number']
        xml_output += f"  <Chunk{i}>\n"
        xml_output += f"    <Text>\n      {text}\n    </Text>\n"
        xml_output += f"    <PageNumber>{page_number}</PageNumber>\n"
        xml_output += f"  </Chunk{i}>\n"

    # Close the Context tag
    xml_output += "</Context>"

    return xml_output
