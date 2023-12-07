import fitz
from PyPDF2 import PdfReader
import tabula

# 실습 pdf 파일 경로
PDF_FILE_PATH = "./pdf/chart_test.pdf"

# PyMuPDF 
# doc = fitz.open(PDF_FILE_PATH)
# for page in doc:
#     text = page.get_text()
#     print(text)

#  PyPDF2 
# reader = PdfReader(PDF_FILE_PATH)
# pages = reader.pages
# text = ""
# for page in pages:
#   sub = page.extract_text()
#   text += sub
# print(text)

# tabula
dfs = tabula.read_pdf(PDF_FILE_PATH, pages="all", encoding='CP949')
print(len(dfs))
print(dfs[0])