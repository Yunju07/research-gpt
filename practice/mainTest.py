import openai
from openai.embeddings_utils import get_embedding
import os
import pandas as pd
import redis
from PyPDF2 import PdfReader
from io import BytesIO
import hashlib

# db = redis.StrictRedis(host='localhost', port=6379, db=0)


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# pdf processing
def extract_pdf(pdf):
    print("Parsing paper")
    number_of_pages = len(pdf.pages)
    print(f"Total number of pages: {number_of_pages}")
    paper_text = []
    for i in range(number_of_pages):
        page = pdf.pages[i]
        page_text = []

        text = page.extract_text().strip()
        page_text = text.split('\n')
        
        blob_text = ""
        processed_text = []

        for t in page_text:
            blob_text += f" {t}"
            if len(blob_text) >= 200 or (page_text.index(t) == len(page_text)-1):
                processed_text.append({"text": blob_text, "page": i+1})
                blob_text = ""
        paper_text += processed_text
    print("Done parsing paper")
    return paper_text

# dataframe
def create_df(data):
    if type(data) == list:
        print("Extracting text from pdf")
        print("Creating dataframe")
        filtered_pdf = []
        # print(pdf.pages[0].extract_text())
        for row in data:
            filtered_pdf.append(row)
        df = pd.DataFrame(filtered_pdf)
        # remove elements with identical df[text] and df[page] values
        df = df.drop_duplicates(subset=["text", "page"], keep="first")
        # df['length'] = df['text'].apply(lambda x: len(x))
        print("Done creating dataframe")

    elif type(data) == str:
        print("Extracting text from txt")
        print("Creating dataframe")
        # Parse the text and add each paragraph to a column 'text' in a dataframe
        df = pd.DataFrame(data.split("\n"), columns=["text"])

    return df

def embeddings(df):
    print("Calculating embeddings")
    openai.api_key = OPENAI_API_KEY
    embedding_model = "text-embedding-ada-002"
    embeddings = df.text.apply([lambda x: get_embedding(x, engine=embedding_model)])
    df["embeddings"] = embeddings
    print("Done calculating embeddings")
    return df



# process start
# file processing 
pdf = PdfReader("./pdf/2021 DB 프로젝트 1.pdf")
paper_text = extract_pdf(pdf)

# dataframe 
df = create_df(paper_text)

# embeddings
df = embeddings(df)
print(df['embeddings'])

# # database saving]
# db.set("test", df.to_json())