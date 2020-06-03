# python
# finding instagram influencer program
# crawler
# project start 2020.05.20
# made by Koo Minku
# developer E-mail : corleone@kakao.com

import requests
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
import selenium
import requests
from selenium.webdriver.support.ui import WebDriverWait
import time
import re


class crawling:
    def __init__(self, hash_post,keyword_post,hash_all_n,follower_over,post_over):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('lang=ko_KR')
        
        # selenium 크롤링을 위한 크롬 드라이버 생성
        self.driver = webdriver.Chrome('./crawler/drivers/chromedriver.exe', chrome_options=self.options)
        #self.driver = webdriver.Chrome('./crawler/drivers/chromedriver.exe')
        self.driver.implicitly_wait(3)
        print("crawling start")
        
        self.hash_post = hash_post
        self.keyword_post = keyword_post
        self.hash_all_n = hash_all_n
        self.follower_over = follower_over
        self.post_over = post_over
        
        # 해시태그를 통한 URL 리스트 생성
        self.urlList = []
        for hash in self.hash_post:
            self.urlList.append("https://www.instagram.com/explore/tags/"+hash+"/?hl=ko")
        
        # 최종 결과 입력을 위한 클래스 변수
        self.follower = 0
        self.post = 0
        #로그인이 안될 경우, 로그인을 위한 이메일과 비밀번호 정보
        self.my_account = ['koomk97@hanmail.net', 'koomk1204?', 1]
        
        pass
        
    def main(self):
        indx= self.hash_low()  # 게시글 개수가 제일 적은 index 정보
        
        print("index is ",indx)
        #제일 적은 게시글의 링크로 크롤링
        link = self.urlList[indx]
        self.driver.get(link)
        self.driver.implicitly_wait(10)
        time.sleep(3)
        
        hrefList = []
        temp = ""
        
        for i in range(2000):
            # 동적 HTML 크롤링, javascript로 생성된 HTML을 불러옴
            soup = BeautifulSoup(self.driver.page_source)
            a_tagList = soup.findAll("a") #모든 a 태그 찾아냄
            
            # 끝까지 가거나 or 로딩이 안되는 경우, 종료
            if temp == a_tagList:
                print("over")
                break
            temp = a_tagList
            
            for a_tag in a_tagList:
                if "href" in a_tag.attrs: # a 태그에 있는 모든 href 정보 불러옴(게시글 링크)
                    hrefList.append(a_tag.attrs['href'])
                    print(a_tag.attrs['href'])
            # 스크롤 맨아래로 - 새로운 HTML 생성
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print("stop")
            self.driver.implicitly_wait(10)
            time.sleep(0.7)
            
        # URL 중복 제거
        hrefList = list(set(hrefList))
        lenUrl = len(hrefList)
        print(lenUrl)
        time.sleep(2)
        nb = 0
        nameList =[] #게시글 포함하는 사용자 리스트 입력
        for link in hrefList: #링크 하나씩 읽어들임 - by postInfo()
            result = self.postInfo(link)
            if result != 0: #이름 return한 경우
                nameList.append(result) #이름 리스트 추가
            print(str(nb)+' / '+str(lenUrl)) #진행상황 cmd에 출력
            nb+=1
            
        nameList = list(set(nameList)) #이름 중복 제거
        print("---nameList---")
        print(nameList)
        
        self.driver.get("http://www.instagram.com/")
        self.driver.implicitly_wait(10)
        print("go to home..")
        time.sleep(1)
        
        #게시글 수, 팔로워 수 만족하는 인플루언서 리스트
        nameResultDic ={}
        for name in nameList:
            print("name :: ",name)
            name_result = self.influencerInfo(name)
            if name_result == 100: #조건 만족할 경우, 이름을 key / 팔로워와 게시글수를 value로 입력
                nameResultDic[name] = [self.follower, self.post]
        
        print("-------- nameResultDic----------")
        print(nameResultDic)
        
        #인플루언서 리스트 게시글 정보 확인하기
        #게시글에 해시태그 몇개 포함되어있는지 확인
        influencer = {}
        if self.keyword_post == '': #키워드가 없으면 그대로 반환
            return nameResultDic
        for name in nameResultDic.keys():
            #입력한 포함 개수보다 많을 경우
            if self.hash_all_n <= self.influencer_post_hash(name, self.hash_all_n):
                print("You r real influencer..!!\n")
                influencer[name] = nameResultDic[name]
        return influencer
    
    
    def hash_low(self): #해시태그 게시글 제일 적은거 찾기
        print("hash_low")
        #해시태그 게시글 갯수 pageCount 리스트에 추가
        pageCount = []
        for link in self.urlList:
            self.driver.get(link)
            self.driver.implicitly_wait(3) # 로딩까지 3초 기다리기
            #게시글 개수 표시된 tag
            count = self.driver.find_element_by_xpath('//*[@id="react-root"]/\
            section/main/header/div[2]/div[1]/div[2]/span/span').text
            
            count = count.replace(',', '')
            pageCount.append(int(count))
            
        return pageCount.index(min(pageCount)) #가장 적은 값의 인덱스 반환
        
        
    def postInfo(self, link):
        #이름은 h2 tag
        #혹은 header 안에 있는 a 태그
        post_re = re.compile('/p/.*') #게시글 링크 조건
        if post_re.match(link) == None: #정규표현식과 일치하지 않을때 = 게시글 링크 아닐 경우
            return 0
        
        self.driver.get("http://www.instagram.com"+link)
        self.driver.implicitly_wait(4)
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            name = bs.find("h2").get_text() #사용자 이름
            content = bs.find("li", role="menuitem").get_text() #게시글 내용
            print("name : ", name)
            print("content : ", content)
            
            #게시글 내용 + 본인 작성 댓글 문자열로 합치기
            strList = content + self.hash_inPost(bs, name)
            #해시태그가 게시글에 포함된 경우 찾기
            for word in self.hash_post: 
                if word not in strList: #해시태그가 하나라도 포함 안된 경우 종료
                    return 0
            print("해시태그가 모두 포함된 게시글이라니 대단한걸")
            return name #해시태그 모두 포함될 경우 이름 리턴
            
        except(AttributeError):
            return 0
        except(OSError):
            return 0
        
        print("not include")
        return 0 # 키워드 포함 안될 경우
    
    #게시글 팔로우 확인
    def influencerInfo(self, name):
        url = "https://www.instagram.com/"+name+"/?hl=ko"
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        time.sleep(0.5)
        
        #로그인 페이지 뜰 경우
        if "instagram.com/accounts/login/" in self.driver.current_url :
            #로그인 함수
            self.insta_login()
        
        time.sleep(2)
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            header = bs.find("ul") #인플루언서 정보 부분 - 게시물 팔로워 팔로우
            li = bs.find_all("li")
            
            korean = re.compile("[가-힣]")
            post_num = li[0].get_text()
            post_num = korean.sub('', post_num) #한국어 제거
            post_num = post_num.replace(',', '').replace(' ', '') #특수문자 제거
            print(post_num+" 개의 게시글")
            
            follower = str(li[1].find("span")['title']).replace(',', '')
            print("팔로워 : "+follower)
            
            #게시글 수와 팔로워 수 조건 만족 경우
            if int(post_num) >= self.post_over and int(follower) >= self.follower_over :
                print("You are influencer")
                print(name)
                #딕셔너리 입력을 위한 클래스 변수에 입력
                self.post = post_num
                self.follower = follower
                return 100 # 게시글 팔로워 조건 만족하는 경우
                
        except(AttributeError):
            print("어딘가 에러")
            return 0
        except(KeyError):
            print("no title value")
            return 0
        except(TypeError):
            print("TypeError")
            return 0

    #게시글 본인 댓글 불러오기
    def hash_inPost(self, bs, user_name):
        result = '' #본인 작성 댓글 있으면, 문자열로 합쳐서 반환
        #더보기 클릭
        for span_name in self.driver.find_elements_by_tag_name("span"):
            try:
                if span_name.get_attribute("aria-label") != None and \
                "Load more" in span_name.get_attribute("aria-label"):
                    span_name.click()
                    print("더보기 클릭")
                    time.sleep(0.6)
                    break
            except(selenium.common.exceptions.StaleElementReferenceException):
                print("i dont know err")
        #답글 클릭
        try:
            for btn_name in self.driver.find_elements_by_tag_name("button"):
                if "(1개)" in btn_name.text :
                    print("CLICKKKK")
                    btn_name.click()
        except(selenium.common.exceptions.StaleElementReferenceException):
            print("the error")
                
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        ul_view = bs.find_all("ul")
        ran = 0
        comment_view = ul_view
        for ul in ul_view:
            comment_view = ul
            #a 태그를 제거했을 때, 아무것도 없으면 댓글화면이 아님
            for a in ul.select('a'):
                a.extract()
            if ul.get_text() != "" or ul.get_text() == None: #댓글화면일 경우
                bs = BeautifulSoup(self.driver.page_source, 'html.parser')
                comment_view = bs.find_all("ul")[ran]
                break
            ran +=1
        result=''
        for comment in comment_view.find_all("li"): # li태그가 모든 댓글, comment = 본인 댓글창
            
            #작성자 본인이 쓴 댓글 - 해시태그 있음
            if comment.find("h3") != None and comment.find("h3").get_text() == user_name: #본인 댓글일 경우
                comment_hash = comment.find_all("a") #본인 댓글의 모든 해시태그 읽어들임
                print("---본인 작성 댓글 있다 ---")
                for a in comment_hash: #해시태그 전부 긁어와서 result에 추가
                    result += a.get_text()
                    print("나는 본인작성 댓글의 해시태그")
        return result #본인작성댓글 문자열로 반환
            
        return '' #본인 작성 댓글 없음
    
    #인플루언서 게시글 안에 해시태그 몇개 포함되어있는지 확인하기
    def influencer_post_hash(self, name, hash_number):
        if self.keyword_post == '':
            print("키워드 없다")
            return 9999
        
        url = "https://www.instagram.com/"+name+"/?hl=ko"
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        
        post_re = re.compile('/p/.*')
        linkList , temp= [], ''
        print("a tag print\n\n")
        #인플루언서 게시글 링크 모두 수집
        for i in range(1000):
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            a_tag = bs.findAll("a")
            if temp == a_tag:
                print("over")
                break
            temp = a_tag
            
            for link in a_tag:
                # a 태그에 있는 모든 href 정보 불러옴 and 게시글 링크인 경우
                if "href" in link.attrs and post_re.match(link.attrs['href']) != None: 
                    linkList.append(link.attrs['href'])
            
            #스크롤 맨아래로
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.implicitly_wait(10)
            time.sleep(1.5)
            
        #게시글 중복 제거
        linkList = list(set(linkList))
        
        #게시글에 포함된 키워드 확인
        hash_count =0
        non_post = []
        for link in linkList: #게시글 전부 탐색
            self.driver.get("https://www.instagram.com"+link+"?hl=ko")
            self.driver.implicitly_wait(10)
            
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            comment_view = bs.find("ul") #게시글+댓글 창
            try:
                content = bs.find("li", role="menuitem").get_text() #게시글 내용
            except(AttributeError):
                continue
            
            if self.keyword_post in content+self.hash_inPost(bs, name):
                print("키워드가 게시글 내용에 포함")
                hash_count += 1
                
            if hash_count >= hash_number: #입력한 개수 이상일 경우
                print("게시글에 해시태그 다있음-- 성공이야")
                print("해시태그 개수 =>> ",hash_count)
                return hash_count
                
            print("해시태그 개수 : ",hash_count)
            non_post.append(hash_count)
            # 게시글 80% 이상을 읽을때까지 포함된 키워드가 하나도 없을 경우 -> 키워드와 관련 없는 인플루언서로 판단
            if int(len(linkList)*0.8) < len(non_post) and len(set(non_post)) =={0}:
                print("90% 이상 게시글이 해시태그 포함하지 않음")
                return 0
        return hash_count
            
    #인스타그램 로그인
    def insta_login(self):
        print("login function start")
        
        id = self.my_account[0]
        pw = self.my_account[1]
        facebook = self.my_account[2]
        
        
        if facebook == 1: #페이스북으로 로그인한 경우
            print("facebook login")
            login_form = self.driver.find_element_by_tag_name("form")
            login_form.find_elements_by_tag_name("button")[1].click()
            self.driver.implicitly_wait(10)
            time.sleep(1)
            id_input = self.driver.find_element_by_id("email")
            pw_input = self.driver.find_element_by_id("pass")
            
            id_input.send_keys(id)
            pw_input.send_keys(pw)
            
            self.driver.find_element_by_id("loginbutton").click()
            
            
        else: #인스타그램 계정 따로 회원가입한 경우
            print("instagram login")
            login = self.driver.find_element_by_tag_name('input')
            id_input = login.find_element_by_name("username")
            pw_input = login.find_element_by_name("password")
            
            id_input.send_keys(id)
            pw_input.send_keys(pw)
            
            self.driver.find_element_by_tag_name("button").click()
        
        self.driver.implicitly_wait(10)
        time.sleep(3)
        return 0
        
        
        
