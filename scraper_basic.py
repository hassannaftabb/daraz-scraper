import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--disable-notifications')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

query = "Rubiks Cube"
pages = 2
query = '+'.join(query.split())

file_name = open(f'daraz-products-{'-'.join(query.split('+'))}.csv', "w", encoding='utf-8')
writer = csv.writer(file_name)
writer.writerow(['Product Name', 'Rating', 'Items Sold', 'Selling Price'])

for page in range(1, pages + 1):
    try:
        driver.get(f"https://www.daraz.pk/catalog/?page={page}&q={query}")
        
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-qa-locator='general-products']")))
        
        time.sleep(2)
        
        product_items = driver.find_elements(By.CSS_SELECTOR, "div[data-qa-locator='product-item']")
        
        for item in product_items:
            try:
                try:
                    name_element = item.find_element(By.CSS_SELECTOR, "div.RfADt a")
                    item_name = name_element.get_attribute('title')
                except NoSuchElementException:
                    item_name = "N/A"
                
                try:
                    rating_div = item.find_element(By.CSS_SELECTOR, "div.mdmmT")
                    full_stars = len(rating_div.find_elements(By.CSS_SELECTOR, "i.Dy1nx"))
                    half_stars = len(rating_div.find_elements(By.CSS_SELECTOR, "i.K8PID"))
                    rating = full_stars + (0.5 * half_stars)
                    
                    try:
                        review_span = rating_div.find_element(By.CSS_SELECTOR, "span.qzqFw")
                        reviews = review_span.text.strip('()')
                    except NoSuchElementException:
                        reviews = "0"
                    
                    item_ratings = f"{rating} ({reviews})"
                except NoSuchElementException:
                    item_ratings = "N/A"
                
                try:
                    sold_element = item.find_element(By.CSS_SELECTOR, "span._1cEkb span")
                    items_sold = sold_element.text.strip()
                except NoSuchElementException:
                    items_sold = "N/A"
                
                try:
                    price_element = item.find_element(By.CSS_SELECTOR, "div.aBrP0 span.ooOxS")
                    item_list_price = price_element.text.strip()
                except NoSuchElementException:
                    item_list_price = "N/A"
                
                writer.writerow([item_name, item_ratings, items_sold, item_list_price])
                print(f"Processed: {item_name[:50]}...")
                
            except Exception as e:
                print(f"Error processing item: {str(e)}")
                continue
                
    except TimeoutException as e:
        print(f"Timeout error on page {page}: {str(e)}")
        continue
    except Exception as e:
        print(f"Error processing page {page}: {str(e)}")
        continue

file_name.close()
driver.quit()