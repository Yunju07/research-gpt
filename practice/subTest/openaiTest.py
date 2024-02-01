from openai import OpenAI
import os


def QueryGpt(a_sentence):
    
    prompt = f"{a_sentence}"

    client = OpenAI(
        api_key= os.environ['OPENAI_API_KEY'],
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        #model="gpt-4-1106-preview",
        model="gpt-3.5-turbo",
    )

    return chat_completion.choices[0]

response = QueryGpt("오늘 서울 날씨 어때?")
print(response)