import json
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
from app import OPENAI_API_KEY
from app import Crawlings
from app import db
from app import app
##

client = OpenAI(api_key=OPENAI_API_KEY)
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def save_embedding(vector, urlinput):
    # embedding 벡터를 JSON 문자열로 변환
    json_vector = json.dumps(vector)
    # 데이터베이스 객체 생성
    embedding_entry = Crawlings(QuestionVector=json_vector, URL=urlinput)
    db.session.add(embedding_entry)
    db.session.commit()

with app.app_context():
    for number in range(11743, 21743):    # 현재 11743 ~ 33002 까지의 자소서 존재 -> 요청 응답 없으면 건너뜀

        url = 'https://linkareer.com/cover-letter/%d?page=1&sort=PASSED_AT&tab=all' % number

        # 웹페이지에 요청을 보내고 응답을 받음
        response = requests.get(url)

        # 응답의 상태코드를 확인하여 요청이 실패했을 경우에는 건너뜁니다.
        if response.status_code != 200:
            print("요청이 실패하였습니다. 상태코드:", response.status_code)
            continue

        # 응답의 HTML 소스를 파싱하여 BeautifulSoup 객체 생성
        soup = BeautifulSoup(response.text, "html.parser")

        # class가 jss1340인 main 태그 확인
        main_tag = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)

        # 텍스트 추출
        crawled_text = main_tag["props"]["pageProps"]["data"]["coverLetterWithHighlight"]["coverLetter"]["content"]

        #print(crawled_text)
       # print()
        #print(number)
        # database 연동 필요 get_embedding(crawled_text)-> url mapping
        embed = get_embedding(crawled_text)
        print(embed)
        save_embedding(embed, url)





