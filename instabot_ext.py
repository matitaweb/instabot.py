

import json
import src.instabot
import time
import random
import re

class InstaBotGeoloc(src.instabot.InstaBot):
    def __init__(self,
                 login,
                 password,
                 like_per_day=2000,
                 media_max_like=50,
                 media_min_like=0,
                 follow_per_day=0,
                 follow_time=5 * 60 * 60,
                 unfollow_per_day=0,
                 start_at_h=0,
                 start_at_m=0,
                 end_at_h=23,
                 end_at_m=59,
                 database_name='follows_db.db',
                 comment_list=[["this", "the", "your"],
                               ["photo", "picture", "pic", "shot", "snapshot"],
                               ["is", "looks", "feels", "is really"],
                               ["great", "super", "good", "very good", "good",
                                "wow", "WOW", "cool", "GREAT", "magnificent",
                                "magical", "very cool", "stylish", "beautiful",
                                "so beautiful", "so stylish", "so professional",
                                "lovely", "so lovely", "very lovely", "glorious",
                                "so glorious", "very glorious", "adorable",
                                "excellent", "amazing"],
                               [".", "..", "...", "!", "!!", "!!!"]],
                 comments_per_day=0,
                 tag_list=['cat', 'car', 'dog'],
                 max_like_for_one_tag=5,
                 unfollow_break_min=15,
                 unfollow_break_max=30,
                 log_mod=0,
                 proxy="",
                 user_blacklist={},
                 tag_blacklist=[],
                 unwanted_username_list=[],
                 unfollow_whitelist=[],
                 geotag='c1175277/bologna-italy',
                 geotag_tot_page=21
                 ):
        src.instabot.InstaBot.__init__(self,
                 login,
                 password,
                 like_per_day=like_per_day,
                 media_max_like=media_max_like,
                 media_min_like=media_min_like,
                 follow_per_day=follow_per_day,
                 follow_time=follow_time,
                 unfollow_per_day=unfollow_per_day,
                 start_at_h=start_at_h,
                 start_at_m=start_at_m,
                 end_at_h=end_at_h,
                 end_at_m=end_at_m,
                 database_name=database_name,
                 comment_list=comment_list,
                 comments_per_day=comments_per_day,
                 tag_list=tag_list,
                 max_like_for_one_tag=max_like_for_one_tag,
                 unfollow_break_min=unfollow_break_min,
                 unfollow_break_max=unfollow_break_max,
                 log_mod=log_mod,
                 proxy=proxy,
                 user_blacklist=user_blacklist,
                 tag_blacklist=tag_blacklist,
                 unwanted_username_list=unwanted_username_list,
                 unfollow_whitelist=unfollow_whitelist)

        self.url_geo_tag = 'https://www.instagram.com/explore/locations/%s/?page=%i&__a=1'
        self.url_geo_location = 'https://www.instagram.com/explore/locations/%s/?page=%i&__a=1'

        self.geotag = geotag
        self.geotag_tot_page = geotag_tot_page
        self.location_list = []

        #

    # overrride
    def login(self):
        log_string = 'Trying to login as %s...\n' % (self.user_login)
        self.write_log(log_string)
        self.login_post = {
            'username': self.user_login,
            'password': self.user_password
        }

        self.s.headers.update({
            'Accept': '*/*',
            'Accept-Language': self.accept_language,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': self.user_agent,
            'X-Instagram-AJAX': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        })

        r = self.s.get(self.url)
        #self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        csrf_token = re.search('(?<=\"csrf_token\":\")\w+', r.text).group(0)
        self.s.headers.update({'X-CSRFToken': csrf_token})
        time.sleep(5 * random.random())
        login = self.s.post(
            self.url_login, data=self.login_post, allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrftoken = login.cookies['csrftoken']
        #ig_vw=1536; ig_pr=1.25; ig_vh=772;  ig_or=landscape-primary;
        self.s.cookies['ig_vw'] = '1536'
        self.s.cookies['ig_pr'] = '1.25'
        self.s.cookies['ig_vh'] = '772'
        self.s.cookies['ig_or'] = 'landscape-primary'
        time.sleep(5 * random.random())

        if login.status_code == 200:
            r = self.s.get('https://www.instagram.com/')
            finder = r.text.find(self.user_login)
            if finder != -1:
                self.user_id = login.cookies['ds_user_id']
                self.login_status = True
                log_string = '%s login success!' % (self.user_login)
                self.write_log(log_string)
            else:
                self.login_status = False
                self.write_log('Login error! Check your login data!')
        else:
            self.write_log('Login error! Connection error!')

    def like_all_exist_media_check(self, media):

        if not self.login_status:
            return False
        """
        l_c = media['likes']['count']
        if not ((l_c <= self.media_max_like and l_c >= self.media_min_like) or
                (self.media_max_like == 0 and l_c >= self.media_min_like) or
                (self.media_min_like == 0 and l_c <= self.media_max_like) or
                (self.media_min_like == 0 and self.media_max_like == 0)):
            return False

        for blacklisted_user_name, blacklisted_user_id in self.user_blacklist.items():
            if media['owner']['id'] == blacklisted_user_id:
                self.write_log("Not liking media owned by blacklisted user: " + blacklisted_user_name)
                return False
        """
        if media['node']['owner']['id'] == self.user_id:
            self.write_log("Keep calm - It's your own media ;)")
            return False

        if self.is_media_already_liked(media['node']['shortcode']):
            self.write_log("Keep calm - already liked %s" %(media['node']['id']))
            return False

        return True

    def is_media_already_liked(self, media_code):
        #'https://www.instagram.com/p/BbDmj4mA7AX/?__a=1'
        if not self.login_status:
            return True

        if self.login_status != 1:
            return True

        url_check = 'https://www.instagram.com/p/%s/?__a=1'% (media_code)
        try:
            r = self.s.get(url_check)
            data = json.loads(r.text)

            viewer_has_liked =  data['graphql']['shortcode_media']['viewer_has_liked']
            return viewer_has_liked
        except:
            return True

    def get_location_id_by_geotag(self, tag, page):
        """ Get media ID set, by your hashtag """

        if self.login_status:
            if self.login_status == 1:
                url_tag = self.url_geo_location % (tag, page)
                try:
                    r = self.s.get(url_tag)
                    all_data = json.loads(r.text)

                    return list(all_data['location_list'])
                except:
                    self.write_log("Except on location_list!")
                    time.sleep(self.ban_sleep_time)
        return []

    def get_media_id_by_geotag(self, loc):
        """ Get media ID set, by your hashtag """

        result = []
        loc_id = loc['id']
        loc_name = loc['name']
        max_page_to_load = 1
        page_num = 0
        for i in range(max_page_to_load):
            page_num = i+1

            if not self.login_status:
                break

            if self.login_status != 1:
                break

            url_tag = self.url_geo_tag % (loc_id, page_num)
            try:
                r = self.s.get(url_tag)
                all_data = json.loads(r.text)
                has_next_page = False
                try:
                    has_next_page = all_data['graphql']['location']['edge_location_to_media']['page_info']['has_next_page']
                except:
                    self.write_log("Except on get_media!")
                    has_next_page = False

                #append
                l = list(all_data['graphql']['location']['edge_location_to_media']['edges'])
                result.extend(l)

                #no more pages
                if not has_next_page:
                    break

            except:
                self.write_log("Except on get_media!")
                break

        self.write_log("Get media id by location_id: %s, name: %s, page %i, tot %i" % (loc_id, loc_name, page_num, len(result)))
        return result

    def new_auto_mod_geo(self):

        # load or reload all location
        self.location_list = []
        for i in range(self.geotag_tot_page):
            a = self.get_location_id_by_geotag(self.geotag, (i+1))
            self.location_list.extend(a)

        self.write_log("Get location id by tag: %s, %i location" % (self.geotag, len(self.location_list)))

        while True:

            if(len(self.location_list) == 0) :
                self.write_log("Location list finished... ")
                break

            # ------------------- Get media_id -------------------
            if len(self.media_by_tag) == 0:
                loc = random.choice(self.location_list)
                self.location_list.remove(loc)
                self.media_by_tag = self.get_media_id_by_geotag(loc)
                self.this_tag_like_count = 0
                self.max_tag_like_count = random.randint(1, self.max_like_for_one_tag)

            # ------------------- Like -------------------
            if self.like_per_day != 0 and len(self.media_by_tag) > 0:
                media = self.media_by_tag.pop()

                already_liked = self.already_liked(media)
                if already_liked:
                    randint = random.randint(1, 5)
                    self.write_log("already liked in local db id: %s ...sleep: %d sec." % (media['node']['id'], randint))
                    time.sleep(randint)
                    continue

                to_like = self.like_all_exist_media_check(media)
                self.save_media_liked(media)

                if not to_like:
                    randint = random.randint(1, 5)
                    self.write_log("got already liked from instagram id: %s ...sleep: %d sec." % (media['node']['id'],randint))
                    time.sleep(randint)
                    continue

                like = self.like(media['node']['id'])

                if like != 0:
                    if like.status_code == 200:
                        # Like, all ok!
                        self.error_400 = 0
                        self.like_counter += 1
                        self.write_log("Liked: %s. Like #%i." % (media['node']['id'], self.like_counter))
                    elif like.status_code == 400:
                        self.write_log("Not liked: %i" % (like.status_code))
                        # Some error. If repeated - can be ban!
                        if self.error_400 >= self.error_400_to_ban:
                            # Look like you banned!
                            time.sleep(self.ban_sleep_time)
                        else:
                            self.error_400 += 1
                    else:
                        self.write_log("Not liked: %i" % (like.status_code))

                time_random = self.like_delay * 0.8 + self.like_delay * 0.2 * random.random()
                self.write_log("... sleep: %d sec." % (time_random))
                time.sleep(time_random)

    def already_liked(self, media):
        filename_to_open = "already_liked.txt"
        try:
            with open(filename_to_open, 'r') as already_liked_file:
                for line in already_liked_file:
                        if str(media['node']['id']+'\n') == line:
                            return True

        except IOError as e:
            print("Unable to open file " + filename_to_open)  # Does not exist OR no read permissions

            with open('already_liked.txt', 'w') as f:
                f.write("ID_ALREADY_LIKED_LIST \n")

        return False

    def save_media_liked(self, media):
        with open("already_liked.txt", "a") as already_liked_file:
            already_liked_file.write(media['node']["id"]+"\n")
        return False

