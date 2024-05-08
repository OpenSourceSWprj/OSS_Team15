from flask import Flask, request

from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\hojin.lee\\Desktop\\OSS_Team15-main\\OSS_Team15-main\\test.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
OPENAI_API_KEY = "sk-proj-VvldGEMD4RuhGImfVEM2T3BlbkFJ2GnK87eyYguabtOmjziE"
client = OpenAI(api_key=OPENAI_API_KEY)
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