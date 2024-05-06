from openai import OpenAI

# openAI api를 사용할 수 있게 api key를 입력받은 client 객체 생성
OPENAI_API_KEY="api key 입력"
client = OpenAI(api_key = OPENAI_API_KEY)
  
# gpt로 입력받은 텍스트를 임베딩
def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

# flask로 입력받은 값을 저장하고 gpt가 출력한 값을 return하는 함수
def get_response(question, keywords):

    # 앞으로 메세지들을 저장할 리스트
    user_message = [
         {"role": "system", "content": "You are the best resume consultant expert"}
    ]

    user_question = "키워드" + keywords + "를 기반으로 자기소개서 질문 " + question + "에 적합한 대답을 해줘"

    # 유저가 입력한 값을 리스트에 저장
    user_message.append({
        "role": "user",
        "content": user_question})
    
    # text embedding
    vector_result = get_embedding(text=user_question)

    # gpt 응답을 저장하는 변수
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=user_message
    )

    # gpt 응답을 저장하는 변수
    response = completion.choices[0].message.content

    # gpt 응답을 리스트에 저장
    user_message.append({
      "role": "assistant",
      "content": response})

    return response
