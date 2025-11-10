"""查找产品列表容器"""

from httpclient import HttpClient
from bs4 import BeautifulSoup
import re

client = HttpClient()
resp = client.get('https://www.iseehair.com/half-wig.html')
soup = BeautifulSoup(resp.text, 'html.parser')

# 查找产品URL模式
product_url = 'isee-99j-burgundy-color-pre-styled-kinky-curly-half-wig'

# 在整个页面中搜索这个URL
all_links = soup.find_all('a', href=re.compile(product_url))

print(f"找到 {len(all_links)} 个包含此产品URL的链接\n")

for i, link in enumerate(all_links, 1):
    print(f"\n=== 链接 {i} ===")
    print(f"href: {link.get('href')[:80]}")
    print(f"text: {link.get_text(strip=True)[:100]}")
    print(f"title: {link.get('title', '')[:100]}")
    
    # 检查父元素
    if link.parent:
        parent_text = link.parent.get_text(strip=True)[:150]
        print(f"parent text: {parent_text}")
        
    if i >= 3:
        break

# 再找找是否有产品列表容器
print("\n\n=== 查找可能的产品列表容器 ===")
product_containers = soup.find_all(['div', 'li', 'article'], class_=re.compile(r'product|item|card', re.I))
print(f"找到 {len(product_containers)} 个可能的产品容器")

if product_containers:
    print(f"\n第一个产品容器的内容:")
    print(product_containers[0].prettify()[:800])
