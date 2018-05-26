import os
import sys
import time
import ConfigParser
import os
import time

from src import InstaBot
from src.check_status import check_status
from src.feed_scanner import feed_scanner
from src.follow_protocol import follow_protocol
from src.unfollow_protocol import unfollow_protocol


if __name__ == '__main__':


    config = ConfigParser.RawConfigParser(allow_no_value=True)
    config.read('./config.properties')
    print(config.get("ACCOUNT", "username"))
    print(config.get("ACCOUNT", "password"))
