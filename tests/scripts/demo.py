#!/usr/bin/python
# -*- coding:UTF-8 -*-
"""
# @Time    :    2025-09-14 13:57
# @Author  :   crawl-coder
# @Desc    :   None
"""
import requests


headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Origin": "http://127.0.0.1:5178",
    "Pragma": "no-cache",
    "Referer": "http://127.0.0.1:5178/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Google Chrome\";v=\"140\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\""
}
url = "http://127.0.0.1:8000/api/v1/users/me"
response = requests.get(url, headers=headers)

print(response.text)
print(response)