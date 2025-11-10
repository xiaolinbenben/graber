"""分析页面结构，找出真正的商品链接"""

from httpclient import HttpClient
from bs4 import BeautifulSoup
import re

client = HttpClient()
resp = client.get('https://www.iseehair.com/half-wig.html')
soup = BeautifulSoup(resp.text, 'html.parser')

# 查找所有带图片的链接
links_with_img = [a for a in soup.find_all('a', href=re.compile(r'\.html$')) if a.find('img')]

print(f'Total links with images: {len(links_with_img)}\n')

print('First 15 links with images:')
for i, a in enumerate(links_with_img[:15], 1):
    href = a.get('href', '')
    text = a.get_text(strip=True)
    title = a.get('title', '')
    img = a.find('img')
    img_alt = img.get('alt', '') if img else ''
    
    print(f'\n{i}. href: {href[:60]}')
    print(f'   title: {title[:60]}')
    print(f'   text: {text[:60]}')
    print(f'   img_alt: {img_alt[:60]}')
    
    # 检查是否是商品详情链接
    is_product = 'isee-' in href.lower() and any(x in href.lower() for x in ['wig', 'hair', 'bundle', 'lace'])
    print(f'   is_product: {is_product}')
