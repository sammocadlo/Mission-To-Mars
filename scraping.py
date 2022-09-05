# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

# create scrape_all function to initialize the browser, create a data dict, end the webdriver and return scraped data
def scrape_all():
    # Initiate headless driver for deployment (splinter)
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    #run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }
    # stop webdriver and return data
    browser.quit()
    return data


# insert scraping code into a function
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # parse the html
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # add a try/except block for handling errors
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # use the parent element to find the summary of the article
        news_p = slide_elem.find('div', class_='article_teaser_body'). get_text()

    except AttributeError:
        return None, None
    
    # add a return statement to the mars_news function
    return news_title, news_p

# ## JPL Space Images Featured Image

# insert scraping code into a function
def featured_image(browser):

    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # adding try/except block for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    # add a return statement to featured_image function
    return img_url

# ## Mars Facts 

# insert mars facts code into a function
def mars_facts():

    # add a BaseException try/except block
    try:
        # create pandas df from html table on website - using read_html to scrape the facts into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]
    except BaseException:
        return None

    # assign columns and set index of dataframe
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # convert df table to html
    return df.to_html()

# insert mars_hemispheres code into a function
def hemispheres(browser):

# Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

# Create a list to hold the images and titles (output to disply in #4 below).
    hemisphere_image_urls = []

# Write code to retrieve the image urls and titles for each hemisphere.
    #Since the main page has only thumbnails, we have to click into each one...
    #then grab each item (each image, each title), 
    #then add them together into the hemisphere_image_urls

    try:
        
        for content in range(4):
    
            #click each link... https://splinter.readthedocs.io/en/latest/elements-in-the-page.html
            browser.links.find_by_partial_text('Hemisphere')[content].click()
            
            #using soup to parse (jupycell 4, above)
            html = browser.html
            hemisphere_soup = soup(html, 'html.parser')
            
            #scrape the interior page...
            title = hemisphere_soup.find('h2', class_='title').text
            img_url = hemisphere_soup.find('li').a.get('href')
            
            #define dictionary, define dictionary items
            hemisphere_content = {}
            hemisphere_content['title']=title
            hemisphere_content['img_url']= f'https://marshemispheres.com/{img_url}' 
            
            #add scraped stuff together into hemisphere_image_urls
            hemisphere_image_urls.append(hemisphere_content)
            browser.back()  #<<LOOP

    except AttributeError:
        return None

    # Print the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
