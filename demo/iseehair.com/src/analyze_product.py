"""分析商品结构，找出商品名称的位置"""

from httpclient import HttpClient
from bs4 import BeautifulSoup
import re

client = HttpClient()
resp = client.get('https://www.iseehair.com/half-wig.html')
soup = BeautifulSoup(resp.text, 'html.parser')

# 找一个商品链接
product_link = soup.find('a', href=re.compile(r'isee-coily-curly-half-wig'))

if product_link:
    print("找到商品链接:")
    print(f"href: {product_link.get('href')}")
    print(f"\n链接本身的HTML:")
    print(product_link.prettify()[:500])
    
    print(f"\n\n父元素的HTML:")
    if product_link.parent:
        print(product_link.parent.prettify()[:1000])
        
        # 在父元素中查找所有文本
        print(f"\n\n父元素中的所有文本内容:")
        for i, text in enumerate(product_link.parent.stripped_strings, 1):
            if len(text) > 3:
                print(f"  {i}. {text}")
