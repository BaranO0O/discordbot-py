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

creds = ServiceAccountCredentials.from_json_keyfile_name("my-project-64703-9cf112921d15.json", scope)
gc = gspread.authorize(creds)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1X9fqj70pkQqM6WMZEUOQUUhVjkzM8CJsbjxp93NJoHg/edit?usp=sharing')
search = sh.worksheet("조사")
timed = sh.worksheet("예약")

# 구글시트 세팅 끝

# 마스토돈 계정 세팅

BASE = 'https://lucemnoctis.online'

m = Mastodon(
    client_id="jJO2wDLbpFMiugWsVZE1S4nGQcwSoIJZQii-dIK_WY8",
    client_secret="PxUS3yWRbZAf84QlGvVojUSKp3b2s1COnv_b-uK3_ig",
    access_token="YDckxaaDI-0Z9iq6GDZ235qpyU6YBVOpXKdhzn53XIs",
    api_base_url=BASE
)

print('성공적으로 로그인 되었습니다.')

# 마스토동 계정 세팅 끝


CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext


def getkey(toot_body):
    match = re.search(r'\[(.*?)\]', toot_body)
    return match.group(1) if match else None


class Listener(StreamListener):

    def on_notification(self, notification):
        if notification['type'] == 'mention':
            got = cleanhtml(notification['status']['content'])
            keyword = getkey(got)

            if keyword is None:
                return
            
            try:
                look = search.find(keyword, in_column=1, case_sensitive=True).row
                result = search.get(f"R{look}C2:R{look}C5", value_render_option="UNFORMATTED_VALUE")[0]
                 
                if result[1] is True:
                    try:
                        if result[2] is True:
                            if len(result) > 3:
                                m.status_post(f"@{notification['status']['account']['acct']} {result[3]}", in_reply_to_id=notification['status']['id'], visibility='private')
                            else:
                                print(f'방문된 후의 지문이 별도로 기입되어 있지 않습니다. 해당 키워드의 조사 후 지문을 기입해주세요: {keyword}')
                                m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id= notification['status']['id'], visibility='private')
                            return
                        else:
                            m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id= notification['status']['id'], visibility='private')
                            search.update_cell(look, 4, 'TRUE')
                    except Exception as e:
                        print(f'체크 관련 오류 발생: {e}')
                else:
                    m.status_post(f"@{notification['status']['account']['acct']} {result[0]}", in_reply_to_id=notification['status']['id'], visibility='private')
                    search.update_cell(look, 4, 'TRUE')
                    search.update_cell(look, 4, 'FALSE')
            except AttributeError:
                m.status_post(f"@{notification['status']['account']['acct']} [{keyword}]는(은) 존재하지 않는 키워드입니다.\n만일 오류라고 판단되는 경우 운영진, 혹은 봇의 관리자에게 연락을 주세요.", in_reply_to_id=result, visibility='private')

def main():
    m.stream_user(Listener())

if __name__ == '__main__':
    main()

while True:
    schedule.run_pending()
    time.sleep(20)

