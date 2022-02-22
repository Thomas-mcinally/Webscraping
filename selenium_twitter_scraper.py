'''
selenium_twitter_scraper version 2.0

Thomas Mcinally tuesday 22/02/2022 (two's day!)

This module allows you to scrape all latest tweets by specifying:
- Search term
- Date to look for tweets since
- Limit on nr. of tweets to scrape (gets most recent ones first)



TODO (next version):
-Add language filter option 

'''
#######################  INPUTS  #############################
search_term = '#nyancat' #str
since = '2022-02-22T00:00:00.000Z' #str e.g.'2000-01-01T00:00:00.000Z'
limit = 5  #int

twitter_username = 'YOUR_EMAIL'
twitter_handle = 'YOUR_HANDLE' #used if twitter asks to verify identity with handle/phone number
twitter_password = 'YOUR_PASSWORD'
##############################################################



import pandas as pd
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Chrome

from selenium.webdriver.common.by import By
from datetime import datetime, timedelta

import os
if ';C:\selenium_drivers' not in os.environ['PATH']:
    os.environ['PATH'] += r';C:\selenium_drivers'

#reformat date input from str to datetime
earliest_date = datetime.strptime(since, "%Y-%m-%dT%H:%M:%S.%fZ")

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


##open browser, maximize window and zoom out to 33%
driver = Chrome()
driver.maximize_window()
sleep(3)
driver.get('chrome://settings/')
driver.execute_script('chrome.settingsPrivate.setDefaultZoom(0.33);')
sleep(3)


##navigate to twitter, login and search for search term
driver.get('https://twitter.com/login')
sleep(3)
username = driver.find_element(By.XPATH,'/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[5]/label/div/div[2]/div/input')
username.send_keys(twitter_username)
username.send_keys(Keys.RETURN)
sleep(3)
#need this if promted to verify identity. Comment out if not
verify_username = driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input')
verify_username.send_keys(twitter_handle)
verify_username.send_keys(Keys.RETURN)
sleep(3)
password = driver.find_element(By.XPATH, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[3]/div/label/div/div[2]/div[1]/input')
password.send_keys(twitter_password)
password.send_keys(Keys.RETURN)
sleep(3)
#search for key word
search_input = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/label/div[2]/div/input')
search_input.send_keys(search_term)
search_input.send_keys(Keys.RETURN)
sleep(3)
#navigate to latest tweets tab
#driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[2]/nav/div/div[2]/div/div[2]/a/div/span').click() # Doesnt work when zoomed out
webElement = driver.find_element(By.XPATH, ("/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[2]/nav/div/div[2]/div/div[2]/a/div/span"))
driver.execute_script("arguments[0].click()", webElement) #workaround, works when zoomed out
sleep(3)


##grab all available tweets
data = []
tweet_ids = set() #prevent scraping same tweet multiple times
last_position = driver.execute_script("return document.body.scrollHeight")
scrolling = True

while scrolling:
    page_cards = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    print('grabbing latest cards')
    for card in page_cards:
        tweet = get_tweet_data(card)
        if tweet:
            if (len(data)<limit):
                if (datetime.strptime(tweet[0], "%Y-%m-%dT%H:%M:%S.%fZ") > earliest_date):
                    tweet_id = tweet[0]+tweet[1] #concatenate handle and datetime to create unique identifier for tweet
                    if tweet_id not in tweet_ids:
                        tweet_ids.add(tweet_id)
                        data.append(tweet)
                        print(tweet)
                else:
                    print('Earliest tweet day reached, ending search...')
                    scrolling = False #end outer while loop
                    break #break out of for loop
            else:
                print('Nr. of scraped tweets reached limit, ending search...')
                scrolling = False #end outer while loop
                break #break out of for loop

#Scroll down on webpage to load new tweets
    scroll_attempt = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(5)
        current_position = driver.execute_script("return document.body.scrollHeight")
        if last_position == current_position:  
            scroll_attempt +=1

            if scroll_attempt >= 3: 
                print('maximum nr. of failed scrolls reached, ending search...')  
                scrolling = False #ending outer while loop
                break #break out of current while loop
            else:
                sleep(3) #attempt to scroll again

        else:
            last_position = current_position
            break #break out of current while loop and scrape new tweets


##Save tweets to csv
df = pd.DataFrame(data, columns=('postdate', 'handle', 'username', 'text', 'reply_cnt', 'retweet_cnt', 'like_cnt'))
csv_path = search_term+'_tweets_after_'+since.replace('-','_').replace(':','_').replace('.','_')+'.csv'
print('Scraping done. Saving tweets in '+csv_path)
df.to_csv(csv_path, index=False, header=True)