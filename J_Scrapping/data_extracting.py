import os
import logging

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)

import os
import math
import pandas as pd
import urllib.request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from tqdm import tqdm

def get_total_products(driver, url):
    """Get the total number of products on the page."""
    print(f"Loading URL: {url}")
    driver.get(url)
    wait = WebDriverWait(driver, 30)
    total = wait.until(EC.presence_of_element_located((By.ID, "toolbar-amount")))
    
    is_paging = check_if_paging(driver)
    
    if is_paging:
        total_products = int(total.text.split(" ")[-1])
    else:
        total_products = int(total.text.split(" ")[0])

    print(f"Total products found: {total_products}")
    return total_products, is_paging

def check_if_paging(driver):
    """Check if paging is present on the page."""
    try:
        driver.find_element(By.ID, "paging-label")
        return True
    except NoSuchElementException:
        return False

def get_pagination_links(driver, main_page, total_products, products_per_page=36):
    """Get all pagination links."""
    print("Collecting pagination links...")
    page_urls = [main_page]
    max_page = math.ceil(total_products / products_per_page)
    
    for page_number in range(1, max_page + 1):
        page_url = f"{main_page}?p={page_number}"
        print(f"Loading page: {page_url}")
        driver.get(page_url)
        wait = WebDriverWait(driver, 60)
        pagination_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pages-items")))
        pagination_links = pagination_container.find_elements(By.CLASS_NAME, "page")
        page_urls = get_page_url(pagination_links, page_urls)
    
    print(f"Total pagination links collected: {len(page_urls)}")
    return page_urls

def get_page_url(pagination_links, page_urls):
    for link in pagination_links:
        url = link.get_attribute('href')
        if url and url not in page_urls:
            page_urls.append(url)
                
    return page_urls

def get_product_links(driver, page_urls):
    """Get all product links from the page URLs."""
    print("Collecting product links...")
    items_link = []
    
    for url in tqdm(page_urls, desc="Product Links"):
        driver.get(url)
        ul_element = driver.find_elements(By.CLASS_NAME, 'product-item')
        for item in ul_element:
            prod_link = item.find_element(By.CLASS_NAME, 'product-item-link').get_attribute('href')
            if prod_link:
                items_link.append(prod_link)
    
    unique_links = list(set(items_link))
    print(f"Total unique product links collected: {len(unique_links)}")
    return unique_links

def remove_existing_links(items_link, csv_file_path):
    """Remove existing product links if they already exist in the CSV file."""
    print(f"Checking for existing links in: {csv_file_path}")
    if os.path.exists(csv_file_path):
        existing_data = pd.read_csv(csv_file_path)
        existing_links = existing_data['Link'].tolist()
        items_link = [x for x in items_link if x not in existing_links]
        print(f"New product links after removing existing ones: {len(items_link)}")
    else:
        print("No existing CSV found. All links are considered new.")
    
    return items_link

def update_image_url(url, new_width, new_height):
    """Update image URL with new dimensions."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params['width'] = new_width
    query_params['height'] = new_height
    new_query_string = urlencode(query_params, doseq=True)
    new_url = urlunparse(parsed_url._replace(query=new_query_string))
    return new_url

def fetch_product_page(driver, link, timeout=120):
    """Fetch the product page."""
    driver.get(link)
    return WebDriverWait(driver, timeout)


def get_product_basic_info(driver, wait):
    """Extract basic product details such as name, price, and description."""
    prod_price = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'price'))).text
    prod_name = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'base'))).text
    prod_description = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@class='value' and @itemprop='description']"))).text
    return prod_price, prod_name, prod_description


def get_product_additional_info(driver):
    """Extract additional product information from the specifications table."""
    element = driver.find_element(By.ID, "product-attribute-specs-table")
    tbody = element.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    more_info = []
    for row in rows:
        cell_th = row.find_element(By.TAG_NAME, "th")
        cell_td = row.find_element(By.TAG_NAME, "td")
        more_info.append(f"{cell_th.get_attribute('innerText')}: {cell_td.get_attribute('innerText')}")
    return more_info[:-1]  # Removing the last element


def extract_name_and_code(prod_name):
    """Extract name and code from the product name."""
    return map(str.strip, prod_name.split('|'))


def get_image_sources(driver):
    """Find and return image sources."""
    image_container = driver.find_element(By.CLASS_NAME, "MagicToolboxSelectorsContainer")
    sources = image_container.find_elements(By.TAG_NAME, "img")
    return [img.get_attribute('src') for img in sources]


def download_image(src_url, code, index, image_save_dir):
    """Download image from the given source URL."""
    new_url = update_image_url(src_url, 1000, 778.5)
    file_path = os.path.join(image_save_dir, f"{code}_{index+1}.jpg")
    urllib.request.urlretrieve(str(new_url), file_path)


def scrape_product_details(driver, items_link, image_save_dir):
    """Scrape product details and download images."""
    print("Scraping product details...")
    products = []
    timeout_prds = []
    error_prds = []
    
    for link in tqdm(items_link, desc="Scraping Products"):
        try:
            wait = fetch_product_page(driver, link)
            prod_price, prod_name, prod_description = get_product_basic_info(driver, wait)
            more_info = get_product_additional_info(driver)
            name, code = extract_name_and_code(prod_name)
            
            products.append({
                'Name': name,
                'Code': code,
                'Link': link,
                'Price': prod_price,
                'Description': prod_description,
                'More info': more_info
            })
            
            image_sources = get_image_sources(driver)
            for index, src_url in enumerate(image_sources):
                download_image(src_url, code, index, image_save_dir)
        
        except TimeoutException:
            timeout_prds.append(link)
        except Exception as e:
            error_prds.append((link, str(e)))
    
    handle_scrape_errors(timeout_prds, error_prds)
    print(f"Total products scraped: {len(products)}")
    return products


def handle_scrape_errors(timeout_prds, error_prds):
    """Handle and log errors that occurred during scraping."""
    for link in timeout_prds:
        print(f"Timeout occurred with URL: {link}")
    
    for link, error in error_prds:
        print(f"An error occurred with URL {link}: {error}")



