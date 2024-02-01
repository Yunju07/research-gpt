import os

from atlassian import Confluence
from markdownify import markdownify as md

from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import DirectoryLoader


md_folder_name = "tmp_md"
confluence_access_token = "NTQ3MjAzMjgwMTE3OmQmIKJAUmvyCLJ9gTbajyVyBsqV"
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


def LoadApiKey():
   os.environ["OPENAI_API_KEY"]

def RetrieveConfluencePage(search_keyword=""):
 
    path_of_this_file = os.path.dirname(os.path.realpath(__file__))
    os.chdir(path_of_this_file)
    try:
       os.mkdir(md_folder_name)
    except:
        os.chdir(md_folder_name)
        for file in os.listdir():
            os.remove(file)
        os.chdir(path_of_this_file)
    
    base_url = 'https://share.nice.co.kr'
    my_access_token = confluence_access_token
    space='~dkws@nice.co.kr'
    confluence = Confluence(
    url=base_url,
    token=my_access_token
    )

    cql = f'type = "Page" AND title ~ "{search_keyword}"'
 
    reference_url = []
 
    pages = confluence.cql(cql, start=0, limit=50, expand=None, include_archived_spaces=None, excerpt=None)
    for i, page in enumerate(pages['results']):
        # 작성한 사용자 관련된 정보도 실을 수 있다면 더 정확해 질 것 같다.
        id = page['content']['id']
        title = page['content']['title']
        
        # body 내용 읽어오는 방법 ...
        this_page = confluence.get_page_by_id(id, expand='body.storage')
 
        body_html = this_page['body']['storage']['value']
        reference_url.append(base_url+page['content']['_links']['webui'])
        body_markdown = md(body_html)

        with open(f"{md_folder_name}/tmp_{i}.md", 'w', encoding='utf-8') as f:
            f.write(f"# TITLE: {title}\n\n")
            f.write(body_markdown)

    print("# Reference", "#"*100)
    for url in reference_url:
        print(url)


if __name__ == "__main__":
    print("\n\n## Load API Key")
    LoadApiKey()

    print("\n\n## Retrieval")
    # Retrieve에 대한 정의 필요
    # 우선은 키워드는 내가 지정해서 검색
    # CQL 검색문법으로 검색결과가 더 정확해져야 한다.
    RetrieveConfluencePage("BATCH")

    print("\n\n## Ask GPT") 
    # loader = UnstructuredMarkdownLoader(md_folder_name)
    loader = DirectoryLoader(md_folder_name, '*.md')

    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    splits = text_splitter.split_documents(docs)

    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

    # Retrieve and generate using the relevant snippets of the blog.
    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")

    print(prompt)

    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

    # def format_docs(docs):
    #    return "\n\n".join(doc.page_content for doc in docs)

    # rag_chain = (
    # {"context": retriever | format_docs, "question": RunnablePassthrough()}
    # | prompt
    # | llm
    # | StrOutputParser()
    # )
    
    # def q_n_a(question, rag_chain):
    #     print(f"Q.\n{question}\n")
    #     print("A.\n", rag_chain.invoke(question))
    #     print()
    #     print()
    # q_n_a("나이스인 배치의 step이의 순서가 어떻게 됩니까?", rag_chain)


    # vectorstore.delete_collection()