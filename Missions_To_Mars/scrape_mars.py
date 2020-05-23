#Import Dependencies

import pandas as pd
from bs4 import BeautifulSoup
from splinter import Browser
import time
from selenium import webdriver
import requests


#Define Executable Path and browser

# executable_path = {'executable_path': 'chromedriver.exe'}
# browser =  Browser('chrome', **executable_path, headless=False)

def scrape():

    #Define Executable Path and browser

    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)

    latest_news_title,latest_news_blurb = mars_news(browser)

    mars_data_set = {"latest_title":latest_news_title,
                "latest_blurb": latest_news_blurb,
                "mars_featured_image":mars_featured_image(browser),
                "mars_weather": mars_weather_tweet(),
                "mars_facts_table": mars_facts(browser),
                "mars_hemisphere_images": mars_hemisphere_images(browser)
                }
    
    browser.quit()
    return mars_data_set


#Create Scraping functions for Mars sites

def mars_news(browser):
    #Mars News Site: https://mars.nasa.gov/news/
    #Access Mars News Website with Splinter

    news_url = 'https://mars.nasa.gov/news/'
    browser.visit(news_url)
    time.sleep(1)

    news_html = browser.html
    news_soup = BeautifulSoup(news_html, 'html.parser')

    first_story = news_soup.find('ul', class_='item_list')

    latest_news_title = first_story.find('div', class_='content_title').text
    latest_news_blurb = first_story.find('div', class_='article_teaser_body').text

    # news_list = [latest_news_title, latest_news_blurb]

    return latest_news_title, latest_news_blurb

def mars_featured_image(browser):

    executable_path = {'executable_path': 'chromedriver'}
    browser = Browser('chrome', **executable_path)

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'html.parser')
    browser.quit()

    s = soup.find('article', class_ = 'carousel_item')['style']
    mars_featured_image_url = 'https://www.jpl.nasa.gov'+s[(s.find("('") + len("('")) : s.find("')")]

    return mars_featured_image_url


# def mars_featured_image(browser):

#     # JPL Website: https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
#     #Access JPL Website with Splinter

#     jpl_image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
#     browser.visit(jpl_image_url)
#     time.sleep(10)
#     browser.click_link_by_partial_text('FULL IMAGE')

#     jpl_image_html = browser.html
#     jpl_image_soup = BeautifulSoup(jpl_image_html, 'html.parser')

#     try:
#         image_url = jpl_image_soup.find('img',class_='fancybox-image')['src']
#     except AttributeError:
#         return None
#     #JPL Main Site URL: https://www.jpl.nasa.gov/

#     jpl_url = 'https://www.jpl.nasa.gov/'

#     #Create full URL to Featured Mars Image

#     mars_featured_image_url = jpl_url + image_url

#     return mars_featured_image_url

def mars_weather_tweet():

    #Mars Twitter Site: https://twitter.com/marswxreport?lang=en
    #Access Mars Twitter Website with Splinter

    weather_url = 'https://twitter.com/marswxreport?lang=en'
    result = requests.get(weather_url)
    time.sleep(30)

    twitter_weather_html = result.text
    twitter_weather_soup = BeautifulSoup(twitter_weather_html, 'html.parser')

    mars_twitter_weather = twitter_weather_soup.find(class_='tweet-text').get_text()

    return mars_twitter_weather

def mars_facts(browser):

    #Mars Facts Site: https://space-facts.com/mars/
    #Access Mars Facts Website with Splinter

    facts_url = 'https://space-facts.com/mars/'
    browser.visit(facts_url)
    time.sleep(10)

    facts_html = browser.html
    facts_soup = BeautifulSoup(facts_html, 'html.parser')

    #Pull data from table on Mars Facts Site

    mars_facts_table = facts_soup.find('table', class_="tablepress tablepress-id-p-mars")
    column_a = mars_facts_table.find_all('td',class_='column-1')
    column_b = mars_facts_table.find_all('td',class_='column-2')

    metrics = []
    values = []

    for metric in column_a:
        metric = metric.text.strip()
        metrics.append(metric)
        
    for value in column_b:
        value = value.text.strip()
        values.append(value)
        
    #Create Dataframe

    Mars_Facts_df = pd.DataFrame({"Metric": metrics,"Value":values})

    #Create HTML Table

    Mars_Facts_HTML = Mars_Facts_df.to_html(index=False)

    return Mars_Facts_HTML

def mars_hemisphere_images(browser):

    #Hemispheres URL: https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars

    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    time.sleep(10)

    hemispheres_html = browser.html
    hemispheres_soup = BeautifulSoup(hemispheres_html, 'html.parser')

    #Scrape site for images

    hemisphere_images = hemispheres_soup.find_all('div',class_='item')

    #Create empty list for loop
    hemisphere_image_links = [] 

    #Main URL for USGS site (remainder URL pulls forward slash after gov)
    main_hemispheres_url = 'https://astrogeology.usgs.gov'

    for image in hemisphere_images:
    
        #Find Title 
        image_title = image.find('h3').text
    
        #Identify remaning piece of URL for each image
        remainder_hemispheres_url = image.find('a', class_="itemLink product-item")['href']
    
        #Use Splinter to visit each site
        browser.visit(main_hemispheres_url + remainder_hemispheres_url)
    
        remainder_hemispheres_html = browser.html
    
        hemi_soup = BeautifulSoup(remainder_hemispheres_html, 'html.parser')
    
        image_url = main_hemispheres_url + hemi_soup.find('img', class_ = 'wide-image')['src']
    
        hemisphere_image_links.append({"Title":image_title, "img_url":image_url})

    return hemisphere_image_links



