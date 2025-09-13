from bs4 import BeautifulSoup
import re
from playwright.sync_api import sync_playwright, TimeoutError
import json
from datetime import datetime
import time
import urllib.parse

# The URL you are actually targeting
url = 'https://www.adidas.ca/en/men-outlet'

def extract_product_sizes(page):
    """Extract available sizes from product detail page."""
    sizes = []
    try:
        # Wait for the size selector to load
        size_selector = page.wait_for_selector('div[data-auto-id="size-selector"]', timeout=10000)
        
        if size_selector:
            # Get all size buttons
            size_buttons = page.query_selector_all('div[data-auto-id="size-selector"] button[role="radio"]')
            
            for button in size_buttons:
                # Get the size text from the button
                size_text = button.inner_text().strip()
                if size_text:
                    sizes.append(size_text)
        
    except TimeoutError:
        print("Size selector not found or timed out")
    except Exception as e:
        print(f"Error extracting sizes: {str(e)}")
    
    return sizes

def extract_product_details(card, page_context):
    """Extract details from a single product card."""
    # Extract the title
    title_tag = card.select_one('p[data-testid="product-card-title"]')
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    # Extract the original price
    original_price_tag = card.select_one('div[data-testid="original-price"] span')
    original_price = None
    if original_price_tag:
        text = original_price_tag.get_text(strip=True)
        match = re.search(r'C\$\s*(\d+(?:\.\d+)?)', text)
        original_price = match.group(1) if match else None

    # Extract the main price
    main_price_tag = card.select_one('div[data-testid="main-price"] span:not([class="_visuallyHidden_1dryf_2"])')
    main_price = None
    if main_price_tag:
        text = main_price_tag.get_text(strip=True)
        match = re.search(r'C\$\s*(\d+(?:\.\d+)?)', text)
        main_price = match.group(1) if match else None

    # Extract the discount percentage
    discount_tag = card.select_one('span[data-testid="discount-text"][class="_discountText_1dryf_91"]')
    discount = discount_tag.get_text(strip=True) if discount_tag else None
    if discount:
        # Remove quotes and % sign, just get the number
        match = re.search(r'"?-?(\d+)%"?', discount)
        discount = match.group(1) if match else None

    # Extract the main product image
    img_tag = card.select_one('img[data-testid="product-card-primary-image"]')
    image_url = img_tag.get('src') if img_tag else None

    # Extract the product description link
    description_link_tag = card.select_one('a[data-testid="product-card-description-link"]')
    description_link = None
    product_sizes = []
    
    if description_link_tag:
        description_link = description_link_tag.get('href')
        if description_link:
            # Make it absolute URL if it's relative
            if description_link.startswith('/'):
                description_link = f"https://www.adidas.ca{description_link}"
            
            # Now scrape the product sizes from the detail page
            print(f"Scraping sizes for: {title}")
            try:
                # Create a new page for product detail
                detail_page = page_context.new_page()
                detail_page.goto(description_link, wait_until="domcontentloaded")
                
                # Extract sizes
                product_sizes = extract_product_sizes(detail_page)
                print(f"Found {len(product_sizes)} sizes: {product_sizes}")
                
                # Close the detail page
                detail_page.close()
                
                # Add a small delay to avoid overwhelming the server
                time.sleep(1)
                
            except Exception as e:
                print(f"Error scraping product detail page for {title}: {str(e)}")
                if 'detail_page' in locals():
                    detail_page.close()

    return {
        "title": title,
        "original_price": original_price,
        "main_price": main_price,
        "discount_percentage": discount,
        "image_url": image_url,
        "description_link": description_link,
        "available_sizes": product_sizes
    }

