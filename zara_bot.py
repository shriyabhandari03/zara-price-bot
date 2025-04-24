import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# Your working Telegram credentials
TOKEN = "YOUR_REAL_BOT_TOKEN_HERE"
CHAT_ID = "1145564175"
bot = Bot(token=TOKEN)

# Track old prices
price_cache = {}

# Zara Women's Dresses URL
ZARA_URLS = [
    "https://www.zara.com/in/en/woman-trend-79-l6027.html?v1=2420823&ex01=2420896&ex02=1066&regionGroupId=230",  # Dresses
    "https://www.zara.com/in/en/woman-tops-l1322.html?v1=2419940&regionGroupId=230",  # Tops & Bodysuits
    "https://www.zara.com/in/en/woman-jeans-l1119.html?v1=2419185&regionGroupId=230",  # Jeans
    "https://www.zara.com/in/en/woman-tshirts-l1362.html?v1=2420417&regionGroupId=230",  # T-Shirts
    "https://www.zara.com/in/en/woman-blazers-l1055.html?v1=2420942&regionGroupId=230",  # Blazers
    "https://www.zara.com/in/en/woman-trend-20-l1900.html?v1=2420370&ex01=2420369&ex02=1217&regionGroupId=230",  # Shirts
    "https://www.zara.com/in/en/woman-cardigans-sweaters-l8322.html?v1=2419844&regionGroupId=230",  # Cardigans & Sweaters
    "https://www.zara.com/in/en/woman-skirts-l1299.html?v1=2420454&regionGroupId=230",  # Skirts
    "https://www.zara.com/in/en/woman-trend-21-l1905.html?v1=2420796&ex01=2420795&ex02=1335&regionGroupId=230",  # Trousers
    "https://www.zara.com/in/en/woman-trousers-shorts-l1355.html?v1=2420480&regionGroupId=230",  # Shorts / Skorts
    "https://www.zara.com/in/en/woman-co-ords-l1061.html?v1=2420285&regionGroupId=230",  # Co-ord Sets
    "https://www.zara.com/in/en/woman-shoes-l1251.html?v1=2445834&regionGroupId=230",  # Shoes
    "https://www.zara.com/in/en/woman-bags-l1024.html?v1=2417728&regionGroupId=230",  # Bags
    "https://www.zara.com/in/en/woman-special-prices-l1314.html?v1=2419737&regionGroupId=230"  # Special Prices
]


# Scrape Zara page
async def scrape_zara():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(ZARA_URLS, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    products = soup.find_all("div", class_="product-grid-product")

    for product in products:
        name_tag = product.find("a", class_="product-link _item")
        if not name_tag:
            continue

        name = name_tag.text.strip()
        url = "https://www.zara.com" + name_tag.get("href")

        price_tag = product.find("span", class_="money-amount__main")
        if not price_tag:
            continue

        price_text = price_tag.text.replace("₹", "").replace(",", "").strip()
        try:
            price = int(float(price_text))
        except:
            continue

        # Check if price dropped by 50% or more
        if name in price_cache:
            old_price = price_cache[name]
            drop_pct = (old_price - price) / old_price * 100

            if drop_pct >= 50:
                message = f"⚠️ Price Drop Alert\n{name}\nOld: ₹{old_price}\nNow: ₹{price}\n{url}"
                await bot.send_message(chat_id=CHAT_ID, text=message)

        price_cache[name] = price

# Loop every 5 mins
async def main_loop():
    while True:
        await scrape_zara()
        await asyncio.sleep(300)  # Wait 5 minutes

asyncio.run(main_loop())
