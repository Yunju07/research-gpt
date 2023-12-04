import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_chat_gpt_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        message = prompt
    )
    return response.choices[0]["message"]["content"]

question = "지구에서 가장 높은 산은 무엇인가요?"
answer = get_chat_gpt_response(question)
print(answer)