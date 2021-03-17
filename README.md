# Finding-Instagram-Influencer
### 인스타그램 인플루언서를 찾아주는 프로그램입니다.<br>
**This is Finding Instagram Influencer Program**
<br><br>
* 조건 : 해시태그 (최대 5개), 팔로워 수, 게시글 수, 인플루언서 게시글에 포함된 키워드 개수<br>
* 위 조건을 입력하면 그에 맞는 인플루언서를 찾아줍니다.<br><br>
* Searching Condition : hashtag (max 5), follower number, post number, keyword count include influencer post<br>
* User input that Condition, then Program can find Influencer<br>
<br><br>
Selenium으로 크롤링하기 때문에 검색에  최대 수십분 소요될 수 있습니다.<br>
검색이 완료되면 웹에는 완료 문구만 나옵니다.<br>
결과는 DB에 저장하고, 바탕화면 폴더를 따로 생성하여 그 안에 CSV 파일로 저장됩니다.<br><br>
Cause crawling by selenium, You can wait tens of minutes for searching<br>
If end of searching, Web can show the complete phrase.<br>
Result is input to DB and making folder with csv file is created on the Desktop.<br>
------------------------------------------------------
## Example
**메인 화면 Index Page**<br>
![instagram2](https://user-images.githubusercontent.com/25974226/111517923-edd6fb00-8798-11eb-99e2-0237e0c5a4db.PNG)

<br><br>
**검색 결과 화면 Result Page**<br>
![insta-result](https://user-images.githubusercontent.com/25974226/111517917-eca5ce00-8798-11eb-8e66-21bd9debc055.PNG)
<br><br>
**결과 파일 형태 Result File List**<br>
![filelist](https://user-images.githubusercontent.com/25974226/99886233-37e22100-2c7e-11eb-8577-0b5b57fe2d46.PNG)
<br><br>
**CSV 파일 내용 확인 Check the CSV file content**<br>
![제주3](https://user-images.githubusercontent.com/25974226/99886226-3153a980-2c7e-11eb-8781-a0285231a776.PNG)
<br><br>

