from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import json
import numpy as np
from numpy import dot
from numpy.linalg import norm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\hojin.lee\\Desktop\\OSS_Team15-main\\OSS_Team15-main\\test.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 데모에 필요한 최소한의 DB

class UserInput(db.Model):
    __tablename__ = 'UserInput'
    QuestionID = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    keywords = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<UserInput: {self.question}>'

class Crawlings(db.Model):
    __tablename__ = 'Crawling'
    QuestionID = db.Column(db.Integer, primary_key=True)
    QuestionVector = db.Column(db.Text, nullable=False)
    URL = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Crawling: {self.URL}>'

class Embedding(db.Model):
    __tablename__ = 'Embedding'
    QuestionID = db.Column(db.Integer, primary_key=True)
    vector = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Embedding: {self.vector}>'

class ChatbotResponse(db.Model):  # New table for storing chatbot responses
    __tablename__ = 'ChatbotResponse'
    ResponseID = db.Column(db.Integer, primary_key=True)
    response = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<ChatbotResponse: {self.response}>'

with app.app_context():
    db.create_all()
# HTML form을 제공하는 루트 페이지

@app.route('/', methods=['GET'])

def index():

    return '''
        <!doctype html>
        <html>
        <head>
            <title>자소서 친구</title>
        </head>
        <body>
            <h1>자소서 항목,키워드</h1>
            <form action="/submit" method="post">
                <p><input type="text" name="question" placeholder="자소서 항목"></p>
                <p><textarea name="keywords" placeholder="keywords"></textarea></p>
                <p><input type="submit" value="제출"></p>
            </form>
        </body>
        </html>
    '''

# 폼 제출 처리

@app.route('/submit', methods=['POST'])

def submit():

    question = request.form['question']

    keywords = request.form['keywords']

    entry = UserInput(question=question, keywords=keywords)

    db.session.add(entry)

    db.session.commit()

    # ChatBot 모듈의 함수에 질문과 키워드를 전달하여 응답을 받습니다.
    response = get_response(question, keywords)

    return f'''
        <!doctype html>
        <html>
        <head>
            <title>입력 결과</title>
        </head>
        <body>
            <h1>제출된 텍스트</h1>
            <p>항목 : { question }</p>
            <p>키워드 : { keywords }</p>
            <h1>ChatBot 응답</h1>
            <p>{ response }</p>
        </body>
        </html>
    '''
OPENAI_API_KEY = "api key 입력"
client = OpenAI(api_key=OPENAI_API_KEY)
def cosine_similarity(A, B):
    return dot(A, B)/(norm(A)*norm(B))



# gpt로 입력받은 텍스트를 임베딩
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

def find_nearest(vector):
    maxval = 0
    indexval = 0
    for number in range(1,53):
        embedding = Crawlings.query.get(number)
        #print(type(embedding.QuestionVector))
        queryVec = json.loads(embedding.QuestionVector)
        #print(type(queryVec))
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

    user_question = "키워드" + keywords + "를 기반으로 자기소개서 질문 " + question + "에 적합한 대답을 해줘"

    # 유저가 입력한 값을 리스트에 저장
    user_message.append({
        "role": "user",
        "content": user_question})

    # text embedding
    vector_result = get_embedding(text=user_question)

    urlid = find_nearest(vector_result)

    con = Crawlings.query.get(urlid)
    print(con.URL)

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

if __name__ == '__main__':
    app.run(debug=True)

