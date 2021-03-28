import tweepy
import datetime,sys,time
from key import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN_KEY,ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

now = datetime.datetime.now()
api.update_status("test:" + str(now))
