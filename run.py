# python
# finding instagram influencer program
# server flask
# project start 2020.05.20
# made by Koo Minku
# developer E-mail : corleone@kakao.com

from insta_crawler import crawling
import re
import requests
from bs4 import BeautifulSoup
import urllib.request
from flask import Flask
from flask import Flask, redirect, url_for, request, render_template, session
import pymysql
import os
import csv
from pathlib import Path
import pymysql

app = Flask(__name__)
app.secret_key = 'd0nt/look6acK_1nA2ger'

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

db = pymysql.connect(
                    host="localhost", 
                    user="root", 
                    passwd="rnalsrn12", #rnalsrn12
                    database="insta_data",
                    port = 3306
                    )

#인플루언서 검색 결과 저장 함수 
def createTable(num):
    cursor = db.cursor()
    # 이름, 팔로워 수, 게시글 수 저장할 테이블
    cursor.execute( """CREATE TABLE %s (
                        no int AUTO_INCREMENT,
                        name varchar(30) NOT NULL,
                        post bigint(8) NOT NULL,
                        follower bigint(11) NOT NULL,
                        PRIMARY KEY (NO)
                    );""" %('influencer_'+num))
    db.commit()
    cursor.close()
    return 'influencer_'+num

#그냥 메인 url 함수
@app.route('/')
def index():
    return render_template('index.html', success='')
    
#크롤링 시작 함수
@app.route('/crawl', methods=['POST'])
def insta_crawlStart():
    print("insta_crawlStart")
    #웹에서 입력 받기
    post_num = request.form['post_num']
    follower_num = request.form['follower_num']
    keyword = request.form['keyword']
    keyword_num = request.form['keyword_num']
    hash =[]
    for i in range(5):
        try:
            hash.append(request.form['hash'+str(i+1)])
        except(KeyError): #해시태그 입력이 5개 미만
            print("hash end : ",i)
            break
    
    #입력 오류 검사
    if post_num == "":
        post_num = 1
    if follower_num == "":
        follower_num = 10
    if keyword =="":
        keyword_num = 0
    if keyword_num =="":
        keyword_num = 1
    for a in range(hash.count('')):
        hash.remove("")
    if len(hash) >5:
        print("해시태그는 최대 5개까지 입니다.")
        return "<script>alert('해시태그는 최대 5개까지 입니다.');\
        window.location.replace('/');</script>"
    if len(hash) <1:
        print("해시태그는 하나 이상 포함되어있어야 합니다.")
        return "<script>alert('해시태그는 하나 이상 포함되어있어야 합니다.');\
        window.location.replace('/');</script>"
    
    print("**"*20)
    print(hash)
    print("post_num : ", post_num)
    print("follower_num : ", follower_num)
    print("keyword : ", keyword)
    print("keyword_num : ", keyword_num)
    
    #해시태그 합치기
    hash_db=""
    for h in hash:
        hash_db = hash_db+"#"+h
    
    #조건값 입력
    cursor = db.cursor()
    cursor.execute("""INSERT INTO search_condition (hashtag, post,follower, 
                keyword, keyword_num) VALUES 
                ("%s", "%s", "%s", "%s", "%s")"""%(hash_db, post_num, follower_num, keyword, keyword_num))
    db.commit()
    #조건 입력한 auto increment 값 불러와서 테이블 생성
    cursor.execute("""SELECT AUTO_INCREMENT FROM information_schema.tables
                WHERE table_name = 'search_condition' 
                AND table_schema = DATABASE() ;""")
    table_num = str(int(cursor.fetchone()[0])-1)
    tablename = createTable(table_num)  #테이블 생성
    
    #클래스 생성
    insta = crawling(hash,keyword,int(keyword_num),int(follower_num),int(post_num))
    result = insta.main() # result는 딕셔너리, 크롤링 결과 저장
    print("----final----")
    print(result)
    
    #DB에 검색 결과 입력
    for name in result.keys():
        cursor.execute("""INSERT INTO %s (name, post,follower ) VALUES 
                ("%s", "%s", "%s")"""%(tablename, name, result[name][1], result[name][0]))
    db.commit()
    
    
    #바탕화면에 폴더 생성
    dir_name = str(Path.home())+"\Desktop\Insta_Influencer_File"
    for n in range(1,20):
        #이미 같은 이름의 폴더가 있으면, 숫자만 달리해서 새로운 폴더 생성
        try:
            if not(os.path.isdir(dir_name)):
                os.makedirs(os.path.join(dir_name))
                print("make dir : ",dir_name)
                break
            else: dir_name= dir_name[:-3]+"("+str(n)+")"
        except(OSError):
            print("Failed to create directory!!!!!")
    
    #생성한 폴더에 결과값 파일 생성
    with open(dir_name+"\insta_influencer_file.csv", 'w',newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["이름", "게시글 수", "팔로워 수"])
        for dic in result.keys():
            wr.writerow([dic, result[dic][0], result[dic][1]])
        print("make file1")
    
    #게시글 기준 내림차순 정렬
    with open(dir_name+"\insta_influencer_file_post.csv", 'w',newline="") as f:
        wr = csv.writer(f)
        cursor.execute("SELECT * FROM %s ORDER BY post DESC" %tablename)
        list = cursor.fetchall()
        wr.writerow(["이름", "게시글 수", "팔로워 수"])
        for dic in list:
            wr.writerow([dic[1], dic[2], dic[3]])
        print("make file2")
            
    #팔로워 기준 내림차순 정렬
    with open(dir_name+"\insta_influencer_file_follower.csv", 'w',newline="") as f:
        wr = csv.writer(f)
        cursor.execute("SELECT * FROM %s ORDER BY follower DESC" %tablename)
        list = cursor.fetchall()
        wr.writerow(["이름", "게시글 수", "팔로워 수"])
        for dic in list:
            wr.writerow([dic[1], dic[2], dic[3]])
        print("make file3")
    
    cursor.close()
    db.close()
    #검색 완료 시, 결과 문구 전송
    success =['검색이 완료되었습니다.', "바탕화면 'Insta_Influencer_File'폴더에서 결과 파일을 확인하세요."]
    return render_template('index.html', success=success)

if __name__ == '__main__':
    app.debug = True
    app.run(host = "127.0.0.1",  port =5000)
    app.run(debug = True)
    