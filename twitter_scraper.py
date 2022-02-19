'''
Version 0.1

GOAL: Be able to grab all tweets that mention a specified hashtag, in a specified period of time



Still buggy. TODO:
-Make sure it doesnt skip tweets
-Account for end of document
-Enable specifying time period


'''


import csv
from getpass import getpass
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime, timedelta

import os
if ';C:\selenium_drivers' not in os.environ['PATH']:
    os.environ['PATH'] += r';C:\selenium_drivers'

def get_tweet_data(card):
    ''' Extract data from tweet card'''
    username = card.find_element(By.XPATH, './/span').text
    handle = card.find_element(By.XPATH, './/span[contains(text(), "@")]').text
    try:
        postdate = card.find_element(By.XPATH, './/time').get_attribute('datetime')
    except NoSuchElementException:
        return
    comment = card.find_element(By.XPATH, './div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[1]').text
    attachment = card.find_element(By.XPATH, './div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]').text
    text = comment + attachment
    reply_cnt = card.find_element(By.XPATH, './/div[@data-testid="reply"]').text
    retweet_cnt = card.find_element(By.XPATH, './/div[@data-testid="retweet"]').text
    like_cnt = card.find_element(By.XPATH, './/div[@data-testid="like"]').text

    tweet = (postdate, handle, username, text, reply_cnt, retweet_cnt, like_cnt)
    return tweet

#open browser, navigate to twitter and log in
driver = Chrome()
driver.maximize_window()
sleep(3)

driver.get('https://twitter.com/login')
sleep(3)

username = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[5]/label/div/div[2]/div/input')
username.send_keys('USERNAME')
username.send_keys(Keys.RETURN)
sleep(3)

verify_username = driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
verify_username.send_keys('HANDLE')
verify_username.send_keys(Keys.RETURN)
sleep(3)

password = driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[3]/div/label/div/div[2]/div[1]/input')
password.send_keys('PASSWORD')
password.send_keys(Keys.RETURN)
sleep(3)

#search for key word
search_input = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/label/div[2]/div/input')
search_input.send_keys('#nyancat')
search_input.send_keys(Keys.RETURN)
sleep(3)

#navigate to latest tweets tab
driver.find_element_by_link_text('Latest').click()
sleep(3)




#grab all available tweets

data = []
tweet_ids = set() #prevent scraping same tweet multiple times
last_position = driver.execute_script("return document.body.scrollHeight")
scrolling = True



while len(data)<20:
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    print('grabbing latest cards')
    for card in page_cards:#[-20:]:
        tweet = get_tweet_data(card)
        if tweet:
            tweet_id = tweet[0]+tweet[1] #concatenate handle and datetime to create unique identifier for tweet
            if tweet_id not in tweet_ids:
                tweet_ids.add(tweet_id)
                data.append(tweet)




    scroll_attempt = 0
    while (datetime.strptime(data[-1][0], "%Y-%m-%dT%H:%M:%S.%fZ") > datetime.now()-timedelta(days=7)):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)
        current_position = driver.execute_script("return document.body.scrollHeight")
        if last_position == current_position:  
            scroll_attempt +=1
            print('scroll failed, trying again')
            sleep(5)

        else:
            last_position = current_position
            break
            