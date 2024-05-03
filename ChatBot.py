from openai import OpenAI

client = OpenAI(api_key="sk-proj-MCMmh37bInGBajxwrdK6T3BlbkFJsMq7yMD3zQXTC4sPZ2YB")
history_message = [
     {"role": "system", "content": "You are the best resume consultant professor"}
]

end_word = '종료'
print(f"자기소개서 질문을 입력해주세요. 질문이 끝났다면 \"{end_word}\" 라고 말해주세요.\n\n")
user_question = ""

while True:
    user_question = input("Any question? ")

    if user_question == end_word:
        print(f"이용해주셔서 감사합니다. 합격을 기원합니다.")
        break

    history_message.append({
        "role": "user",
        "content": user_question})

    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=history_message
    )

    response = completion.choices[0].message.content
    print(response)

    history_message.append({
      "role": "assistant",
      "content": response})

    print("\n\n")
