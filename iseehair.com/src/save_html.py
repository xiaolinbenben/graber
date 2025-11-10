"""保存页面HTML用于分析"""
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://www.iseehair.com/half-wig.html'
response = requests.get(
    url,
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
    timeout=30,
    verify=False
)

with open('../data/page_source.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print(f"HTML已保存，总长度: {len(response.text)} 字符")
print("\n查找关键词:")
print(f"  'product': {response.text.count('product')}")
print(f"  'data-': {response.text.count('data-')}")
print(f"  'script': {response.text.count('<script')}")
print(f"  'isee-': {response.text.count('isee-')}")
