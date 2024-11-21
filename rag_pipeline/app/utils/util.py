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
