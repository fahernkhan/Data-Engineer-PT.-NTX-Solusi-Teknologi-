# Data Collection Challenge for DE Technical Test

## 1. Pendahuluan

Proyek ini bertujuan untuk mengumpulkan data dari situs web Fortiguard, secara khusus dari halaman yang berkaitan dengan ancaman keamanan. Proses ini dilakukan dengan melakukan scraping pada setiap level risiko dan mengumpulkan data berupa `title` (judul artikel) dan `link` (tautan langsung ke artikel). Proyek ini dirancang untuk melakukan scraping secara asinkron dan menangani potensi error seperti koneksi gagal, timeouts, dan pagination dinamis.

## 2. Teknologi yang Digunakan

- **Python 3.x**
- **Libraries**:
  - `httpx`: Untuk melakukan permintaan HTTP secara asinkron.
  - `BeautifulSoup4`: Untuk parsing dan mengekstrak data dari HTML.
  - `polars`: Untuk menyimpan data dalam format CSV.
  - `tqdm`: Untuk progress bar saat scraping (opsional).
  - `json`: Untuk mencatat halaman yang dilewati (skipped pages).

## 3. Arsitektur dan Alur Kerja

### 3.1 Input
Situs web target adalah Fortiguard dengan struktur URL sebagai berikut:


Dimana:
- `level`: Merupakan level risiko (nilai dari 1 hingga 5).
- `page`: Nomor halaman (mulai dari 1 hingga jumlah halaman maksimal).

### 3.2 Output
- **Dataset**: Hasil scraping akan disimpan dalam format CSV untuk setiap level risiko di direktori `datasets/`. Setiap file CSV akan berisi dua kolom:
  - `title`: Judul artikel.
  - `link`: Tautan ke artikel di situs web.
- **Skipped Pages**: Halaman-halaman yang gagal di-scrape karena error akan dicatat dalam file `skipped.json` di dalam direktori yang sama.

### 3.3 Tahapan Utama
1. **Scraping**: Proses scraping dilakukan secara asinkron menggunakan `httpx` untuk meningkatkan efisiensi. Scraping dilakukan untuk 5 level risiko yang berbeda.
2. **Ekstraksi Data**: Setiap halaman yang berhasil diambil akan diproses dengan `BeautifulSoup` untuk mengekstrak `title` dan `link`.
3. **Penanganan Pagination**: Jumlah halaman akan diambil dari situs web, dengan fallback ke batas maksimal (500 halaman) jika terjadi error atau jika tidak ada pagination.
4. **Error Handling**: Jika halaman gagal diambil, maka halaman tersebut dicatat sebagai halaman yang dilewati, dan proses scraping tetap berlanjut.

## 4. Instalasi dan Persiapan

### 4.1 Instalasi
Pastikan Python 3.x telah terpasang. Selanjutnya, instal dependencies yang dibutuhkan dengan perintah berikut:

```bash
pip install httpx BeautifulSoup4 polars tqdm
```

Dimana:
- `level`: Merupakan level risiko (nilai dari 1 hingga 5).
- `page`: Nomor halaman (mulai dari 1 hingga jumlah halaman maksimal).

### 3.2 Output
- **Dataset**: Hasil scraping akan disimpan dalam format CSV untuk setiap level risiko di direktori `datasets/`. Setiap file CSV akan berisi dua kolom:
  - `title`: Judul artikel.
  - `link`: Tautan ke artikel di situs web.
- **Skipped Pages**: Halaman-halaman yang gagal di-scrape karena error akan dicatat dalam file `skipped.json` di dalam direktori yang sama.

