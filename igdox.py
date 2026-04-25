# Original author: Sayyed Viquar Ahmed
# Adapted — instaloader backend (Instagram blocked old ?__a=1 API)

import instaloader

class dox:
    def __init__(self, username):
        L = instaloader.Instaloader()
        self._profile = instaloader.Profile.from_username(L.context, username)

    def username(self):     return self._profile.username
    def user_id(self):      return self._profile.userid
    def fullname(self):     return self._profile.full_name
    def followers(self):    return self._profile.followers
    def following(self):    return self._profile.followees
    def profile_pic(self):  return self._profile.profile_pic_url
    def bio(self):          return self._profile.biography
    def posts(self):        return self._profile.mediacount
    def url(self):          return self._profile.external_url
    def business(self):     return self._profile.is_business_account
    def recently(self):     return False
    def private(self):      return self._profile.is_private
    def verified(self):     return self._profile.is_verified
    def business_category(self): return self._profile.business_category_name
