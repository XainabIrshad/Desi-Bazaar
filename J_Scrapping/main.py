import json
import os
import sys
import pandas as pd
from selenium import webdriver
from data_extracting import (
    get_total_products,
    get_pagination_links,
    get_product_links,
    remove_existing_links,
    scrape_product_details,
    )
from data_processing import data_processing
from image_processing import image_processing
from data_post_processing import post_processing
from database import get_db_connection, create_table, load_data, add_fulltext_index

def load_config(config_file):
    """Load configuration from a JSON file."""
    with open(config_file, 'r') as file:
        return json.load(file)


def append_or_create_csv(csv_file_path, new_data):
    """Append rows to an existing CSV file or create a new one if it doesn't exist."""
    if os.path.exists(csv_file_path):
        existing_data = pd.read_csv(csv_file_path)
        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        print(f"Appended data to existing CSV file at {csv_file_path}")
        combined_data.to_csv(csv_file_path, index=False)
    else:
        print(f"Created new CSV file at {csv_file_path}")
        new_data.to_csv(csv_file_path, index=False)


# Create Images Folder
os.makedirs("Images", exist_ok=True)
if os.path.exists("new_products.csv"):
    os.remove("new_products.csv")
        
# Load config
config = load_config('config.json')

driver = webdriver.Chrome()

all_products = []

for main_page in config["main_pages"]:
    total_products, is_paging = get_total_products(driver, main_page)
    if is_paging:
        page_urls = get_pagination_links(driver, main_page, total_products)
    else:
        page_urls = [main_page]
    items_link = get_product_links(driver, page_urls)
    
    # Remove existing links
    items_link = remove_existing_links(items_link, config["csv_file_path"])
    
    # Scrape product details
    products = scrape_product_details(driver, items_link, config["image_save_dir"])
    all_products.extend(products)

# Close the driver
driver.quit()

# Append or create CSV file

append_or_create_csv(config["new_csv_file_path"], pd.DataFrame(all_products))
df_products = None
try:
    df_products = pd.read_csv(config["new_csv_file_path"])
     # # Data processing
    df_products_processed = data_processing(df_products)
    df_products_processed.to_csv(config["new_csv_file_path"], index=False)

    # Image processing
    df_images_processed = image_processing(df_products_processed, config["image_save_dir"])
    df_images_processed.to_csv(config["new_csv_file_path"], index=False)

    # Post processing
    df_final = post_processing(df_images_processed)
    df_final.to_csv(config["new_csv_file_path"], index=False)

    append_or_create_csv(config["csv_file_path"], df_final)


    # Database operations
    connection = get_db_connection(config["db_host"], config["db_user"], config["db_password"], config["db_name"]) 
    cursor = connection.cursor()

    create_table(cursor, config["table_name"])
    load_data(cursor, config["table_name"], df_final)
    add_fulltext_index(cursor, config["table_name"])

    connection.commit()
    cursor.close()
    connection.close()
    print("Database operations completed successfully.")

except pd.errors.EmptyDataError:
    print("The CSV file is empty, No new products found.")
    sys.exit()