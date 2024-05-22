from flask import request, jsonify
from sqlalchemy import func
from Temp import db, ChatbotResponse, UserInput, UserAnswer, app
from ChatBot import get_response, get_refactoring


# HTML form을 제공하는 루트 페이지
@app.route('/', methods=['GET'])
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>면접관 G씨</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0;
            }
            #container {
                max-width: 800px;
                margin: 20px auto;
                background-color: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                border: 1px solid #ddd;
            }
            h1 {
                text-align: center;
                color: #333;
                font-size: 24px;
                margin-bottom: 20px;
            }
            form {
                margin-top: 20px;
            }
            label {
                font-size: 16px;
                color: #333;
                display: block;
                margin-bottom: 10px;
            }
            textarea, input[type="text"] {
                width: 100%;
                padding: 12px;
                font-size: 14px;
                border-radius: 5px;
                border: 1px solid #ccc;
                margin-bottom: 20px;
                box-sizing: border-box;
            }
            input[type="submit"] {
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s ease;
                width: 100%;
            }
            input[type="submit"]:hover {
                background-color: #0056b3;
            }
            .chatgpt-mark {
                display: inline-block;
                width: 20px;
                height: 20px;
                background-image: url('https://chat.openai.com/static/images/favicon.ico');
                background-size: cover;
                margin-left: 5px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
        <div id="container">
            <h1>면접관 G씨<span class="chatgpt-mark"></span></h1>
            <form action="/submit" method="post">
                <label for="question">자기소개서 질문 하나를 선택하고 입력해주세요:</label>
                <textarea id="question" name="question" placeholder="질문을 입력해주세요." rows="5"></textarea>
                <label for="keywords">질문에 대한 키워드를 입력해주세요 (쉼표로 구분):</label>
                <textarea id="keywords" name="keywords" placeholder="키워드를 입력해주세요." rows="3"></textarea>
                <input type="submit" value="제출">
            </form>
        </div>
    </body>
    </html>
        '''


def keywordsSave(response, question_id):
    id = question_id
    keywords = response.split('/')
    keywordID = 1
    for keyword in keywords:
        entry = ChatbotResponse(keywordID=keywordID, QuestionID=id, response=keyword)
        db.session.add(entry)
        keywordID += 1
    db.session.commit()


@app.route('/get_response/<int:question_id>/<int:keyword_id>', methods=['GET'])
def get_next_response(question_id, keyword_id):
    next_response = ChatbotResponse.query.filter_by(keywordID=keyword_id + 1, QuestionID=question_id).first()
    if next_response:
        return jsonify({'response': next_response.response})
    else:
        return jsonify({'response': '질문에 대한 답변을 생성중입니다...'})


@app.route('/submit', methods=['POST'])
def submit():
    question = request.form['question']
    keywords = request.form['keywords']
    entry = UserInput(question=question, keywords=keywords)
    db.session.add(entry)
    db.session.commit()

    response = get_response(question, keywords)

    if '/' not in response:  # '/'가 포함되지 않은 응답일 때
        # 재 실행하는 코드
        return submit()

    max_question_id = db.session.query(func.max(ChatbotResponse.QuestionID)).scalar()
    if max_question_id is None:
        question_id = 1
    else:
        question_id = max_question_id + 1

    keywordsSave(response, question_id)

    response_html = ''
    keywordID = 1
    recommend = ChatbotResponse.query.filter_by(keywordID=keywordID, QuestionID=question_id).first()
    if recommend:
        response_html += f'<div id="keyword-{keywordID}">'
        response_html += f'<p>{recommend.response}</p>'
        response_html += '<div id="user-answer-container">'
        response_html += '<input type="text" id="user-answer-input" placeholder="사용자 답변">'
        response_html += '<button onclick="submitUserAnswer()">확인</button>'
        response_html += '</div>'
        response_html += '</div>'
        keywordID += 1

    next_button = '<button id="next-button" onclick="getNextResponse()">다음</button>'

    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>입력 결과</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0;
            }}
            #container {{
                max-width: 800px;
                margin: 20px auto;
                background-color: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
                border: 1px solid #ddd;
            }}
            h1 {{
                text-align: center;
                color: #333;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            p {{
                font-size: 16px;
                color: #333;
            }}
            #response-container {{
                margin-top: 20px;
            }}
            input[type="text"] {{
                width: 100%;
                padding: 12px;
                font-size: 14px;
                border-radius: 5px;
                border: 1px solid #ccc;
                margin-bottom: 20px;
                box-sizing: border-box;
            }}
            button {{
                background-color: #007bff;
                color: #fff;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s ease;
                margin-top: 20px;
                display: block;
                width: 100%;
            }}
            button:hover {{
                background-color: #0056b3;
            }}
        </style>
        <script>
            let keywordId = 1;
            const question_id = {question_id};

            function getNextResponse() {{
                const currentKeyword = document.getElementById('keyword-' + keywordId);
                if (currentKeyword) {{
                    currentKeyword.style.display = 'none';
                    keywordId++;
                    fetch(`/get_response/${{question_id}}/${{keywordId}}`)
                        .then(response => response.json())
                        .then(data => {{
                            const responseContainer = document.getElementById('response-container');
                            responseContainer.innerHTML = '';
                            if (data.response !== '질문에 대한 답변을 생성중입니다...') {{
                                responseContainer.innerHTML = `<div id="keyword-${{keywordId}}">`;
                                responseContainer.innerHTML += `<p>${{data.response}}</p>`;
                                responseContainer.innerHTML += '<div id="user-answer-container">';
                                responseContainer.innerHTML += '<input type="text" id="user-answer-input" placeholder="사용자 답변">';
                                responseContainer.innerHTML += '<button onclick="submitUserAnswer()">확인</button>';
                                responseContainer.innerHTML += '</div>';
                                responseContainer.innerHTML += '</div>';
                                document.getElementById('next-button').style.display = 'block';
                            }} else {{
                                responseContainer.innerHTML = '<p>질문에 대한 답변을 생성중입니다...</p>';
                                document.getElementById('next-button').style.display = 'none';
                                fetch(`/get_refactoring/${question}`)
                                    .then(response => response.json())
                                    .then(data => {{
                                        const refactoring = data['refactoring'];
                                        const refactoringElement = document.createElement('p');
                                        refactoringElement.textContent = refactoring;
                                        responseContainer.innerHTML = '<h1>=====================================<br>면접관 G씨의 답변 입니다.</h1>';
                                        responseContainer.appendChild(refactoringElement);
                                        
                                    }})
                                    .catch(error => console.error('Error:', error));
                            }}
                        }})
                        .catch(error => console.error('Error:', error));
                }}
            }}

            function submitUserAnswer() {{
                const userAnswer = document.getElementById('user-answer-input').value;
                const responseContainer = document.getElementById('response-container');
                const keywordText = responseContainer.querySelector('p').textContent;
                fetch('/submit-answer', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        Question: '{question}',
                        keyword: keywordText,
                        user_answer: userAnswer
                    }})
                }})
                .then(response => response.json())
                .then(data => {{
                    console.log(data.message);
                    getNextResponse();
                }})
                .catch(error => console.error('Error:', error));
            }}
        </script>
    </head>
    <body>
        <div id="container">
            <h1>분석 카테고리</h1>
            <p>항목 : {question}</p>
            <p>키워드 : {keywords}</p>
            <h1>제시된 키워드에 대한 답변(경험)을 적어주세요</h1>
            <div id="response-container">
                {response_html}
            </div>
            {next_button}
        </div>
    </body>
    </html>
        '''


@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.json
    question = data['Question']
    user_answer = data['user_answer']
    recommend_keyword = data['keyword']
    entry = UserAnswer(Question=question, user_answer=user_answer, keyword=recommend_keyword)
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'User answer submitted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
