import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
import os
import pandas as pd
import redis
from PyPDF2 import PdfReader
from io import BytesIO
import hashlib

db = redis.StrictRedis(host='localhost', port=6379, db=0)


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

# 임베딩 계산 함수
def embeddings(df):
    print("Calculating embeddings")
    openai.api_key = OPENAI_API_KEY
    embedding_model = "text-embedding-ada-002"
    embeddings = df.text.apply([lambda x: get_embedding(x, engine=embedding_model)])
    df["embeddings"] = embeddings
    print("Done calculating embeddings")
    return df

# 쿼리문과 코사인 유사도가 높은 상위 n개의 조각을 데이터프레임에서 얻습니다
def search(df, query, n=2, pprint=True):
    query_embedding = get_embedding(query, engine="text-embedding-ada-002")
    df['similarity'] = df.embeddings.apply(lambda x: cosine_similarity(x, query_embedding))

    results = df.sort_values("similarity", ascending=False, ignore_index=True)
    results = results.head(n)
    sources = []
  
    for i in range(n):
        # 유사도가 크다고 나온 데이터에 대한 정보
        sources.append({"Page " + str(results.iloc[i]["page"]): results.iloc[i]["text"][:150] + "..."})
    
    return {"results": results, "sources": sources}


def create_prompt(df, user_input):
    print('Creating prompt')

    result = search(df, user_input, n=2)
    data = result['results']
    sources = result['sources']
    system_role = """Your role is to read pdf file and reply only with the content of the file. 
    You are given a query, a series of text embeddings and the title from a paper in order of their cosine similarity to the query. 
    You must take the given embeddings and return a concise and essential answer to questions in the languange of the query. Speak as softly as possible:"""

    user_input = user_input + """
    Here are the embeddings:

    1.""" + str(data.iloc[0]['text']) + """
    """

    history = [
    {"role": "system", "content": system_role},
    {"role": "user", "content": str(user_input)}]

    print('Done creating prompt')

    return {'messages': history, 'sources': sources}

def gpt(context, sources):
    print('Sending request to OpenAI')
    openai.api_key = OPENAI_API_KEY
    r = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=context)
    answer = r.choices[0]["message"]["content"]
    print('Done sending request to OpenAI')
    response = {'answer': answer, 'sources': sources}
    return response

# process start
# file processing 
pdf = PdfReader("./pdf/수익모델.pdf")
paper_text = extract_pdf(pdf)

# dataframe 
df = create_df(paper_text)

# embeddings
df = embeddings(df)
print(df['embeddings'])

# database saving
db.set("test", df.to_json())

# question about pdf
query = "free-mium 수익모델의 예시에 대해 설명해줘"
prompt = create_prompt(df, query)

# call openAI
response = gpt(prompt['messages'], prompt['sources'])
print("query : " + query)
print("answer : ")
print(response)