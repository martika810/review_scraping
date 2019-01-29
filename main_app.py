import pickle
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
from urllib.parse import urljoin
from glassdoor_scraper import extract_employee_years, extract_recomends,extract_rating_info

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
    browser.get(url)

def go_next_page(browser, base_url):
    next_button = browser.find_element_by_css_selector('#FooterPageNav li.next a')
    next_url_link = next_button.get_attribute('href')
    next_full_link = urljoin(base_url,next_url_link)
    browser.get(next_full_link)

def is_last_page(browser):
    # #FooterPageNav > div > ul > li.next > a
    return not(len(browser.find_elements_by_css_selector("#FooterPageNav li.next > a")) >= 1)

# Return a dictionary with all reviews in that page
def extract_all_reviews_on_this_page(browser,dataframe):
    facebook_html_parser = BeautifulSoup(browser.page_source, 'html.parser')
    extracted_reviews_on_this_page = facebook_html_parser.select("div.hreview")
    for extracted_review in extracted_reviews_on_this_page:
        review = {}
        # Extract the date
        review_date = extracted_review.select("div.cf time.date")
        review['review date'] = review_date[0].text

        # Extract status, position and location which is in this format(Current Employee - Technical Sourcer in London, England)
        employee_status_position_location = extracted_review.select("span.authorInfo span.authorJobTitle.middle.reviewer")[0].text
        review['employee_status'] = employee_status_position_location.split('-')[0]
        review['employee position'] = employee_status_position_location.split('-')[1]
        employee_location = extracted_review.select("span.authorInfo span.authorLocation")[0].text
        review['employee_location'] = employee_location

        review_title = extracted_review.select("h2 a.reviewLink span.summary")[0].text
        review['review_title'] = review_title

        review['employee_years_at_company'] = extract_employee_years(extracted_review)
        # #span.voteHelpful > button span.count span
        number_helpful_votes = extracted_review.select("span.voteHelpful > button span.count span")[0].text
        review['number_helpful_votes'] = number_helpful_votes

        pros_text = extracted_review.select("div.description div.prosConsAdvice p.pros")[0].text
        review['pros_text'] = pros_text

        # div.prosConsAdvice  p.mainText
        cons_text = extracted_review.select("div.description div.prosConsAdvice p.cons")[0].text
        review['cons_text'] = cons_text
        advice_management_element = extracted_review.select("div.description div.prosConsAdvice p.adviceMgmt")
        if(len(advice_management_element)>0):
            review['advice_mgmt_text'] = ''
        else:
            review['advice_mgmt_text'] = 'not mentioned'

        rating_dictionary_information = extract_rating_info(extracted_review)
        review['ratings_work_life_balance'] = rating_dictionary_information['ratings_work_life_balance']
        review['ratings_culture_values'] = rating_dictionary_information['ratings_culture_values']
        review['ratings_career_oportinity'] = rating_dictionary_information['ratings_career_oportinity']
        review['ratings_comp_benefits'] = rating_dictionary_information['ratings_comp_benefits']
        review['ratings_senior_management'] = rating_dictionary_information['ratings_senior_management']
        review['overall_rating'] = rating_dictionary_information['overall_rating']

        recommends_results = extract_recomends(extracted_review)
        if 'recommeds' in recommends_results:
            review['recommends'] = recommends_results['recommends']
        if 'positive_outlook' in recommends_results:
            review['positive_outlook'] = recommends_results['positive_outlook']
        if 'approves_ceo' in recommends_results:
            review['approves_ceo'] = recommends_results['approves_ceo']

        review_serie = pd.Series(review, index = review.keys())
        dataframe = dataframe.append(review_serie, ignore_index=True)
    return dataframe



facebook_url = "https://www.glassdoor.co.uk/Reviews/Facebook-Reviews-E40772.htm"
login_glassdoor_url = "https://www.glassdoor.co.uk/profile/login_input.htm?userOriginHook=HEADER_SIGNIN_LINK"
filename_to_save = 'extracted_reviews.csv'
browser = webdriver.Chrome('./chromedriver')
browser.implicitly_wait(15)

get_cookies(browser, login_glassdoor_url)

set_cookies(browser, facebook_url)

dataframe_file = Path(filename_to_save)
if(not dataframe_file.exists()):
    dataframe = pd.DataFrame()
else:
    dataframe = pd.read_csv(filename_to_save)

browser.get(facebook_url)

while not is_last_page(browser):

    dataframe = extract_all_reviews_on_this_page(browser,dataframe)
    dataframe.to_csv('extracted_review.csv')
    go_next_page(browser, facebook_url)

browser.quit()

# #MainCol > div.module.snug.empStatsAndReview