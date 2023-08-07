#!/usr/bin/python3
# -*- coding: utf-8 -*-
from mastodon import Mastodon
from mastodon.streaming import StreamListener
import re
from oauth2client.service_account import ServiceAccountCredentials
import gspread


# 구글시트 세팅


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("dicebot-394804-ea8603f0116f.json", scope)
gc = gspread.authorize(creds)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1H_3YqJIv1UhdgEq4x4217VuP5Oerryl3YMDaXOuxCtw/edit?usp=sharing')
search = sh.worksheet("조사")

# 구글시트 세팅 끝

# 마스토돈 계정 세팅

BASE = 'https://occm.cc'

m = Mastodon(
    client_id="nJdRpfOqaXu_GPVtYHveFZf4DjW9buP7GWhAWkwTKWw",
    client_secret="sAVZl6IwZHfXlfyN_SnOrTfGebT3ptEKQSwzJBBJhH0",
    access_token="pmzXJoUCKfmM-ShhcHiDZTo8y0-7wsG8xeNRMpW20D8",
    api_base_url=BASE
)

print('성공적으로 로그인 되었습니다.')

# 마스토동 계정 세팅 끝

CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

class Listener(StreamListener):

    def on_notification(self, notification):
        if notification['type'] == 'mention':
            got = cleanhtml(notification['status']['content'])

            if got.__contains__('[') is False or got.__contains__(']') is False:
                pass

            else:
                keyword = got[got.find('[')+1:got.find(']')]
                
                try:
                    look = search.find(keyword, in_column=1, case_sensitive=True).row
                    result = search.get(f"R{look}C2:R{look}C5", value_render_option="UNFORMATTED_VALUE")[0]
                 
                    if result[1] is True:
                        try:
                            if result[2] is True:
                                try:
                                    m.status_post(f"@{notification['status']['account']['acct']} {result[3]}", in_reply_to_id= notification['status']['id'], visibility='private')
                                except:
                                    print(f'방문된 후의 지문이 별도로 기입되어 있지 않습니다. 해당 키워드의 조사 후 지문을 기입해주세요: {keyword}')
                                    m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id= notification['status']['id'], visibility='private')
                                return
                            else:
                                m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id= notification['status']['id'], visibility='private')
                                search.update_cell(look, 4, 'TRUE')
                        except Exception as e:
                            print(f'체크 관련 오류 발생: {e}')
                    else:
                        m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id= notification['status']['id'], visibility='private')
                except AttributeError:
                    m.status_post(f"@{notification['status']['account']['acct']} [{keyword}]는(은) 존재하지 않는 키워드입니다.\n만일 오류라고 판단되는 경우 운영진, 혹은 봇의 관리자에게 연락을 주세요.", in_reply_to_id=result, visibility='private')

def main():
    m.stream_user(Listener())

if __name__ == '__main__':
    main()
