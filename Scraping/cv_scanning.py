import pdfplumber
import re
# from langchain.document_loaders import PDFPlumberLoader
from langchain_community.document_loaders import PDFPlumberLoader
import json
from helpers import clean_page_text


def extract_text_from_cv_pdf(pdf_path: str) -> str:
    """
    Extracts clean text from a CV PDF using pdfplumber.
    
    Args:
        pdf_path (str): Path to the CV PDF file.
    
    Returns:
        str: Extracted text.
    """

    all_text = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:

                # 1️⃣ Extract normal text
                text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if text:
                    all_text.append(clean_page_text(text))

                # 2️⃣ Extract tables (skills often inside tables)
                tables = page.extract_tables()
                for table in tables:
                    table_text = "\n".join(
                        [" | ".join([cell or "" for cell in row]) for row in table]
                    )
                    all_text.append(clean_page_text(table_text))

    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

    return "\n".join(all_text).strip()

def extract_cv_text_langchain(cv_path: str) -> dict:
    """
    Extract text from a single CV PDF, returning each page separately.

    Args:
        cv_path (str): Path to the CV PDF.

    Returns:
        dict: {
            "filename": ...,
            "total_pages": ...,
            "pages": [
                {"page_number": 1, "text": ...},
                ...
            ]
        }
    """

    loader = PDFPlumberLoader(cv_path)
    raw_pages = loader.load()

    pages_data = []
    for i, page in enumerate(raw_pages, start=1):
        cleaned = clean_page_text(page.page_content)
        pages_data.append({
            "page_number": i,
            "text": cleaned
        })

    return {
        "filename": cv_path.replace("\\", "/").split("/")[-1],
        "total_pages": len(raw_pages),
        "pages": pages_data
    }

if __name__ == "__main__":
    my_CV_path = r"D:\Desktop\Khaled Hany AbdElGhafar.pdf"
    extracted_text = extract_text_from_cv_pdf(my_CV_path)

    with open("extracted_cv_text_with_cleaning.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)

    extracted_using_langchain = extract_cv_text_langchain(my_CV_path)

    for page in extracted_using_langchain["pages"]:
        print(f"Page {page['page_number']}:\n{page['text']}\n{'-'*40}\n")
    
    with open("extracted_cv_langchain_v2.json", "w", encoding="utf-8") as f:
        json.dump(extracted_using_langchain, f, ensure_ascii=False, indent=4)

    with open("extracted_cv_langchain_v2.txt", "w", encoding="utf-8") as f:
        for page in extracted_using_langchain["pages"]:
            f.write(f"Page {page['page_number']}:\n{page['text']}\n{'-'*40}\n")

    print("Extraction complete. Check the output files.")
