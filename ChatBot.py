from openai import OpenAI

# openAI api를 사용할 수 있게 api key를 입력받은 client 객체 생성
OPENAI_API_KEY="api key 입력"
client = OpenAI(api_key = OPENAI_API_KEY)
  
# 앞으로 메세지들을 저장할 리스트
user_message = [
     {"role": "system", "content": "You are the best resume consultant expert"}
]

end_word = '종료'
print(f"자기소개서 질문을 입력해주세요. 질문이 끝났다면 \"{end_word}\" 라고 말해주세요.\n\n")

# 유저가 입력한 값을 저장할 변수
user_question = ""
user_question = input("Any question? ")

if user_question == end_word:
    print(f"이용해주셔서 감사합니다. 합격을 기원합니다.")

# 유저가 입력한 값을 리스트에 저장
user_message.append({
    "role": "user",
    "content": user_question})

# completion 변수에 gpt가 생성한 값을 저장
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=user_message
)

# gpt 응답을 저장하는 변수
response = completion.choices[0].message.content
print(response)

# gpt 응답을 리스트에 저장
user_message.append({
  "role": "assistant",
  "content": response})

print("\n\n")
