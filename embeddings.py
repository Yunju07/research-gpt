import openai
import os
import pandas as pd
import redis
from PyPDF2 import PdfReader
from io import BytesIO
import hashlib

db = redis.StrictRedis(host='localhost', port=6379, db=0)


OPENAI_API_KEY = os.environ('OPENAI_API_KEY')


def get_embedding(text, model="text-embedding-ada-002"):
        text = text.replace("\n", " ")
        openai.api_key = OPENAI_API_KEY
        return openai.embeddings.create(input = [text], model=model).data[0].embedding

def extract_txt(txt):
    with open(txt, "r") as f:
        text = f.read()
    return str(text)

def extract_pdf(pdf):
    print("Parsing paper")
    number_of_pages = len(pdf.pages)
    print(f"Total number of pages: {number_of_pages}")
    paper_text = []
    for i in range(number_of_pages):
        page = pdf.pages[i]
        page_text = []

        def visitor_body(text, cm, tm, fontDict, fontSize):
            x = tm[4]
            y = tm[5]
            # ignore header/footer
            if (y > 50 and y < 720) and (len(text.strip()) > 1):
                page_text.append({"fontsize": fontSize, "text": text.strip().replace("\x03", ""), "x": x, "y": y})

        _ = page.extract_text(visitor_text=visitor_body)

        blob_font_size = None
        blob_text = ""
        processed_text = []

        for t in page_text:
            if t["fontsize"] == blob_font_size:
                blob_text += f" {t['text']}"
                if len(blob_text) >= 200:
                    processed_text.append({"fontsize": blob_font_size, "text": blob_text, "page": i})
                    blob_font_size = None
                    blob_text = ""
            else:
                if blob_font_size is not None and len(blob_text) >= 1:
                    processed_text.append({"fontsize": blob_font_size, "text": blob_text, "page": i})
                blob_font_size = t["fontsize"]
                blob_text = t["text"]
        paper_text += processed_text
    print("Done parsing paper")
    return paper_text


def create_df(data):

    if type(data) == list:
        print("Extracting text from pdf")
        print("Creating dataframe")
        filtered_pdf = []
        # print(pdf.pages[0].extract_text())
        for row in data:
            if len(row["text"]) < 30:
                continue
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
file = open("./example.pdf", 'rb')
pdf = PdfReader(file)

paper_text = extract_pdf(pdf)
df = create_df(paper_text)
df = embeddings(df)

key = hashlib.md5(file).hexdigest()
print(key)

# database saving
if db.get(key) is None:
    db.set(key, df.to_json())