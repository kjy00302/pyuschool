import requests
import bs4
import re


class Uschool():
    def __init__(self):
        self.websession = requests.session()
        self.SESSION = None
        self.classes = None

    def login(self, id, password):
        self.websession.post('https://uschool.uplus.co.kr/member/login/', params={'id':id, 'password':password})
        self.SESSION = self.websession.cookies.get('SESSION')
    
    def sessionlogin(self, session):
        self.SESSION = session
        self.websession.cookies.set('SESSION', session)
    
    def classcrawler(self):
        if self.SESSION == None:
            raise Exception
        classes = []
        isdone = False
        page = 0
        while not isdone:
            soup = bs4.BeautifulSoup(self.websession.get('https://uschool.uplus.co.kr/course/?page=%d' % page).text, "lxml")
            extraction = soup.findAll('td', attrs={'class':None})
            if (extraction != []):
                classes.extend(extraction)
                page += 1
            else:
                isdone = True
        return classes

    @classmethod
    def prettierclass(self, classes):
        prettified = []
        for lesson in classes:
            lesson_name = lesson.find('a', attrs={'class':'title-course -as-popup'}).text.strip()
            lesson_code = lesson.find('i').attrs['data-no']
            tutor = lesson.find('span', attrs={'class':'teacher-name'}).text.split(':')[1].strip()
            persons = re.findall('\d+', lesson.find('span', attrs={'class':'num-persons'}).text)
            max_persons = persons[0]
            applied_persons = persons[1]
            queued_persons = persons[2]
            fees = re.findall('\d+', lesson.find('span', attrs={'class':'teacher-fees'}).text)
            lesson_fees = fees[0]
            textbook_fees = fees[1]
            prettified.append({
                '강좌명': lesson_name,
                '강좌코드': int(lesson_code),
                '강사명': tutor,
                '정원': int(max_persons),
                '신청인원': int(applied_persons),
                '대기인원': int(queued_persons),
                '수강료': int(lesson_fees),
                '교재비': int(textbook_fees)
                })
        return prettified

    def update(self):
        self.classes = self.prettierclass(self.classcrawler())

    def apply_lesson(self, lesson_code):
        status = self.websession.get('https://uschool.uplus.co.kr/course/%d/apply.popup' % lesson_code)
        if (status.text.find('정상적으로 완료') != -1):
            pass
        elif (status.text.find('이미 수강신청 한 강좌입니다') != -1):
            raise Warning('이미 수강신청 한 강좌입니다')
        elif (status.text.find('수강신청 기간이 아닙니다') != -1):
            raise Warning('아직 수강신청 기간이 아닙니다')
        elif (status.text.find('동일한 시간대의 다른 강좌를 신청하셨습니다') != -1):
            raise Exception('동일한 시간대의 다른 강좌를 신청하셨습니다')
        elif (status.text.find('아이디를 입력해주세요') != -1):
            raise Exception('로그인이 필요합니다')
        else:
            print(status.text)
            raise Exception('알수없는 오류. 위의 출력을 참조하시오')
