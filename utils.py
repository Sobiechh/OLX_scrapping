from bs4 import BeautifulSoup
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TEST_URL1 = "https://www.olx.pl/nieruchomosci/dzialki/lodzkie/"
TEST_URL2 = "https://www.olx.pl/nieruchomosci/dzialki/tomaszow-mazowiecki/?search%5Bfilter_float_price%3Ato%5D=1"
TEST_URL3 = "https://www.olx.pl/nieruchomosci/dzialki/lodzkie/?search%5Bfilter_float_m%3Ato%5D=200"
TEST_URL4 = "https://www.olx.pl/nieruchomosci/dzialki/lodzkie/?search%5Bfilter_float_price%3Ato%5D=50000"

current_page_number = 1

def get_url_content(url_link, page_number, **filters):
    """
    Get source code frome page
    """

    print(filters)
    print()
    print()
    if page_number != None:
        url_link += f"&page={page_number}&"

    for key, value in filters.items():
        url_link += get_search_filter(key, value) + "&"
    
    #headless option to chromedriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    #webdriver get source
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url_link)
    page_source = driver.page_source


    html_parser = BeautifulSoup(page_source, "html.parser")
    driver.close()

    print(url_link)

    return html_parser

def check_page_content(soup):
    """
    Return false when nothing meets criteria
    """
    if soup.find(class_="emptynew" ) == None:
        return True
    
    return False

def get_page_count(url_criteria):
    """
    Return number of pages
    """
    soup = get_url_content(url_criteria, 1)
    pager = soup.find(class_="pager")

    if pager == None: 
        return 1
    
    pager_items = pager.find_all(class_="item")
    numbers = [num.find('span').get_text() for num in pager_items]

    return int(numbers[-1])

def get_page_links(soup):
    """
    Gets all links from one site and return them into a list
    """
    if check_page_content(soup) == False:
        return None
    
    offers = soup.find_all(class_="offer-wrapper")
    links = [offer.find("a").get("href") for offer in offers if offer.find("a").get("href") != "#"]

    return links

def get_all_links(url_criteria):
    """
    Get all links offer from all sites
    """
    num_of_sites = get_page_count(url_criteria)

    all_offers = []

    for page_number in range(1, num_of_sites+1):
        url_content = get_url_content(url_criteria, page_number)
        page_links = get_page_links(url_content)

        if page_links == None:
            return []

        all_offers.extend(page_links)
    
    return reduce_duplicates(all_offers)

def reduce_duplicates(list_of_offers):
    """
    Reduce duplicated offers
    """

    return list(set(list_of_offers))

def txt_to_float(text):
    """
    Parse number in text from olx offer to float
    """
    parsed = float("".join(text.replace(",",".").split(" ")[:-1]))

    return parsed

def get_search_filter(filter_name, filter_value):
    """
    Get filters
    """
    if filter_name == "localization":
        value = f"{filter_value}/"
    if filter_name == "surface_min":
        value = f"search%5Bfilter_float_m%3Afrom%5D={filter_value}"
    if filter_name == "surface_max":
        value = f"search%5Bfilter_float_m%3Ato%5D={filter_value}"
    if filter_name == "seller":
        value = f"search%5Bprivate_business%5D={filter_value}"
    if filter_name == "type":
        value = f"search%5Bfilter_enum_type%5D%5B0%5D={filter_value}"

    return value
    
get_url_content("https://www.olx.pl/nieruchomosci/dzialki/?", 
                5, 
                surface_min=100,
                surface_max=3000,
                seller="private",
                type="dzialki-budowlane"
                )