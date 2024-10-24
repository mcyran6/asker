import sys
from PyPDF2 import PdfReader, PdfWriter

def extract_pages(input_pdf_path, start_page, end_page, output_pdf_path):
    input_pdf = PdfReader(input_pdf_path)
    output_pdf = PdfWriter()

    for page_num in range(start_page - 1, end_page):  # Pages are zero-indexed
        output_pdf.add_page(input_pdf.pages[page_num])

    with open(output_pdf_path, "wb") as output_file:
        output_pdf.write(output_file)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python extract_pages.py <input_pdf> <start_page> <end_page> <output_pdf>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    start_page = int(sys.argv[2])
    end_page = int(sys.argv[3])
    output_pdf_path = sys.argv[4]

    extract_pages(input_pdf_path, start_page, end_page, output_pdf_path)

