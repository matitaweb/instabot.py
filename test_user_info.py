
import os
import sys
import time
import ConfigParser
import os
import time
# https://github.com/instabot-py/instabot.py

# import sys
# sys.path.insert(0, '../src')
import src.userinfo

if __name__ == '__main__':
    ui = src.userinfo.UserInfo()
    hello = ui.hello()
    # search by user_name:
    ui.search_user(user_id="3075876582")
    # or if you know user_id ui.search_user(user_id="50417061")
    print(ui.user_name)
    print(ui.user_id)

    # get following list with no limit
    ui.get_following()
    print(ui.following)

    # get followers list with limit 10
    ui.get_followers(limit=10)
    print(ui.followers)