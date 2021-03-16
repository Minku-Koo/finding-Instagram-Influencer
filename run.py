"""
Project Name : Finding Instagram Influencer Program
Create Date : 20/May/2020
Update Date : 15/Mar/2021
Author : Minkuk Koo
E-Mail : corleone@kakao.com
Version : 1.2.1
Keyword : 'selenium', 'crawling', 'Flask' ,'BeautifulSoup', 'Instagram', 'Influencer'

* Please, Input your personal Instagram email and password
"""

from insta_crawler import instaCrawl
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
from flask import Flask, redirect, url_for, request, render_template, session
import pymysql
import os, csv, pymysql
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'd0n-t/lo0ok6a+4/cK_1nA2ger'

"""
MariaDB database information
db name : insta_data

CREATE TABLE search_condition(
    no int AUTO_INCREMENT,
    hashtag varchar(50) NOT NULL,
    post bigint(8) NOT NULL,
    follower bigint(11) NOT NULL,
    keyword varchar(15) ,
    keyword_num bigint(4) ,
    PRIMARY KEY (NO)
);

CREATE TABLE influencer_<NUMBER>(
    no int AUTO_INCREMENT,
    name varchar(30) NOT NULL,
    post bigint(8) NOT NULL,
    follower bigint(11) NOT NULL,
    PRIMARY KEY (NO)
);
"""

# get Database object
def getDatabase():
    db = pymysql.connect(
                        host="localhost", 
                        user="root", 
                        passwd="rnalsrn12", #your Password
                        database="insta_data",
                        port = 3306
                        )
    return db

#인플루언서 검색 결과 저장 함수 
def createTable(num):
    """
    Parameters
        num <int> : Table number
    
    returns
        'influencer_'+num <string> : Database Table name
    """
    
    db = getDatabase()
    cursor = db.cursor()
    # 이름, 팔로워 수, 게시글 수 저장할 테이블
    cursor.execute( """CREATE TABLE %s (
                        no int AUTO_INCREMENT,
                        name varchar(30) NOT NULL,
                        post bigint(8) NOT NULL,
                        follower bigint(11) NOT NULL,
                        PRIMARY KEY (NO) );
                    """ %('influencer_'+num))
    db.commit()
    cursor.close()
    return 'influencer_'+num

#그냥 메인 url 함수
@app.route('/')
def index():
    return render_template('index.html', success='')

# csv file create
def create_csv(dir_name, file_name, data):
    with open(dir_name+"/"+file_name+".csv", "w", newline="" ) as f:
        wr = csv.writer(f)
        wr.writerow(["이름", "게시글 수", "팔로워 수"])
        for dic in data: wr.writerow( [dic[1], dic[2], dic[3]] )


# create directory 
#바탕화면에 폴더 생성
def create_dir(dirpath):
    # 최대 20개 폴더 생성 가능
    for n in range(1,20):
        #이미 같은 이름의 폴더가 있으면, 숫자만 달리해서 새로운 폴더 생성
        try:
            if not( os.path.isdir(dirpath) ):
                os.makedirs(os.path.join(dirpath))
                break
            else: 
                dirpath= dirpath.split("(")[0]+"("+str(n)+")"
            
        except(OSError):
            print("Failed to create directory!!!")
            return 0
    return 1

#크롤링 시작 함수
@app.route('/crawl', methods=['POST'])
def insta_crawling():
    #웹에서 입력 받기
    post_num = request.form['post_num'] #게시글 개수
    follower_num = request.form['follower_num'] #팔로워 수
    keyword = request.form['keyword'] #포함 키워드
    keyword_num = request.form['keyword_num'] #포함 키워드 개수
    hash =[] # 해시 태그
    for i in range(5):
        try:
            hash.append(request.form['hash'+str(i+1)])
        except(KeyError): #해시태그 입력이 5개 미만
            break
    
    #입력 오류 검사 -> 기본값 설정
    if post_num == "": post_num = 1
    if follower_num == "": follower_num = 10
    if keyword =="": keyword_num = 0
    if keyword_num =="": keyword_num = 1
    
    #해시태그 리스트에서 공백 모두 제거
    for _ in range(hash.count("")): hash.remove("")
        
    if len(hash) >5:  #해시태그 최대 입력값 초과 시
        print("해시태그는 최대 5개까지 입니다.")
        return "<script>alert('해시태그는 최대 5개까지 입니다.');\
        window.location.replace('/');</script>"
    if len(hash) <1: #해시태그 하나도 포함되지 않을 시
        print("해시태그는 하나 이상 포함되어있어야 합니다.")
        return "<script>alert('해시태그는 하나 이상 포함되어있어야 합니다.');\
        window.location.replace('/');</script>"
   
    #해시태그 합치기
    hash_db=""
    for h in hash: hash_db = hash_db+"#"+h
    
    #조건값 입력
    db = getDatabase()
    cursor = db.cursor()
    
    cursor.execute("""INSERT INTO search_condition (hashtag, post, follower, 
                keyword, keyword_num) VALUES ("%s", "%s", "%s", "%s", "%s")
                """%(hash_db, post_num, follower_num, keyword, keyword_num))
    
    #조건 입력한 auto increment 값 불러와서 테이블 생성
    cursor.execute("""SELECT AUTO_INCREMENT FROM information_schema.tables
                WHERE table_name = 'search_condition' 
                AND table_schema = DATABASE() ;""")
    table_num = str( int( cursor.fetchone()[0] ) - 1 )
    tablename = createTable(table_num)  #테이블 생성
    
    #클래스 생성
    insta = instaCrawl(   hash, 
                        keyword, 
                        int(keyword_num),
                        int(follower_num),
                        int(post_num)
                    )
    result = insta.crawler() # result is dictionary, save crawling result
    
    #DB에 검색 결과 입력
    for name in result.keys():
        cursor.execute("""INSERT INTO %s (name, post,follower ) VALUES 
                ("%s", "%s", "%s")"""%(tablename, name, result[name][1], result[name][0]))
    
    
    #바탕화면에 폴더 생성
    dir_name = str(Path.home())+"\Desktop\Insta_Influencer_File"
    
    create_dir_result = create_dir(dir_name)
    if create_dir_result == 0: # result directory cannot save
        fail = ["폴더를 더이상 생성할 수 없습니다.", "결과 생성 폴더는 최대 20개까지 가능합니다."]
        return render_template('index.html', success=fail)
    
    
    #생성한 폴더에 결과값 파일 생성
    with open(dir_name+"\insta_influencer_list.csv", 'w', newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["이름", "게시글 수", "팔로워 수"])
        for dic in result.keys():
            wr.writerow( [dic, result[dic][0], result[dic][1]] )
    
    #게시글 기준 내림차순 정렬
    cursor.execute( "SELECT * FROM %s ORDER BY post DESC" %tablename )
    create_csv(dir_name, "insta_influencer_by_post", cursor.fetchall())
    
    #팔로워 기준 내림차순 정렬
    cursor.execute( "SELECT * FROM %s ORDER BY follower DESC" %tablename )
    create_csv(dir_name, "insta_influencer_by_follower", cursor.fetchall() ) # db_data)
    
    db.commit()
    cursor.close()
    db.close()
    #검색 완료 시, 결과 문구 전송
    success =['검색이 완료되었습니다.', "바탕화면 'Insta_Influencer_File'폴더에서 결과 파일을 확인하세요."]
    return render_template('index.html', success=success)

if __name__ == '__main__':
    app.debug = True
    app.run(host = "127.0.0.1",  port =5000)
    app.run(debug = True)
    