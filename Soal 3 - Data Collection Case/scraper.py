import httpx
from bs4 import BeautifulSoup
import polars as pl
import asyncio
import json
import os

# Direktori penyimpanan dataset
os.makedirs('datasets', exist_ok=True)

# Fungsi untuk scraping halaman
async def scrape_page(level, page):
    url = f"https://www.fortiguard.com/encyclopedia?type=ips&risk={level}&page={page}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.text
            else:
                return None
    except httpx.RequestError as exc:
        print(f"Error fetching {url}: {exc}")
        return None

# Fungsi untuk mendapatkan jumlah halaman maksimal
def get_max_pages(html, fallback_max=500):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('ul', class_='pagination')
    if pagination:
        pages = pagination.find_all('li')
        if pages:
            # Ambil elemen kedua dari terakhir (biasanya nomor halaman terakhir)
            last_page = pages[-2].text.strip()
            try:
                return int(last_page)
            except ValueError:
                pass  # Jika gagal parsing, gunakan fallback
    # Jika pagination tidak ditemukan atau gagal parsing, gunakan fallback
    return fallback_max

# Fungsi untuk parsing HTML dan ekstraksi title dan link
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', attrs={'onclick': True})

    data = []
    for item in items:
        # Ambil link dari onclick
        onclick_value = item['onclick']
        link = "https://www.fortiguard.com" + onclick_value.split("'")[1]

        # Ambil title dari tag <b>
        title_tag = item.find('b')
        title = title_tag.text.strip() if title_tag else 'No Title'

        data.append((title, link))
    return data

# Fungsi utama untuk scraping semua level dan menyimpan hasil
async def scrape_all_levels():
    skipped_pages = {}
    fallback_max_pages = 500  # Limit fallback default untuk halaman maksimal

    # Loop untuk setiap level
    for level in range(1, 6):
        all_data = []
        skipped = []

        # Dapatkan HTML dari halaman pertama untuk mengetahui jumlah halaman maksimal
        html_first_page = await scrape_page(level, 1)
        if html_first_page:
            # Dapatkan jumlah halaman maksimal dari HTML atau fallback ke 500
            max_pages = get_max_pages(html_first_page, fallback_max=fallback_max_pages)
        else:
            max_pages = fallback_max_pages  # Jika halaman pertama gagal, set ke fallback

        print(f"Scraping level {level}, max pages: {max_pages}")

        # Loop untuk setiap halaman di level
        for page in range(1, max_pages + 1):
            html = await scrape_page(level, page)
            if html:
                data = parse_html(html)
                all_data.extend(data)
            else:
                skipped.append(page)

        # Simpan hasil ke CSV
        df = pl.DataFrame(all_data, schema={"title": pl.Utf8, "link": pl.Utf8})
        df.write_csv(f'datasets/forti_lists_{level}.csv')

        # Catat halaman yang dilewati
        if skipped:
            skipped_pages[level] = skipped

    # Simpan halaman yang dilewati ke JSON
    if skipped_pages:
        with open('datasets/skipped.json', 'w') as f:
            json.dump(skipped_pages, f, indent=4)

# Jalankan fungsi utama dengan asyncio
if __name__ == "__main__":
    asyncio.run(scrape_all_levels())
