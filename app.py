from flask import Flask, request, render_template_string
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\seokw\\PycharmProjects\\OS_Project\\OSS_Team15\\test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255),nullable=False)
    keywords = db.Column(db.String(255),nullable=False)

    def __repr__(self):
        return f'<Entry: {self.text}>'
with app.app_context():
    db.create_all()
# HTML form을 제공하는 루트 페이지
@app.route('/', methods=['GET'])
def index():
    db.create_all()
    return '''
    <!doctype html>
    <html>
    <head>
        <title>자소서 친구</title>
    </head>
    <body>
        <h1>자소서 항목,키워드</h1>
        <form action="/submit" method="post">
            <p><input type="text" name="text" placeholder="자소서 항목"></p>
            <p><textarea name="keywords" placeholder="keywords"></textarea></p>
            <p><input type="submit" value="제출"></p>
        </form>
    </body>
    </html>
    '''

# 폼 제출 처리
@app.route('/submit', methods=['POST'])
def submit():
    text = request.form['text']
    keywords = request.form['keywords']
    entry = Entry(text=text,keywords=keywords)
    db.session.add(entry)
    db.session.commit()
    return f'''
        <!doctype html>
        <html>
        <head>
            <title>입력 결과</title>
        </head>
        <body>
            <h1>제출된 텍스트</h1>
            <p>항목 : { text }</p>
            <p>키워드 : {keywords}</p>
        </body>
        </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
