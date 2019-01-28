import pickle
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd

# https://www.glassdoor.co.uk/Overview/Working-at-SmartFocus-EI_IE450765.11,21.htm
def get_cookies(browser,url):
    browser.get(url)
    print('input your username and password in Firefox and hit Submit')
    input('Hit Enter here if you have summited the form: <Enter>')
    cookies = browser.get_cookies()
    pickle.dump(cookies, open("cookies.pickle", "wb"))


def set_cookies(browser,url):
    browser.get(url)
    cookies = pickle.load(open("cookies.pickle", "rb"))
    for cookie in cookies:
        browser.add_cookie(cookie)

    browser.add_cookie({'name':'aep_usuc_f',
                        'value':'isfm=y&site=glo&c_tp=GBP&x_alimid=814979923&isb=y&ups_u_t=1577293226431&region=UK&b_locale=en_US&ae_u_p_s=0'})
    browser.get(url)

def go_next_page(browser):
    browser.fing_element_by_css_selector("#FooterPageNav li.next > a")[0].click()

# Return a dictionary with all reviews in that page
def extract_all_reviews_on_this_page(browser,dataframe):
    facebook_html_parser = BeautifulSoup(browser.page_source, 'html.parser')
    extracted_reviews_on_this_page = facebook_html_parser.select("div.hreview")
    for extracted_review in extracted_reviews_on_this_page:
        review = {}
        review_date = extracted_review.select("div.cf time.date")
        review['review date'] = review_date[0].text
        review['employee position'] = ''
        review['employee_location'] = ''
        review['employee_status'] = ''
        review['review_title'] = ''
        review['employee_years_at_company'] = ''
        review['number_helpful_votes'] = ''
        review['pros_text'] = ''
        review['cons_text'] = ''
        review['advice_mgmt_text'] = ''
        review['ratings_category1'] = ''
        review['ratings_category2'] = ''
        review['ratings_category3'] = ''
        review['ratings_category4'] = ''
        review['ratings_category5'] = ''
        review['overall_rating'] = ''
        dataframe.append(pd.Series(review, index = review.keys()))



facebook_url = "https://www.glassdoor.co.uk/Reviews/Facebook-Reviews-E40772.htm"
filename_to_save = 'extracted_reviews.csv'
browser = webdriver.Chrome('./chromedriver')
browser.implicitly_wait(15)

dataframe_file = Path(filename_to_save)
if(not dataframe_file.exists()):
    dataframe = pd.DataFrame()
else:
    dataframe = pd.read_csv(filename_to_save)

browser.get(facebook_url)

extract_all_reviews_on_this_page(browser,dataframe)
dataframe.to_csv(filename_to_save)
go_next_page(browser)
browser.quit()

# #MainCol > div.module.snug.empStatsAndReview