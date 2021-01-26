import requests
import pandas as pd
from bs4 import BeautifulSoup

cookies = {
    '_ga': 'GA1.3.22250053.1596163036',
    '_gcl_au': '1.1.1150676965.1605128075',
    '_gid': 'GA1.3.2096215875.1611324575',
    'has_js': '1',
    '_gat': '1',
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en,en-US;q=0.9,vi;q=0.8',
}

response = requests.get('https://student.uit.edu.vn/danh-muc-mon-hoc-dai-hoc', headers=headers, cookies=cookies)

soup = BeautifulSoup(response.text, 'html.parser')
table_MN = pd.read_html(response.text)
course_name = table_MN[0] # DataFrame