### 3.3 Tahapan Utama
1. **Scraping**: Proses scraping dilakukan secara asinkron menggunakan `httpx` untuk meningkatkan efisiensi. Scraping dilakukan untuk 5 level risiko yang berbeda.
2. **Ekstraksi Data**: Setiap halaman yang berhasil diambil akan diproses dengan `BeautifulSoup` untuk mengekstrak `title` dan `link`.
3. **Penanganan Pagination**: Jumlah halaman akan diambil dari situs web, dengan fallback ke batas maksimal (500 halaman) jika terjadi error atau jika tidak ada pagination.
4. **Error Handling**: Jika halaman gagal diambil, maka halaman tersebut dicatat sebagai halaman yang dilewati, dan proses scraping tetap berlanjut.

## 4. Instalasi dan Persiapan

### 4.1 Instalasi
Pastikan Python 3.x telah terpasang. Selanjutnya, instal dependencies yang dibutuhkan dengan perintah berikut:

```bash
pip install httpx BeautifulSoup4 polars tqdm
```

### 4.2 Struktur Direktori
.
├── datasets/                   # Direktori tempat menyimpan output
├── scraper.py                  # File Python untuk melakukan scraping
├── Dokumentasi-Pengerjaan.md   # Dokumentasi pengerjaan proyek ini
└── README.md                   # Dokumentasi proyek ini

## 5. Implementasi
Berikut adalah penjelasan dari implementasi proyek scraping ini:

### 5.1 Fungsi scrape_page
Fungsi ini digunakan untuk melakukan permintaan HTTP secara asinkron ke halaman target dan mengambil konten HTML.

```python
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
```

### 5.2 Fungsi get_max_pages
Fungsi ini mengekstrak jumlah halaman maksimal dari HTML untuk setiap level risiko. Jika pagination gagal ditemukan, digunakan fallback limit.

```python
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
```

### 5.3 Fungsi parse_html
Fungsi ini melakukan parsing HTML untuk mengekstrak title dan link.

```python
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

```

### 5.3 Fungsi scrape_all_levels
Fungsi ini mengatur proses scraping untuk semua level risiko dan menyimpan data ke CSV serta halaman yang gagal di-scrape ke file JSON.

```python
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
```

## 6. Penggunaan
Pastikan semua dependencies telah terinstal. Jalankan script scraper.py menggunakan Python.

```bash
python scraper.py
```
Proses scraping akan berlangsung dan hasilnya akan disimpan di direktori datasets/ dengan format berikut:

1. forti_lists_{level}.csv: CSV file untuk setiap level risiko (1-5) berisi kolom title dan link.
2. skipped.json: JSON file berisi halaman-halaman yang dilewati.

Dimana:
- `level`: Merupakan level risiko (nilai dari 1 hingga 5).
- `page`: Nomor halaman (mulai dari 1 hingga jumlah halaman maksimal).

## 7. Error Handling

- Jika terjadi kesalahan jaringan atau halaman tidak dapat diakses, skrip akan mencatat halaman tersebut dalam file skipped.json.
- Fallback pagination akan digunakan jika jumlah halaman maksimal tidak dapat ditemukan.

## 8. Performa dan Efisiensi

- Scraping dilakukan secara asinkron menggunakan httpx, yang memungkinkan banyak permintaan dilakukan bersamaan, meningkatkan efisiensi waktu scraping.
- Hanya halaman-halaman yang gagal akan dicatat sebagai skipped, dan skrip akan tetap melanjutkan scraping untuk halaman lainnya.


### Penjelasan:
- **Pendahuluan**: Gambaran umum tentang proyek dan tujuan.
- **Arsitektur dan Alur Kerja**: Memberikan detail mengenai input, output, dan tahapan utama scraping.
- **Implementasi**: Berisi penjelasan dan kode untuk fungsi-fungsi utama yang digunakan.
- **Penggunaan**: Langkah-langkah untuk menjalankan proyek.
- **Error Handling**: Menjelaskan bagaimana skrip menangani error.
- **Performa dan Efisiensi**: Menjelaskan pendekatan asinkron untuk meningkatkan efisiensi.

Dokumentasi ini mencakup seluruh proses mulai dari pengaturan, implementasi, hingga cara penggunaan dan lisensi proyek.