#! /usr/bin/python3

import string
from getpass import getpass
from json import dump
from random import randint
from time import sleep
from selenium import webdriver
from os import environ
from os.path import realpath
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from argparse import ArgumentParser
import logging


# Locations
LOGIN_URL = "https://www.instagram.com/" 
BASE_URL_POST = "https://www.instagram.com/p/"
GECKODRIVER_PATH = environ.get("GECKODRIVER_PATH")
OUTPUT_DIR = "./outputs"

# Numeric params
LOADING_TIME = 2
WAIT_TIME_MAX = 20
WAIT_TIME_MIN = 10
MAX_ATTEMPTS = 3
MAX_LOAD_MORE_COMMENTS_CLICKS = 1

# constants used to locate comments in DOM
CSS_ID_COOKIES_ACCEPT = "button.aOOlW:nth-child(1)"
CSS_ID_COMMENT_CONTAINER = "XQXOT"
CSS_CLASS_COMMENT = "C4VMK"
CSS_CLASS_COMMENT_AUTHOR = "_6lAjh"
TAG_COMMENT_TEXT = "span" 

# constants to locate login elements
XPATH_USERNAME = "/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input"
XPATH_PASSWORD = "/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input"
XPATH_LOGIN = "/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]"
CSS_NOT_NOW = "button.sqdOP:nth-child(1)"

class TimeOutException(Exception):
    pass

class Comment:
    author = ""
    text = ""

class Stopper:
    attempts = 0
    maxAttempts = 0

    def __init__(self, maxAttempts):
        self.maxAttempts = maxAttempts

    def waitRandom(self, waitTimeMin, waitTimeMax):
        self.waitAbsolute(randint(waitTimeMin, waitTimeMax))
    
    def waitAbsolute(self, toWait):
        if self.attempts > self.maxAttempts:
            raise TimeOutException
        else:
            logging.debug("next action in " + str(toWait) + " seconds")
            sleep(toWait)
            self.attempts += 1
        
    


def logIn(driver, usernameScraped):
        
    # prompts for scraper instagram account password
    passwordScraper = getpass(f"Password for user {usernameScraped}:")
    driver.get(LOGIN_URL)
    
    # Accepts all cookies
    Stopper(1).waitRandom(WAIT_TIME_MIN, WAIT_TIME_MAX)
    #Stopper(1).waitAbsolute(3)
    driver.find_element_by_css_selector(CSS_ID_COOKIES_ACCEPT).click()
    
    # Enters username and password and logins
    Stopper(1).waitRandom(WAIT_TIME_MIN, WAIT_TIME_MAX)
    #Stopper(1).waitAbsolute(3)
    driver.find_element_by_xpath(XPATH_USERNAME).send_keys(usernameScraped)
    driver.find_element_by_xpath(XPATH_PASSWORD).send_keys(passwordScraper)
    Stopper(1).waitRandom(WAIT_TIME_MIN, WAIT_TIME_MAX)
    #Stopper(1).waitAbsolute(3)
    driver.find_element_by_xpath(XPATH_LOGIN).click()

    # Skips saving browser
    Stopper(1).waitRandom(WAIT_TIME_MIN, WAIT_TIME_MAX)
    #Stopper(1).waitAbsolute(3)
    driver.find_element_by_css_selector(CSS_NOT_NOW).click()

def scrapeComments(driver, userScraped, postId):

    # Can't scrape the post if postId is not provided
    if postId is None:
        print("No postId provided, exiting ...")
        return
    
    commentsScraped = []
   
    # Opens post with provided postId
    driver.get(BASE_URL_POST + postId)    
    
    # queries all comments 
    sleep(LOADING_TIME)
    i = 0
    stopper = Stopper(MAX_ATTEMPTS)
    while i < MAX_LOAD_MORE_COMMENTS_CLICKS:
        try:
            stopper.waitRandom(WAIT_TIME_MIN, WAIT_TIME_MAX)
            driver.find_element_by_css_selector(".dCJp8").click()
            i += 1
            stopper = Stopper(MAX_ATTEMPTS)
        except NoSuchElementException:
             logging.warning("'load more comments' button not found, retrying ...")
        except TimeOutException:
            logging.warning("Maximum waiting time for 'load more comments' button to pop up has expired")
            break
        
    # scrapes all comments
    commentsOnScreen = driver.find_elements_by_class_name(CSS_CLASS_COMMENT)
    for c in commentsOnScreen:
        commentHolder = Comment()
        commentHolder.author = c.find_element_by_class_name(CSS_CLASS_COMMENT_AUTHOR).text
        commentHolder.text = c.find_elements_by_tag_name(TAG_COMMENT_TEXT)[1].text
        logging.debug("author=" + commentHolder.author + ", text=" + commentHolder.text)
        commentsScraped.append(commentHolder)

    logging.info(f"Succesfully scraped {len(commentsScraped)} comments")
    
    # Dumps scraped data
    with open(OUTPUT_DIR + "/comments_" + postId + ".json", 'w') as comments, open(OUTPUT_DIR + "/authors_" + postId + ".txt", 'w') as authors:
        
        # If author is the OP, skip this comment
        for c in commentsScraped:
            if userScraped not in c.author:
        
                # Txt file with one author per line
                authors.write(c.author + "\n")
            else:
                commentsScraped.remove(c)
        # Json file with all Comment objects
        dump([c.__dict__ for c in commentsScraped], comments, indent=1)          
    
    logging.info(f"comments dumped at {realpath(comments.name)}")
    logging.info(f"authors dumped at {realpath(authors.name)}")


if __name__ == '__main__':
    logging.getLogger().setLevel("INFO")
    parser = ArgumentParser(description="scrapes instagram post comments ")
    parser.add_argument("userScraper", type=str, nargs='?')
    parser.add_argument("userScraped", type=str, nargs='?')
    parser.add_argument("postId", type=str, nargs='?')

    args = parser.parse_args()

    with webdriver.Firefox(executable_path=GECKODRIVER_PATH) as driver:
        logIn(driver, args.userScraper)
        scrapeComments(driver, args.userScraped, args.postId)
