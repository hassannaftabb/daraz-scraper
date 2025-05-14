import csv
import requests
from bs4 import BeautifulSoup
import time
import random

def get_page_content(url):
    """Get page content with retry mechanism"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))
            continue
    return None

def get_rating_info(item):
    """Extract rating information from product item"""
    try:
        # Try different rating selectors
        rating_div = item.select_one('div.mdmmT, div.rating, div.stars, div.review')
        if not rating_div:
            return "N/A"

        # Get full stars
        full_stars = len(rating_div.select('i.Dy1nx, i.star, i.full, span.star'))
        
        # Get half stars
        half_stars = len(rating_div.select('i.K8PID, i.half, span.half'))
        
        rating = full_stars + (0.5 * half_stars)
        
        # Get review count
        review_span = rating_div.select_one('span.qzqFw, span.review, span.count, span.rating')
        reviews = review_span.text.strip('()') if review_span else "0"
        
        return f"{rating} ({reviews})"
    except Exception as e:
        print(f"Error getting rating info: {str(e)}")
        return "N/A"

def main():
    query = "Rubiks Cube"
    pages = 2
    query = '+'.join(query.split())
    
    file_name = open(f'daraz-products-{'-'.join(query.split('+'))}.csv', "w", encoding='utf-8')
    writer = csv.writer(file_name)
    writer.writerow(['Product Name', 'Rating', 'Items Sold', 'Selling Price'])
    
    for page in range(1, pages + 1):
        try:
            url = f"https://www.daraz.pk/catalog/?page={page}&q={query}"
            content = get_page_content(url)
            
            if not content:
                print(f"Failed to get content for page {page}")
                continue
                
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find product items
            product_items = soup.select('div[data-qa-locator="product-item"], div.product-item, div.product-card, div.product')
            
            for item in product_items:
                try:
                    # Get product name
                    name_element = item.select_one('div.RfADt a, a.title, div.title a, h2 a, a.name, div.name a')
                    item_name = name_element.get('title', '') if name_element else 'N/A'
                    
                    # Get rating info
                    item_ratings = get_rating_info(item)
                    
                    # Get items sold
                    sold_element = item.select_one('span._1cEkb span, span.sold, span.sales, span.purchase, span.buy')
                    items_sold = sold_element.text if sold_element else 'N/A'
                    
                    # Get price
                    price_element = item.select_one('div.aBrP0 span.ooOxS, div.price span, span.price, div.cost span, span.cost')
                    item_list_price = price_element.text if price_element else 'N/A'
                    
                    writer.writerow([item_name, item_ratings, items_sold, item_list_price])
                    print(f"Processed: {item_name[:50]}...")
                    
                except Exception as e:
                    print(f"Error processing item: {str(e)}")
                    continue
                    
            # Add a small delay between pages
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            print(f"Error processing page {page}: {str(e)}")
            continue
    
    file_name.close()

if __name__ == "__main__":
    main() 