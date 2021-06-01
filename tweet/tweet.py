import tweepy
import datetime, sys, time, yaml, codecs
from time import sleep
from datetime import timedelta
from key import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY,ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

while True:
  now = datetime.datetime.now()

  # 朝食(前日の18:00にツイート)
  if now.hour == 18 and now.minute == 0 and now.second == 0:
    with open("../outputs/menu.yml") as file:
      yml = yaml.safe_load(file)

      #朝食のみ前日にツイートするため次の日のデータを取得してくる
      api.update_status("~朝食~\n" + yml[(now.today() + timedelta(days=1)).strftime('%m/%d')]['breakfast'].replace(' ', '\n'))
      sleep(10)

  # 昼食(8:00にツイート)
  elif now.hour == 8 and now.minute == 0 and now.second == 0:
    with open("../outputs/menu.yml") as file:
      yml = yaml.safe_load(file)
      print("~昼食~\n" + yml[now.today().strftime('%m/%d')]['lunch'])
      api.update_status("~昼食~\n" + yml[now.today().strftime('%m/%d')]['lunch'])
      sleep(10)

  # 夕食(12:30にツイート)
  elif now.hour == 12 and now.minute == 50 and now.second == 0:
    with open("../outputs/menu.yml") as file:
      yml = yaml.safe_load(file)
      print("~夕食~\n" + yml[now.today().strftime('%m/%d')]['dinner'])
      api.update_status("~夕食~\n" + yml[now.today().strftime('%m/%d')]['dinner'])
      sleep(10)
