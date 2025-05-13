import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementNotInteractableException,
    WebDriverException
)
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

def get_element_text(element, selectors, use_xpath=False):
    """Helper method to get element text with multiple fallback selectors"""
    for selector in selectors:
        try:
            if use_xpath:
                return element.find_element(By.XPATH, selector).text
            return element.find_element(By.CSS_SELECTOR, selector).text
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
            continue
    return "N/A"

def get_element_attribute(element, selectors, attribute, use_xpath=False):
    """Helper method to get element attribute with multiple fallback selectors"""
    for selector in selectors:
        try:
            if use_xpath:
                return element.find_element(By.XPATH, selector).get_attribute(attribute)
            return element.find_element(By.CSS_SELECTOR, selector).get_attribute(attribute)
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
            continue
    return "N/A"

def get_element(element, selectors, use_xpath=False):
    """Helper method to get element with multiple fallback selectors"""
    for selector in selectors:
        try:
            if use_xpath:
                return element.find_element(By.XPATH, selector)
            return element.find_element(By.CSS_SELECTOR, selector)
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
            continue
    return None

def get_elements(element, selectors, use_xpath=False):
    """Helper method to get elements with multiple fallback selectors"""
    for selector in selectors:
        try:
            if use_xpath:
                elements = element.find_elements(By.XPATH, selector)
            else:
                elements = element.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return elements
        except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
            continue
    return []

def get_rating_info(item):
    """Helper method to get rating information with multiple fallback approaches"""
    css_selectors = [
        "div.mdmmT",
        "div[class*='rating']",
        "div[class*='stars']",
        "div[class*='review']"
    ]
    
    xpath_selectors = [
        ".//div[contains(@class, 'rating')]",
        ".//div[contains(@class, 'stars')]",
        ".//div[contains(@class, 'review')]",
        ".//div[.//i[contains(@class, 'star')]]",
        ".//div[.//span[contains(text(), '★')]]"
    ]
    
    rating_div = get_element(item, css_selectors) or get_element(item, xpath_selectors, use_xpath=True)
    if not rating_div:
        return "N/A"
    
    star_selectors = [
        # css selectors
        "i.Dy1nx, i[class*='star']",
        "i[class*='full']",
        "i[class*='star']",
        "span[class*='star']",
        # xpath selectors
        ".//i[contains(@class, 'star')]",
        ".//i[contains(@class, 'full')]",
        ".//span[contains(@class, 'star')]",
        ".//i[contains(text(), '★')]",
        ".//span[contains(text(), '★')]"
    ]
    
    half_star_selectors = [
        # css selectors
        "i.K8PID, i[class*='half']",
        "i[class*='half']",
        "span[class*='half']",
        # xpath selectors
        ".//i[contains(@class, 'half')]",
        ".//span[contains(@class, 'half')]",
        ".//i[contains(text(), '½')]",
        ".//span[contains(text(), '½')]"
    ]
    
    review_selectors = [
        # css selectors
        "span.qzqFw",
        "span[class*='review']",
        "span[class*='count']",
        "span[class*='rating']",
        # xpath selectors
        ".//span[contains(text(), 'review')]",
        ".//span[contains(text(), 'rating')]",
        ".//span[contains(text(), '(')]",
        ".//span[contains(text(), ')')]"
    ]
    
    try:
        full_stars = len(get_elements(rating_div, star_selectors)) or len(get_elements(rating_div, star_selectors, use_xpath=True))
        half_stars = len(get_elements(rating_div, half_star_selectors)) or len(get_elements(rating_div, half_star_selectors, use_xpath=True))
        rating = full_stars + (0.5 * half_stars)
        
        reviews = get_element_text(rating_div, review_selectors) or get_element_text(rating_div, review_selectors, use_xpath=True)
        reviews = reviews.strip('()')
        if not reviews:
            reviews = "0"
            
        return f"{rating} ({reviews})"
    except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, ValueError) as e:
        print(f"Error getting rating info: {str(e)}")
        return "N/A"

