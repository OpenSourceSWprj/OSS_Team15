import json
import requests
from bs4 import BeautifulSoup

url = "https://linkareer.com/cover-letter/33171?page=1&sort=PASSED_AT&tab=all"

# 웹페이지에 요청을 보내고 응답을 받음
response = requests.get(url)
# 응답의 HTML 소스를 파싱하여 BeautifulSoup 객체 생성
soup = BeautifulSoup(response.text, "html.parser")
# class가 jss1340인 main 태그 확인
main_tag = json.loads(soup.find("script", {"id": "__NEXT_DATA__"}).text)
print(
    main_tag["props"]["pageProps"]["data"]["coverLetterWithHighlight"]["coverLetter"]["content"]
)

# for page in range(1,643):
#     	Hollys_url = 'https://linkareer.com/cover-letter/33171?page=%d&sort=PASSED_AT&tab=all' %page
