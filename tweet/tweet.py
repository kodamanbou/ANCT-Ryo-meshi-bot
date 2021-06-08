import os
from pathlib import Path
import tweepy
import datetime, yaml
from time import sleep
from datetime import timedelta
from key import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
file_path = Path(os.path.dirname(__file__)).parent.joinpath('outputs/menu.yml').resolve()
print(file_path)

while True:
    now = datetime.datetime.now()

    # 朝食(前日の18:00にツイート)
    if now.hour == 18 and now.minute == 0 and now.second == 0:
        with open(file_path) as file:
            yml = yaml.safe_load(file)
            menus = yml[(now.today() + timedelta(days=1)).strftime('%m/%d')]['breakfast']
            menu_text = ''
            for menu in menus:
                menu_text += menu
                menu_text += '\n'

            # 朝食のみ前日にツイートするため次の日のデータを取得してくる
            api.update_status("~朝食~\n" + menu_text)
            sleep(10)

    # 昼食(8:00にツイート)
    elif now.hour == 8 and now.minute == 0 and now.second == 0:
        with open(file_path) as file:
            yml = yaml.safe_load(file)
            menus = yml[now.today().strftime('%m/%d')]['lunch']
            menu_text = ''
            for menu in menus:
                menu_text += menu
                menu_text += '\n'
            api.update_status("~昼食~\n" + menu_text)
            sleep(10)

    # 夕食(12:50にツイート)
    elif now.hour == 12 and now.minute == 50 and now.second == 0:
        with open(file_path) as file:
            yml = yaml.safe_load(file)
            menus = yml[now.today().strftime('%m/%d')]['dinner']
            menu_text = ''
            for menu in menus:
                menu_text += menu
                menu_text += '\n'
            api.update_status("~夕食~\n" + menu_text)
            sleep(10)