for page in range(1, pages + 1):
    try:
        driver.get(f"https://www.daraz.pk/catalog/?page={page}&q={query}")
        
        wait = WebDriverWait(driver, 10)
        
        # css selectors
        css_selectors = [
            "div[data-qa-locator='general-products']",
            "div[class*='products']",
            "div[class*='items']",
            "div[class*='grid']",
            "div[class*='list']"
        ]
        
        # xpath selectors
        xpath_selectors = [
            "//div[contains(@class, 'products')]",
            "//div[contains(@class, 'items')]",
            "//div[contains(@class, 'grid')]",
            "//div[contains(@class, 'list')]",
            "//div[.//div[contains(@class, 'product')]]",
            "//div[.//a[contains(@class, 'title')]]"
        ]
        
        for selector in css_selectors + xpath_selectors:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR if selector in css_selectors else By.XPATH, selector)))
                break
            except TimeoutException:
                continue
        
        time.sleep(2)
        
        product_items = []
        
        # css selectors
        css_item_selectors = [
            "div[data-qa-locator='product-item']",
            "div[class*='product-item']",
            "div[class*='product-card']",
            "div[class*='product']",
            "div[class*='item']"
        ]
        
        # xpath selectors
        xpath_item_selectors = [
            "//div[contains(@class, 'product-item')]",
            "//div[contains(@class, 'product-card')]",
            "//div[contains(@class, 'product')]",
            "//div[.//a[contains(@class, 'title')]]",
            "//div[.//span[contains(text(), 'Rs.')]]",
            "//div[.//i[contains(@class, 'star')]]"
        ]
        
        for selector in css_item_selectors + xpath_item_selectors:
            try:
                if selector in css_item_selectors:
                    product_items = driver.find_elements(By.CSS_SELECTOR, selector)
                else:
                    product_items = driver.find_elements(By.XPATH, selector)
                if product_items:
                    break
            except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException):
                continue
        
        for item in product_items:
            try:
                # css selectors
                css_name_selectors = [
                    "div.RfADt a",
                    "a[class*='title']",
                    "div[class*='title'] a",
                    "h2 a",
                    "a[class*='name']",
                    "div[class*='name'] a"
                ]
                
                # xpath selectors
                xpath_name_selectors = [
                    ".//a[contains(@class, 'title')]",
                    ".//a[contains(@class, 'name')]",
                    ".//h2//a",
                    ".//div[contains(@class, 'title')]//a",
                    ".//div[contains(@class, 'name')]//a",
                    ".//a[contains(@href, '/products/')]"
                ]
                
                item_name = get_element_attribute(item, css_name_selectors, 'title') or get_element_attribute(item, xpath_name_selectors, 'title', use_xpath=True)
                
                item_ratings = get_rating_info(item)
                
                # css selectors
                css_sold_selectors = [
                    "span._1cEkb span",
                    "span[class*='sold']",
                    "span[class*='sales']",
                    "span[class*='purchase']",
                    "span[class*='buy']"
                ]
                
                # xpath selectors
                xpath_sold_selectors = [
                    ".//span[contains(text(), 'sold')]",
                    ".//span[contains(text(), 'sales')]",
                    ".//span[contains(text(), 'purchase')]",
                    ".//span[contains(text(), 'buy')]",
                    ".//span[contains(text(), 'sale')]"
                ]
                
                items_sold = get_element_text(item, css_sold_selectors) or get_element_text(item, xpath_sold_selectors, use_xpath=True)
                
                # css selectors
                css_price_selectors = [
                    "div.aBrP0 span.ooOxS",
                    "div[class*='price'] span",
                    "span[class*='price']",
                    "div[class*='cost'] span",
                    "span[class*='cost']"
                ]
                
                # xpath selectors
                xpath_price_selectors = [
                    ".//span[contains(text(), 'Rs.')]",
                    ".//span[contains(text(), 'PKR')]",
                    ".//div[contains(@class, 'price')]//span",
                    ".//span[contains(@class, 'price')]",
                    ".//div[contains(@class, 'cost')]//span"
                ]
                
                item_list_price = get_element_text(item, css_price_selectors) or get_element_text(item, xpath_price_selectors, use_xpath=True)
                
                writer.writerow([item_name, item_ratings, items_sold, item_list_price])
                print(f"Processed: {item_name[:50]}...")
                
            except (NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException, ValueError) as e:
                print(f"Error processing item: {str(e)}")
                continue
                
    except TimeoutException as e:
        print(f"Timeout error on page {page}: {str(e)}")
        continue
    except WebDriverException as e:
        print(f"WebDriver error on page {page}: {str(e)}")
        continue
    except Exception as e:
        print(f"Unexpected error on page {page}: {str(e)}")
        continue

file_name.close()
driver.quit() 