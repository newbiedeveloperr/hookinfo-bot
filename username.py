# Original author: Sayyed Viquar Ahmed
# Extended with proper HTTP checks

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def _check(platform, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=7, allow_redirects=True)
        return (True if r.status_code == 200 else False), url
    except Exception:
        return None, url

def instagram(u): return _check("Instagram",  f"https://www.instagram.com/{u}/")
def facebook(u):  return _check("Facebook",   f"https://www.facebook.com/{u}")
def pinrest(u):   return _check("Pinterest",  f"https://www.pinterest.com/{u}/")
def twitter(u):   return _check("Twitter/X",  f"https://twitter.com/{u}")
def github(u):    return _check("GitHub",     f"https://github.com/{u}")
def tiktok(u):    return _check("TikTok",     f"https://www.tiktok.com/@{u}")
def reddit(u):    return _check("Reddit",     f"https://www.reddit.com/user/{u}")
def twitch(u):    return _check("Twitch",     f"https://www.twitch.tv/{u}")
def youtube(u):   return _check("YouTube",    f"https://www.youtube.com/@{u}")
def telegram(u):  return _check("Telegram",   f"https://t.me/{u}")
def steam(u):     return _check("Steam",      f"https://steamcommunity.com/id/{u}")
def snapchat(u):  return _check("Snapchat",   f"https://www.snapchat.com/add/{u}")
def linkedin(u):  return _check("LinkedIn",   f"https://www.linkedin.com/in/{u}")
def gitlab(u):    return _check("GitLab",     f"https://gitlab.com/{u}")
def medium(u):    return _check("Medium",     f"https://medium.com/@{u}")

ALL_PLATFORMS = [
    ("Instagram",  instagram),
    ("Facebook",   facebook),
    ("Pinterest",  pinrest),
    ("Twitter/X",  twitter),
    ("GitHub",     github),
    ("TikTok",     tiktok),
    ("Reddit",     reddit),
    ("Twitch",     twitch),
    ("YouTube",    youtube),
    ("Telegram",   telegram),
    ("Steam",      steam),
    ("Snapchat",   snapchat),
    ("LinkedIn",   linkedin),
    ("GitLab",     gitlab),
    ("Medium",     medium),
]
