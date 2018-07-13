#!/usr/bin/env python
# encoding: utf-8
import datetime
import json
import base64
from time import sleep

import pymongo
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""
输入你的微博账号和密码，可去淘宝买，一元七个。
建议买几十个，微博反扒的厉害，太频繁了会出现302转移。
或者你也可以把时间间隔调大点。
"""
WeiBoAccounts = [
{'username': 'liujuan86088@163.com', 'password': '*****'},
]

cookies = []
client = pymongo.MongoClient("localhost", 27017)
db = client["Sina"]
userAccount = db["userAccount"]


def get_cookie_from_weibo(username, password):
    driver = webdriver.Chrome()
    driver.get('https://weibo.cn')
    assert "微博" in driver.title
    login_link = driver.find_element_by_link_text('登录')
    ActionChains(driver).move_to_element(login_link).click().perform()
    login_name = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "loginName"))
    )
    login_password = driver.find_element_by_id("loginPassword")
    login_name.send_keys(username)
    login_password.send_keys(password)
    login_button = driver.find_element_by_id("loginAction")
    login_button.click()
    # 这里停留了10秒观察一下启动的Chrome是否登陆成功了，没有的化手动登陆进去
    sleep(10)
    cookie = driver.get_cookies()
    driver.close()
    return cookie


def init_cookies():
    for cookie in userAccount.find():
        cookies.append(cookie['cookie'])


if __name__ == "__main__":
    try:
        userAccount.drop()
    except Exception as e:
        pass
    for account in WeiBoAccounts:
        cookie = get_cookie_from_weibo(account["username"], account["password"])
        userAccount.insert_one({"_id": account["username"], "cookie": cookie})
