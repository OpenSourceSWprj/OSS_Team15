import json

from openai import OpenAI
from flask import jsonify
from numpy import dot
from numpy.linalg import norm
from crawling import crawlurl

from Temp import client, UserAnswer
from Temp import Crawlings, app
def cosine_similarity(A, B):
    return dot(A, B)/(norm(A)*norm(B))



# gpt로 입력받은 텍스트를 임베딩
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def find_nearest(vector):
    maxval = 0
    indexval = 0
    for number in range(1,57):
        embedding = Crawlings.query.get(number)
        queryVec = json.loads(embedding.QuestionVector)
        temp = abs(cosine_similarity(queryVec,vector))
        if(temp>maxval):
            maxval = temp
            indexval = number
    return indexval

# flask로 입력받은 값을 저장하고 gpt가 출력한 값을 return하는 함수
def get_response(question, keywords):
    # 앞으로 메세지들을 저장할 리스트
    user_message = [
        {"role": "system", "content": "You are the best resume consultant expert"}
    ]


    vector_result = get_embedding(text="질문 : [" + question+"] + 키워드 : ["+keywords+"]")

    urlid = find_nearest(vector_result)

    con = Crawlings.query.get(urlid)
    crawled_text = crawlurl(con.URL)
    print(con.URL)

    user_question = "see the resume ["+crawled_text + ("] and extract various keywords that are not present in the original keywords [") + keywords+"]. please answer in korean. Display them separated by '/'. Respond only with combinations of keywords and '/'."
    # gpt 응답을 리스트에 저장
    user_message = [
        {"role": "system", "content": "You are the best resume consultant expert"}
    ]
    user_message.append({
        "role": "user",
        "content": user_question})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=user_message
    )


    response = completion.choices[0].message.content



    

    return response


def check_moderation(text):
    """
    주어진 텍스트가 OpenAI의 Moderation API에서 부적절한지 여부를 체크하는 함수.

    Args:
    text (str): 검사할 텍스트
    

    Returns:
    bool: 텍스트가 부적절하면 True, 그렇지 않으면 False
    """

    
    response = client.moderations.create(input=text)

    output = response.results[0]


    if output:
        return True


def translate_text(text):
    # GPT-4 모델에게 번역 요청을 보냅니다
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content":f"Translate the following text to korean: {text}"}
        ]
    )


    response = completion.choices[0].message.content


    return response




@app.route('/get_refactoring/<question>', methods=['GET'])
def get_refactoring(question):
    # Find the QuestionID for the given question
    question_entry = UserAnswer.query.filter_by(Question=question).first()
    if question_entry:
        question_id = question_entry.QuestionID
    else:
        # Handle the case if the question doesn't exist
        return jsonify({'error': 'Question not found'}), 404

    keyword_responses = []

    print(question_id)

    # Filter UserAnswer entries based on the QuestionID
    answers = UserAnswer.query.filter_by(QuestionID=question_id).all()

    print(answers)

    for answer in answers:
        keyword_responses.append((answer.keyword, answer.user_answer))

    # 앞으로 메세지들을 저장할 리스트
    user_message = [
        {"role": "system", "content": "You are a job seeker writing a resume for the company you desperately want."}
    ]

    print(str(keyword_responses))
    user_question = "Thank you for supporting our company. Please answer the following questions - Q: " + question  + "(Here's the information we have about you: " + str(keyword_responses) + "). Please be sure to include information about yourself when answering the questions. Give your best answer using all your information. Enclose your answers using your own information in curly brackets each given information. Please be sure to answer in Korean. "

    user_message.append({
        "role": "user",
        "content": user_question})

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=user_message
    )


    response = completion.choices[0].message.content

    return jsonify({'refactoring': response})