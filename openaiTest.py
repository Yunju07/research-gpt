import openai
import os

openai.api_key = os.environ['OPENAI_API_KEY']

def get_chat_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

question = "안녕?"
answer = get_chat_gpt_response(question)
print(answer)