def save_to_json(products):
    """Save products data to JSON file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create the data structure
    data = {
        "scraped_at": datetime.now().isoformat(),
        "source": url,
        "total_products": len(products),
        "products": products
    }
    
    # Save to file
    try:
        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✓ Data successfully saved to products.json")
    except Exception as e:
        print(f"Error saving to JSON: {str(e)}")

def get_next_page_url(page):
    """Extract the next page URL if it exists."""
    # Check if we can find the total pages
    page_indicator = page.query_selector('span[data-testid="page-indicator"]')
    if not page_indicator:
        return None
    
    # Extract current page and total pages from the text (e.g., "Page: 1 of 16")
    indicator_text = page_indicator.inner_text()
    match = re.search(r'Page:\s*(\d+)\s*of\s*(\d+)', indicator_text)
    if not match:
        return None
    
    current_page = int(match.group(1))
    total_pages = int(match.group(2))
    
    # Check if we're on the last page
    if current_page >= total_pages:
        return None
    
    # Construct next page URL
    parsed_url = urllib.parse.urlparse(page.url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    # Calculate the start parameter (48 items per page)
    next_start = current_page * 48
    query_params['start'] = [str(next_start)]
    
    # Construct the URL
    new_query = urllib.parse.urlencode(query_params, doseq=True)
    if new_query:
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
    else:
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?start={next_start}"

def scrape_page(page, context):
    """Scrape a single page of products."""
    # Add wait for pagination element
    print("Waiting for page content to load...")
    page.wait_for_selector('span[data-testid="page-indicator"]', timeout=45000)
    
    # Wait for product grid
    print("Waiting for product grid...")
    grid = page.wait_for_selector('main[data-testid="product-grid"]', 
                                state="visible", 
                                timeout=45000)
    
    if not grid:
        raise TimeoutError("Product grid not found")

    # Scroll to load all products
    for _ in range(3):  # Scroll multiple times to ensure all content loads
        page.evaluate("""
            window.scrollTo({
                top: document.body.scrollHeight,
                behavior: 'smooth'
            });
        """)
        time.sleep(1)
    
    # Scroll back to top
    page.evaluate("window.scrollTo(0, 0);")
    time.sleep(1)
    
    # Get the page content
    html_content = page.content()
    
    # Process the content
    soup = BeautifulSoup(html_content, 'html.parser')
    product_cards = soup.select('article[data-testid="plp-product-card"]')
    
    return [extract_product_details(card, context) for card in product_cards]

def main():
    print("Starting enhanced scraper for Adidas with product details and sizes...")
    all_products = []
    current_page = 1
    
    with sync_playwright() as p:
        browser = p.firefox.launch(
            headless=False,
            slow_mo=100
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/116.0'
        )
        
        page = context.new_page()
        current_url = url

        try:
            while current_url:
                print(f"\n=== Processing page {current_page} ===")
                page.goto(current_url, wait_until="domcontentloaded")
                
                # Scrape current page
                page_products = scrape_page(page, context)
                all_products.extend(page_products)
                print(f"Found {len(page_products)} products on page {current_page}")
                
                # Check for next page
                # next_url = get_next_page_url(page)
                next_url = None
                if next_url:
                    current_url = urllib.parse.urljoin(url, next_url)
                    current_page += 1
                    print(f"Found next page: {current_url}")
                    # Add small delay between pages
                    time.sleep(3)
                else:
                    current_url = None
                    print("No more pages found")

        except TimeoutError as e:
            print(f"Timeout Error: {str(e)}")
            page.screenshot(path=f"timeout_error_page_{current_page}.png")
        except Exception as e:
            print(f"Unexpected error on page {current_page}: {str(e)}")
            page.screenshot(path=f"error_page_{current_page}.png")
        finally:
            context.close()
            browser.close()

        # Save all products if any were collected
        if all_products:
            print(f"\n=== SCRAPING COMPLETE ===")
            print(f"Total products collected: {len(all_products)}")
            
            # Count products with sizes
            products_with_sizes = [p for p in all_products if p.get('available_sizes')]
            print(f"Products with sizes collected: {len(products_with_sizes)}")
            
            save_to_json(all_products)
            
            # Print sample of results
            print("\nSample of extracted products:")
            for i, product in enumerate(all_products[:2]):
                print(f"\n--- Product {i+1} ---")
                print(json.dumps(product, indent=2))

if __name__ == "__main__":
    main()