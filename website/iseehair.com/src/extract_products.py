"""从页面文本内容中提取商品信息"""

from httpclient import HttpClient
from bs4 import BeautifulSoup
import re

client = HttpClient()
resp = client.get('https://www.iseehair.com/half-wig.html')
soup = BeautifulSoup(resp.text, 'html.parser')

# 查找所有包含商品URL的链接
product_links = soup.find_all('a', href=re.compile(r'/isee-.*-wig.*\.html$'))

print(f"找到 {len(product_links)} 个商品链接\n")

# 对每个链接，查找其完整的产品信息
seen_urls = set()
products = []

for link in product_links:
    href = link.get('href', '')
    if not href or href in seen_urls:
        continue
    
    # 过滤掉非商品页面
    if any(x in href.lower() for x in ['clearance', 'flash', 'sale', 'best-seller', 'new-arrival', 'wholesale']):
        continue
        
    seen_urls.add(href)
    
    # 尝试多种方式提取商品名称
    name = ''
    
    # 方法1: 查找包含此链接的父元素中的文本
    parent = link.parent
    while parent and not name:
        # 在父元素中查找所有链接
        links_in_parent = parent.find_all('a', href=href)
        for l in links_in_parent:
            # 获取链接文本（不是图片alt）
            text = l.get_text(strip=True)
            if text and len(text) > 10 and 'half wig' not in text.lower():
                name = text
                break
        
        if not name and parent.parent:
            parent = parent.parent
        else:
            break
    
    # 方法2: 从URL中推断名称
    if not name:
        # 从URL提取：isee-water-wave-half-wig-...html -> Water Wave Half Wig
        url_parts = href.replace('.html', '').replace('/isee-', '').replace('-', ' ').split()
        name = ' '.join(word.capitalize() for word in url_parts if word not in ['for', 'with', 'the', 'and'])
    
    products.append({'name': name, 'url': href})

print(f"提取到 {len(products)} 个商品\n")
print("前10个商品:")
for i, prod in enumerate(products[:10], 1):
    print(f"{i}. {prod['name'][:80]}")
    print(f"   {prod['url'][:80]}\n")
