# 🏷️ Adidas.ca Product Scraper

A **Playwright + BeautifulSoup** powered scraper for extracting product data from [adidas.ca](https://www.adidas.ca) — specifically designed for **JavaScript-rendered** product listing pages such as the *Men's Outlet* section.

This scraper:
- Loads the page in a real browser (via Playwright) to ensure all JS-rendered content is available
- Waits for the product grid and cards to fully load
- Scrolls to trigger lazy loading of more products
- Parses the rendered HTML with BeautifulSoup
- Extracts **title**, **original price**, **sale price**, **discount** and **product image** for each product
- Saves the results to a timestamped JSON file

---

## 📂 Project Structure

```
.
├── scraper.py          # Main scraper script
├── products.json       # Output file (generated after run)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## ⚙️ Features

- **Headless or headed browser mode** — run silently or watch the browser in action
- **Stable selectors** — uses `data-testid` attributes instead of fragile CSS class names
- **Lazy-load handling** — scrolls the page to load more products
- **Error handling** — captures screenshots on timeouts or unexpected errors
- **JSON output** — includes scrape timestamp, source URL, and product list

---

## 📦 Requirements

- Python **3.9+**
- [Playwright](https://playwright.dev/python/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [lxml](https://lxml.de/) (optional but faster HTML parsing)

---

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/adidas-scraper.git
   cd adidas-scraper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

---

## 📜 Usage

Run the scraper:

```bash
python scraper.py
```

By default, it will:

1. Launch Firefox (changeable to Chromium or WebKit in code)
2. Navigate to the Men's Outlet page
3. Wait for the product grid and cards to load
4. Scroll to load more products
5. Extract product details
6. Save them to `products.json`

---

## 🛠 Configuration

You can change the target URL in `scraper.py`:

```python
url = 'https://www.adidas.ca/en/men-outlet'
```

You can also:
- Switch browser type (`p.firefox`, `p.chromium`, `p.webkit`)
- Toggle `headless=True` or `False`
- Adjust scroll delay and number of scrolls

---

## 📄 Output Format

Example `products.json`:

```json
{
  "scraped_at": "2025-09-12T23:07:02.392254",
  "source": "https://www.adidas.ca/en/men-outlet",
  "products": [
    {
      "title": "Adizero Adios Pro 4 Shoes",
      "original_price": "300",
      "main_price": "240",
      "discount_percentage": "20",
      "image_url": "https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/9f1917f40b8d4ac6899065e9fd048e94_9366/adizero-adios-pro-4-shoes.jpg"
    },
    {
      "title": "Campus 00s Shoes",
      "original_price": "140",
      "main_price": "98",
      "discount_percentage": "30",
      "image_url": "https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/2345cc874f884fc0a6a8af50010537fb_9366/campus-00s-shoes.jpg"
    },
    {
      "title": "Campus 00s Shoes",
      "original_price": "140",
      "main_price": "98",
      "discount_percentage": "30",
      "image_url": "https://assets.adidas.com/images/w_383,h_383,f_auto,q_auto,fl_lossy,c_fill,g_auto/b562097cb5f34542af86af500104b3cc_9366/campus-00s-shoes.jpg"
    },
}
```

---

## 🚀 How It Works

1. **Launch Browser** — Playwright opens a real browser instance
2. **Navigate & Wait** — waits for `main[data-testid="product-grid"]` to be visible
3. **Scroll** — triggers lazy loading of more products
4. **Extract HTML** — grabs the fully rendered DOM
5. **Parse with BeautifulSoup** — finds `article[data-testid="plp-product-card"]` elements
6. **Extract Data** — pulls title, original price, and sale price
7. **Save JSON** — writes results to `products.json`

---

## 🛡 Error Handling

- **TimeoutError** — If product grid or cards don't load in time, a screenshot is saved (`timeout_error.png`)
- **Unexpected Error** — Any other exception also triggers a screenshot (`error.png`)

---

## 📌 Notes

- This scraper is for **educational and personal use only**
- Always check the target site's Terms of Service before scraping
- Excessive requests may result in IP blocking — use responsibly
- Playwright's `slow_mo` option can be adjusted for debugging

---

## 📜 License

MIT License — feel free to use and modify, but attribution is appreciated.

---

## ✨ Author

**Rakibur** — Full Stack Developer & Team Lead

Specializing in MERN stack, Next.js, TypeScript, Tailwind CSS, React Native, and Python Flask.

Expert in building scalable web/mobile apps, ERP systems, and custom scrapers.
