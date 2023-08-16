#!/usr/bin/python3
# -*- coding: utf-8 -*-
from mastodon import Mastodon
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import schedule
import time
import datetime


# 구글시트 세팅


scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("dicebot-394804-ea8603f0116f.json", scope)
gc = gspread.authorize(creds)
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1H_3YqJIv1UhdgEq4x4217VuP5Oerryl3YMDaXOuxCtw/edit?usp=sharing')
search = sh.worksheet("조사")
timed = sh.worksheet("예약")

# 구글시트 세팅 끝

# 마스토돈 계정 세팅

BASE = 'https://occm.cc'

m = Mastodon(
    client_id="w9Yrf034cWrQvGI2n-NATWB48-gDhMAJAWA9oc4JZjg",
    client_secret="vIvfRD6fi_ftm65Gu6j5vDiMychnSreKj-_4K_ttNNs",
    access_token="uvbAlR6YoUlyuFNf0dPptxt7yZsaOnTZrnz2iwjUJew",
    api_base_url=BASE
)

print('성공적으로 로그인 되었습니다.')

# 마스토동 계정 세팅 끝

def post_at_time():
    toots = timed.get("C3:C7", value_render_option="UNFORMATTED_VALUE")
    print(toots)
    posting_date = datetime.datetime.now()
    print(posting_date)
    p_year = posting_date.year
    p_month = posting_date.month
    p_day = posting_date.day
    kst = datetime.timezone(datetime.timedelta(hours=9))
    try:
        m.status_post(f"{toots[0][0]}", scheduled_at=datetime.datetime(p_year, p_month, p_day, 1, 00, tzinfo=kst), visibility='private')
        print('통금툿 예약 완료')
        m.status_post(f"{toots[1][0]}", scheduled_at=datetime.datetime(p_year, p_month, p_day, 7, 00, tzinfo=kst), visibility='private')
        print('아침 점호툿 예약 완료')
        m.status_post(f"{toots[2][0]}", scheduled_at=datetime.datetime(p_year, p_month, p_day, 12, 00, tzinfo=kst), visibility='private')
        print('점심 식단툿 예약 완료')
        m.status_post(f"{toots[3][0]}", scheduled_at=datetime.datetime(p_year, p_month, p_day, 17, 00, tzinfo=kst), visibility='private')
        print('저녁 식단툿 예약 완료')
        m.status_post(f"{toots[4][0]}", scheduled_at=datetime.datetime(p_year, p_month, p_day, 21, 00, tzinfo=kst), visibility='private')
        print('일일의뢰 종료툿 예약 완료')
        print('전체 예약 완료')
        look = m.scheduled_statuses()
        print(look)
    except Exception as e:
        print(f'다음과 같은 오류가 발생하였습니다: {e}')


schedule.every().day.at("01:31").do(post_at_time)


while True:
    schedule.run_pending()
    time.sleep(20)

