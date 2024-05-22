from flask import request, jsonify
from sqlalchemy import func
from Temp import db, ChatbotResponse, UserInput, UserAnswer, app
from ChatBot import get_response, get_refactoring

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
            <h1>자소서 항목, 키워드</h1>
            <form action="/submit" method="post">
                <p><input type="text" name="question" placeholder="자소서 항목"></p>
                <p><textarea name="keywords" placeholder="keywords"></textarea></p>
                <p><input type="submit" value="제출"></p>
            </form>
            <div id="response-container"></div>
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
    next_response = ChatbotResponse.query.filter_by(keywordID=keyword_id+1, QuestionID=question_id).first()
    if next_response:
        return jsonify({'response': next_response.response})
    else:
        return jsonify({'response': 'No more responses'})

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
        <!doctype html>
        <html>
        <head>
            <title>입력 결과</title>
            <script>
                let keywordId = 1;
                const question_id = {question_id};

                function getNextResponse() {{
                    const currentKeyword = document.getElementById('keyword-' + keywordId);
                    currentKeyword.style.display = 'none'; // 현재 키워드 숨기기
                    keywordId++;
                    fetch(`/get_response/${{question_id}}/${{keywordId}}`)
                        .then(response => response.json())
                        .then(data => {{
                            const responseContainer = document.getElementById('response-container');
                            responseContainer.innerHTML = ''; // Clear previous responses
                            if (data.response !== 'No more responses') {{
                                responseContainer.innerHTML += `<div id="keyword-${{keywordId}}">`;
                                responseContainer.innerHTML += `<p>${{data.response}}</p>`;
                                responseContainer.innerHTML += '<div id="user-answer-container">';
                                responseContainer.innerHTML += '<input type="text" id="user-answer-input" placeholder="사용자 답변">';
                                responseContainer.innerHTML += '<button onclick="submitUserAnswer()">확인</button>';
                                responseContainer.innerHTML += '</div>';
                                responseContainer.innerHTML += '</div>';
                                // Show the next button
                                document.getElementById('next-button').style.display = 'block';
                            }} else {{
                                responseContainer.innerHTML += '<p>No more responses</p>';
                                document.getElementById('next-button').style.display = 'none'; // 다음 버튼 숨기기
                                
                                // 여기에 추가
                                fetch(`/get_refactoring/{question}`)
                                    .then(response => response.json())
                                    .then(data => {{
                                        const refactoring = data['refactoring']; // 서버에서 받은 JSON 데이터에서 refactoring 필드를 가져옴
                                        const refactoringElement = document.createElement('p'); // 새로운 p 요소 생성
                                        refactoringElement.textContent = refactoring; // p 요소에 refactoring 내용을 설정
                                        responseContainer.appendChild(refactoringElement); // 화면에 p 요소 추가
                                    }})
                                    .catch(error => console.error('Error:', error));
                                                        }}
                                                    }})
                        .catch(error => console.error('Error:', error));
                }}
                
                function stripTags(html) {{
                const doc = new DOMParser().parseFromString(html, 'text/html');
                return doc.body.textContent || "";
                }}

                function submitUserAnswer() {{
                    const userAnswer = document.getElementById('user-answer-input').value;
                    const keywordHtml = document.getElementById('response-container').innerHTML;
                    const keywordText = stripTags(keywordHtml); 
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
            <h1>제출된 텍스트</h1>
            <p>항목 : {question}</p>
            <p>키워드 : {keywords}</p>
            <h1>ChatBot 응답</h1>
            <div id="response-container">
                {response_html}
            </div>
            {next_button}
            <script>
                getNextResponse();
            </script>
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
