"""测试商品名称提取"""

import json
from products import ProductScraper

# 读取分类数据
with open("../data/categories.json", "r", encoding="utf-8") as f:
    categories = json.load(f)

# 只测试第一个分类的前2页
scraper = ProductScraper()
products = scraper.scrape_category_products(
    categories[0]['url'], 
    categories[0]['name'],
    max_pages=2
)

print(f"\n测试结果：共找到 {len(products)} 个商品")
print("\n前10个商品信息：")
for i, prod in enumerate(products[:10], 1):
    print(f"\n{i}. 名称: {prod['name']}")
    print(f"   价格: {prod.get('price', 'N/A')}")
    print(f"   链接: {prod['url']}")
