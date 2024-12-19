from openai import AzureOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version='2024-08-01-preview',
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
try:
    # response = client.chat.completions.create(
    #     model="o1-preview",
    #     messages=[{"role": "user", "content": "Hello, world!"}],
    # )
    
    # user_message = {
    #     "role": "user",
    #     "content": (
    #         "You are a helpful assistant. "
    #         "You will act according to the following persona: "
    #         "Language: korean, Gender: 'man', Tone: 'formal', Manner: 'manner'.\n"
    #         "hello"
    #     )
    # }
    # messages = [user_message]
    # response = client.chat.completions.create(
    #     model="o1-preview",
    #     messages=messages,        
    #     max_completion_tokens= 8192 
    # )
    persona = {}
    persona['language']='korean'
    persona['gender'] ='male'
    persona['tone'] = 'formal'
    persona['manner'] = 'manner'
    topic='Introduce my self'
    mood='happy'
    # 시스템 메시지 대신 사용자 메시지에 페르소나 정보를 포함
    persona_prompt = f"You are a helpful assistant. You will act according to the following persona: Language: {persona['language']}, Gender: {persona['gender']}, Tone: {persona['tone']}, Manner: {persona['manner']}. The conversation topic is '{topic}' and the mood is '{mood}'. "
    
    # 메시지 목록에 persona_prompt 추가 (첫 번째 메시지로)
    messages_with_persona = [{"role": "user", "content": persona_prompt}] 
    response = client.chat.completions.create(
        model="o1-preview",
        messages=messages_with_persona,       
        max_completion_tokens=2048        
    )
    # return response.choices[0].message.content    
    print(response.choices[0].message.content)
except Exception as e:
    print(f"An error occurred: {e}")