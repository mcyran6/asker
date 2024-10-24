import os
import json
from PyPDF2 import PdfFileReader

def extract_toc_from_pdf(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfFileReader(file)

        # Get the table of contents
        toc = pdf_reader.getOutlines()

        # Extract the table of contents information
        toc_data = []
        for item in toc:
            if isinstance(item, list):
                for sub_item in item:
                    page_number = pdf_reader.getDestinationPageNumber(sub_item)
                    toc_data.append({'title': sub_item.title, 'page': page_number + 1})
            else:
                page_number = pdf_reader.getDestinationPageNumber(item)
                toc_data.append({'title': item.title, 'page': page_number + 1})

    return toc_data

# Usage example
pdf_file_path = 'path/to/your/pdf/file.pdf'
toc_json_file_path = 'path/to/your/json/file.json'

# Extract the table of contents
toc_data = extract_toc_from_pdf(pdf_file_path)

# Save the table of contents as a JSON file
with open(toc_json_file_path, 'w') as file:
    json.dump(toc_data, file, indent=2)

print(f"Table of contents saved to: {toc_json_file_path}")