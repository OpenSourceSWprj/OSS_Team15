import requests
from bs4 import BeautifulSoup

# 크롤링할 웹 페이지의 URL
url = 'https://www.example.com'

# 웹 페이지에 GET 요청 보내기
response = requests.get(url)

# 요청이 성공했는지 확인
if response.status_code == 200:
    # HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 제목 추출
    title = soup.title.text
    
    # 결과 출력
    print("웹 페이지 제목:", title)
else:
    print("요청 실패:", response.status_code)
