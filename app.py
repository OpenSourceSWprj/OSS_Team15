# app.py
from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy

import ChatBot

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\seokw\\PycharmProjects\\OS_Project\\OSS_Team15\\test1.db'

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

class Crawling(db.Model):
    __tablename__ = 'Crawling'
    QuestionID = db.Column(db.Integer, primary_key=True)
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
    response = ChatBot.get_response(question, keywords)

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

if __name__ == '__main__':
    app.run(debug=True)
