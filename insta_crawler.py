
"""
Project Name : Finding Instagram Influencer
Create Date : 20/May/2020
Update Date : 15/Mar/2021
Author : Minkuk Koo
E-Mail : corleone@kakao.com
Version : 1.2.1

* Please, Input your personal Instagram email and password
"""

import requests
from bs4 import BeautifulSoup
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
import selenium, time, re
from selenium.webdriver.support.ui import WebDriverWait

class instaCrawl:
    def __init__(self, 
                hash_post,
                keyword_post,
                keyword_include_count,
                follower_over,
                post_over):
        """
        Parameters
            hash_post <str in list> : is hash tag in post?
            keyword_post <str> : is keyword in post?
            keyword_include_count <int> : how many keyword in posts
            follower_over <int> : followers count
            post_over <int> : posts count
        
        """
        self.hash_post = hash_post
        self.keyword_post = keyword_post
        self.keyword_include_count = keyword_include_count
        self.follower_over = follower_over
        self.post_over = post_over
        
        # 최종 결과 입력을 위한 클래스 변수
        self.follower = 0
        self.post = 0
        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('lang=ko_KR')
        
        # selenium 크롤링을 위한 크롬 드라이버 생성
        self.driver = webdriver.Chrome(
                                './crawler/drivers/chromedriver.exe', 
                                chrome_options=self.options
                                )
        self.driver.implicitly_wait(3)
        
        # 해시태그를 통한 URL 리스트 생성
        self.urlList = []
        for hash in self.hash_post:
            self.urlList.append("https://www.instagram.com/explore/tags/"+hash+"/?hl=ko")
        
        
        #로그인이 안될 경우, 로그인을 위한 이메일과 비밀번호 정보/ 1이면 facebook, 0이면 instagram 계정
        # for login
        # 1 : facebook account
        # 2 : instagram account
        self.__myAccount = ['your email', 'your password', 1]
        
    
    def crawler(self):
        # if page cannot load -> time delay and reload
        def time_delay(soup, delay):
            time.sleep(delay)
            a_tag_list = soup.findAll("a")
            return a_tag_list
            
        indx= self.__get_min_post()  # 게시글 개수가 제일 적은 index 정보
        
        #제일 적은 게시글의 링크로 크롤링
        link = self.urlList[indx]
        self.driver.get(link)
        self.driver.implicitly_wait(10)
        time.sleep(2)
        
        post_list = [] # hashtag post link
        temp = ""
        
        for i in range(2000): # max scroll times = 2000
            # dynamin HTML Page crawling, call HTML made by Javascript
            soup = BeautifulSoup(self.driver.page_source)
            a_tag_list = soup.findAll("a") # find all <a> tag
            
            # 끝까지 가거나 or 로딩이 안되는 경우, 종료
            if temp == a_tag_list: 
                a_tag_list = time_delay(soup, 2)
                if temp == a_tag_list: 
                    a_tag_list = time_delay(soup, 1)
                    if temp == a_tag_list:
                        print("Program over..")
                        break
                        
            temp = a_tag_list
            
            # scroll to Bottom, load new post
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.implicitly_wait(10)
            time.sleep(1)
        
            for a_tag in a_tag_list:
                if "href" in a_tag.attrs: # a 태그에 있는 모든 href 정보 불러옴(게시글 링크)
                    post_list.append( a_tag.attrs['href'] )
        
        # URL 중복 제거
        post_list = list(set(post_list))
        
        url_count = len(post_list)
        time.sleep(1)
        
        post_number = 0 # for process percent
        nameList =[] # 수집한 포스트 링크의 모든 user 
        
        for link in post_list: #링크 하나씩 읽어들임 - by __getPostName()
            post_name = self.__getPostName(link)
            if post_name != 0: # if user name return
                nameList.append(post_name)
                
            print(str(post_number)+' / '+str(url_count)) # print process on cmd
            post_number+=1 
            
        nameList = list(set(nameList)) #이름 중복 제거
        
        self.driver.get("http://www.instagram.com/")
        self.driver.implicitly_wait(10)
        print("go to intagram home..")
        time.sleep(1)
        
        #게시글 수, 팔로워 수 만족하는 인플루언서 리스트
        nameResultDic ={}
        for name in nameList:
            if self.__getUserData(name) == 1: #조건 만족할 경우
                # 이름을 key, 팔로워와 게시글수를 value로 입력
                nameResultDic[name] = [self.follower, self.post]
        
        #인플루언서 리스트 게시글 정보 확인하기
        #게시글에 키워드 몇개 포함되어있는지 확인
        if self.keyword_post == '': # 포함해야할 키워드가 없으면 그대로 반환
            return nameResultDic
            
        influencer = {} # 키워드 검사 변수
        for name in nameResultDic.keys():
            #입력한 키워드 포함 개수보다 많을 경우
            if self.keyword_include_count <= self.__getKeywordCount(name, self.keyword_include_count):
                print("You are real influencer..!! >>", name)
                influencer[name] = nameResultDic[name]
                
        return influencer
    
    # find minimun post about hashtag / 해시태그 게시글 제일 적은거 찾기
    def __get_min_post(self): 
        #해시태그 게시글 갯수 pageCount 리스트에 추가
        pageCount = []
        self.driver.get(self.urlList[0])
        print("driver move to :",self.urlList[0])
        self.driver.implicitly_wait(10)
        #로그인 페이지 뜰 경우
        if "instagram.com/accounts/login" in self.driver.current_url :
            #로그인 함수
            self.__insta_login()
            print("로그인 완료")
            self.driver.implicitly_wait(10)
            time.sleep(3)
            print("now url: ",self.driver.current_url)
            if "instagram.com/accounts/login" in self.driver.current_url :
                print("또 어카운트 에러")
                keepGoing_by_myAccount = self.driver.find_elements_by_tag_name("button")[1]
                keepGoing_by_myAccount.click()
                print("어카운트 에러 확인 완료")
            self.driver.implicitly_wait(10)
        time.sleep(1)
        try:
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            dialog_box_class = bs.find("div", role="dialog")['class']
            dialog = self.driver.find_element_by_class_name(dialog_box_class)
            print("다이어로그 클릭")
            dialog.click()
            self.driver.implicitly_wait(10)
        except:
            print("문제 없음")
            pass
        
        for link in self.urlList:
            self.driver.get(link)
            print("driver move to 2 :",self.urlList[0])
            self.driver.implicitly_wait(10) 
            #게시글 개수 표시된 tag
            print("get min post 에러")
            post_count_xpath = '//*[@id="react-root"]/section/main/header/div[2]/div/div[2]/span/span'
            count = self.driver.find_element_by_xpath(post_count_xpath).text
            
            count = count.replace(',', '')
            pageCount.append(int(count))
            
        return pageCount.index(min(pageCount)) #가장 적은 값의 인덱스 반환
        
    #check hashtag in post
    def __getPostName(self, link):
        """
        Parameters
            link <str> : post link
        
        returns
            name <str> : user name if hash tag in post
            0 <int> : hash tag not in post
        """
        post_condition = re.compile('/p/.*') # post url condition
        if post_condition.match(link) == None: #정규표현식과 일치하지 않을때 = 게시글 링크 아닐 경우
            return 0
        
        self.driver.get("http://www.instagram.com"+link)
        self.driver.implicitly_wait(5)
        time.sleep(0.2)
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        try:
            name = bs.find("h2").get_text() # user name
            content = bs.find("li", role="menuitem").get_text() # post content
            
            #게시글 내용 + 본인 작성 댓글 -> 문자열로 합치기
            post_content = content + self.get_hash_in_post( name)
            #해시태그가 게시글에 포함된 경우 찾기
            for word in self.hash_post: 
                if word not in post_content: #해시태그가 하나라도 포함 안된 경우 종료
                    return 0
            print("All Hashtag in Post")
            return name # 해시태그 모두 포함될 경우 이름 리턴
            
        except :
            return 0
        
        print("hashtag not include")
        return 0 # 키워드 포함 안될 경우
    
    # check users followers number
    def __getUserData(self, name):
        url = "https://www.instagram.com/"+name+"/?hl=ko"
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        time.sleep(0.5)
        
        # if load Login page
        if "instagram.com/accounts/login/" in self.driver.current_url :
            # go login
            self.__insta_login()
        
        time.sleep(1)
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        try:
            li = bs.find_all("li")
            korean = re.compile("[가-힣]")
            
            post_num = li[0].get_text()
            post_num = korean.sub('', post_num) # remove koream
            post_num = post_num.replace(',', '').replace(' ', '') # remove  special character
            
            follower = str(li[1].find("span")['title']).replace(',', '') # get followers number
            
            #게시글 수와 팔로워 수 조건 만족 경우
            if int(post_num) >= self.post_over and int(follower) >= self.follower_over :
                
                #딕셔너리 입력을 위한 클래스 변수에 입력
                self.post = post_num
                self.follower = follower
                return 1 # 게시글 팔로워 조건 만족하는 경우
                
        
        except(KeyError):
            print("No title value")
            return 0
        except(TypeError):
            print("TypeError")
            return 0
        except:
            print("Somewhere Error!")
            return 0

    # 게시글 내용 + 본인 작성 댓글 불러오기
    def __get_all_post_content(self, user_name):
        """
        Parameters
            user_name <str> : user name
        
        returns
            result <str> : post contetn + user comment and reply
        
        """
        
        #본인 작성 댓글 있으면, 문자열로 합쳐서 반환
        result = ''  # 합친 문자열 반환
        
        try: self.driver.find_elements_by_tag_name("span")
        except: time.sleep(1)
        
        #더보기 클릭
        for span_name in self.driver.find_elements_by_tag_name("span"):
            try:
                if span_name.get_attribute("aria-label") != None and \
                "Load more" in span_name.get_attribute("aria-label"):
                    span_name.click() # 댓글 더보기 클릭
                    time.sleep(0.3)
                    break
            except :
                pass
                
        #답글 클릭
        try:
            for btn_name in self.driver.find_elements_by_tag_name("button"):
                if "(1개)" in btn_name.text : # 본인 해시태그 댓글은 대부분 답글이 1개
                    btn_name.click()
        except :
            print("reply click error")
            pass
                
        bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        ul_view = bs.find_all("ul")
        
        index = 0
        comment_view = ul_view
        for ul in ul_view: # 댓글 화면 찾기
            comment_view = ul
            #a 태그를 제거했을 때, 아무것도 없으면 댓글화면이 아님
            for a in ul.select('a'):
                a.extract()
                
            if ul.get_text() != "" or ul.get_text() == None: #댓글화면일 경우
                bs = BeautifulSoup(self.driver.page_source, 'html.parser')
                comment_view = bs.find_all("ul")[index]
                break
            index +=1
            
        result=''
        for comment in comment_view.find_all("li"): #  <li> is comment 
            
            # user comment  and has hashtag
            if comment.find("h3") != None and comment.find("h3").get_text() == user_name: #본인 댓글일 경우
                comment_hash = comment.find_all("a") # get hashtag in user comment
                for hash in comment_hash: # hashtag appent to result
                    result += hash.get_text()
        return result #본인작성댓글 문자열로 반환
            
    #인플루언서 게시글 안에 키워드 몇개 포함되어있는지 확인하기
    # how many keyword in user post
    def __getKeywordCount(self, name, keyword_number):
        """
        Parameters
            name <str> : user name
            keyword_number <int> : keyword count
            
        returns
            keyword_count <int> : keyword count in post
        """
        
        if self.keyword_post == '': # no keyword
            print("No Keyword")
            return 999
        
        url = "https://www.instagram.com/"+name+"/?hl=ko"
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        
        post_re = re.compile('/p/.*')
        linkList , temp= [], ''
        #인플루언서 게시글 링크 모두 수집
        # scrap all post link in user
        for i in range(2000):
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            a_tag = bs.findAll("a")
            if temp == a_tag:
                break
            temp = a_tag
            
            for link in a_tag:
                # 게시글 링크가 맞는 경우
                # a 태그에 있는 모든 href 정보(= link) 불러옴
                if "href" in link.attrs and post_re.match(link.attrs['href']) != None: 
                    linkList.append(link.attrs['href'])
            
            #스크롤 맨아래로
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.driver.implicitly_wait(10)
            time.sleep(1.5)
            
        #게시글 중복 제거
        linkList = list(set(linkList))
        
        #게시글에 포함된 키워드 확인
        keyword_count =0
        no_keyword_post = []
        for link in linkList: #게시글 전부 탐색
            self.driver.get("https://www.instagram.com"+link+"?hl=ko")
            self.driver.implicitly_wait(10)
            
            bs = BeautifulSoup(self.driver.page_source, 'html.parser')
            comment_view = bs.find("ul") #게시글+댓글
            try:
                content = bs.find("li", role="menuitem").get_text() #게시글 내용
            except(AttributeError):
                continue
            
            # if keyword in post
            if self.keyword_post in content+self.__get_all_post_content(name):
                print("Keyword in Post content")
                keyword_count += 1
                
            if keyword_count >= keyword_number: #입력한 개수 이상일 경우
                print("Keyword in post")
                print("키워드 개수 : ",keyword_count)
                return keyword_count
                
            print("키워드 개수 : ",keyword_count)
            no_keyword_post.append(keyword_count)
            # 게시글 80% 이상을 읽을때까지 포함된 키워드가 하나도 없을 경우 -> 키워드와 관련 없는 인플루언서로 판단
            if int(len(linkList)*0.8) < len(no_keyword_post) and len(set(no_keyword_post)) =={0}:
                print("90% 이상 게시글이 해시태그 포함하지 않음")
                return 0
        return keyword_count
            
    #인스타그램 로그인
    def __insta_login(self):
        
        id = self.__myAccount[0] 
        pw = self.__myAccount[1]
        facebook = self.__myAccount[2]
        
        if facebook == 1: # if login by facebook account
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
            
            
        else:  # if login by instagram account
            print("instagram login")
            login = self.driver.find_element_by_tag_name('input')
            id_input = login.find_element_by_name("username")
            pw_input = login.find_element_by_name("password")
            
            id_input.send_keys(id)
            pw_input.send_keys(pw)
            
            self.driver.find_element_by_tag_name("button").click()
        
        self.driver.implicitly_wait(10)
        time.sleep(3)
        
        return 
        
        
        
