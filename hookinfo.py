# Original author: Sayyed Viquar Ahmed
# Ported from CLI to Telegram Bot

import json
import phonenumbers as p
from phonenumbers import carrier, geocoder, timezone
from urllib.request import urlopen
from username import ALL_PLATFORMS
import urllib


# ── 1. Instagram OSINT ────────────────────────────────────────────────────────

def instagram_check(username: str) -> str:
    try:
        import instaloader
        L = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(L.context, username)

        lines = [
            f"📸 *Instagram OSINT*",
            f"👤 Username   : `{profile.username}`",
            f"🆔 User ID    : `{profile.userid}`",
            f"📛 Full Name  : `{profile.full_name or 'N/A'}`",
            f"🔗 Ext. URL   : {profile.external_url or 'None'}",
            f"🖼️  Posts      : `{profile.mediacount}`",
            f"👥 Followers  : `{profile.followers:,}`",
            f"➡️  Following  : `{profile.followees:,}`",
            f"📝 Bio        : {profile.biography or 'N/A'}",
            f"🔒 Private    : `{'Yes' if profile.is_private else 'No'}`",
            f"✅ Verified   : `{'Yes' if profile.is_verified else 'No'}`",
            f"🏢 Business   : `{'Yes' if profile.is_business_account else 'No'}`",
        ]
        if profile.business_category_name:
            lines.append(f"📂 Category   : `{profile.business_category_name}`")
        return "\n".join(lines)

    except Exception as e:
        return f"❌ Could not fetch Instagram data for `{username}`.\nReason: `{e}`"


# ── 2. Web Search ─────────────────────────────────────────────────────────────

def web_search(query: str) -> str:
    try:
        from googlesearch import search
        results = list(search(query, num_results=10))

        if not results:
            return "❌ Can't Search your Query — no results found."

        lines = [f"🌐 *Web Search Results*\nQuery: `{query}`\n"]
        for i, url in enumerate(results, 1):
            lines.append(f"`{i}.` {url}")
        return "\n".join(lines)

    except Exception as e:
        return f"❌ Web search failed.\nError: `{e}`"


# ── 3. Phone Lookup ───────────────────────────────────────────────────────────

def phone_lookup(no: str) -> str:
    try:
        ph_no = p.parse(no)
        if not p.is_valid_number(ph_no):
            return "❌ Invalid phone number. Use international format e.g. `+919876543210`"

        geo_location = geocoder.description_for_number(ph_no, 'en')
        no_carrier   = carrier.name_for_number(ph_no, 'en')
        tz_list      = timezone.time_zones_for_number(ph_no)
        fmt_intl     = p.format_number(ph_no, p.PhoneNumberFormat.INTERNATIONAL)
        fmt_e164     = p.format_number(ph_no, p.PhoneNumberFormat.E164)

        num_type_map = {
            0: "Fixed Line", 1: "Mobile", 2: "Fixed/Mobile",
            3: "Toll Free", 4: "Premium Rate", 6: "VOIP", 7: "Personal",
        }
        num_type = num_type_map.get(p.number_type(ph_no), "Unknown")

        lines = [
            f"📞 *Phone Lookup*",
            f"📱 Number     : `{fmt_intl}`",
            f"🔢 E.164      : `{fmt_e164}`",
            f"🌍 Country    : `{geo_location or 'Unknown'}`",
            f"📡 Carrier    : `{no_carrier or 'Unknown'}`",
            f"🕐 Timezone   : `{', '.join(tz_list) or 'Unknown'}`",
            f"📋 Type       : `{num_type}`",
        ]
        return "\n".join(lines)

    except Exception:
        return "❌ No data found for this number.\nTip: Use international format like `+14155552671`"


# ── 4. IP Lookup ──────────────────────────────────────────────────────────────

def ip_lookup(ip: str) -> str:
    try:
        url = "http://ip-api.com/json/" + ip
        values = json.load(urlopen(url))

        if values.get("status") == "fail":
            return f"❌ Can't find information for `{ip}`.\nReason: {values.get('message', 'Unknown')}"

        lines = [
            f"🖥️  *IP Lookup*",
            f"🌐 IP Address : `{values.get('query', ip)}`",
            f"🌍 Country    : `{values.get('country', 'N/A')} ({values.get('countryCode', '')})`",
            f"🏙️  Region     : `{values.get('regionName', 'N/A')}`",
            f"🏘️  City       : `{values.get('city', 'N/A')}`",
            f"📮 ZIP        : `{values.get('zip', 'N/A')}`",
            f"🕐 Timezone   : `{values.get('timezone', 'N/A')}`",
            f"📡 ISP        : `{values.get('isp', 'N/A')}`",
            f"🏢 Org        : `{values.get('org', 'N/A')}`",
            f"🔢 AS         : `{values.get('as', 'N/A')}`",
        ]
        lat = values.get('lat')
        lon = values.get('lon')
        if lat and lon:
            lines.append(f"\n[📍 View on Google Maps](https://maps.google.com/?q={lat},{lon})")
        return "\n".join(lines)

    except Exception as e:
        return f"❌ Can't find information for the given IP address.\nError: `{e}`"


# ── 5. Username Search ────────────────────────────────────────────────────────

def username_search(username: str) -> str:
    found, not_found, errors = [], [], []

    for platform_name, func in ALL_PLATFORMS:
        status, url = func(username)
        if status is True:
            found.append(f"✅ [{platform_name}]({url})")
        elif status is False:
            not_found.append(f"❌ {platform_name}")
        else:
            errors.append(f"⚠️ {platform_name}")

    lines = [f"🔍 *Username Search — `{username}`*\n"]
    if found:
        lines.append("*Found on:*")
        lines.extend(found)
    if not_found:
        lines.append(f"\n*Not found on {len(not_found)} platform(s)*")
    if errors:
        lines.append(f"\n*Could not check {len(errors)} platform(s)*")

    return "\n".join(lines)
