"""爬取网站所有商品信息(支持分页)"""

import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from httpclient import HttpClient
from config import BASE_URL
from saver import save_to_json


class ProductScraper:
    """商品爬虫类，按分类分页抓取商品"""

    def __init__(self):
        self.client = HttpClient()
        self.products: List[Dict[str, Any]] = []
        self.visited_urls = set()

    def _build_page_url(self, category_url: str, page: int) -> str:
        if page <= 1:
            return category_url
        if '?' in category_url:
            return f"{category_url}&p={page}"
        return f"{category_url}?p={page}"

    def scrape_category_products(self, category_url: str, category_name: str, max_pages: int = 10) -> List[Dict[str, Any]]:
        """爬取某个分类下的所有商品(支持简单分页)

        Args:
            category_url: 分类URL
            category_name: 分类名称
            max_pages: 最大页数（防止无限循环）

        Returns:
            商品信息列表
        """
        print(f"正在爬取分类: {category_name}")
        all_products: List[Dict[str, Any]] = []

        for page in range(1, max_pages + 1):
            page_url = self._build_page_url(category_url, page)

            if page_url in self.visited_urls:
                print(f"  跳过已访问的URL: {page_url}")
                continue

            self.visited_urls.add(page_url)
            print(f"  爬取第 {page} 页: {page_url}")

            try:
                resp = self.client.get(page_url)
                soup = BeautifulSoup(resp.text, 'html.parser')

                page_products: List[Dict[str, Any]] = []

                # 优先选择带图片的链接，通常为商品链接
                anchors = [a for a in soup.find_all('a', href=re.compile(r'\.html$')) if a.find('img')]

                for a in anchors:
                    href = a.get('href', '').strip()
                    if not href or href == '#' or href == category_url:
                        continue

                    # 构建绝对URL
                    if href.startswith('/'):
                        product_url = urljoin(BASE_URL, href)
                    elif href.startswith('http'):
                        product_url = href
                    else:
                        # 相对路径或其它非标准链接跳过
                        continue

                    low = href.lower()
                    skip_patterns = ['privacy', 'terms', 'about', 'contact', 'faq', 'blog', 'cart', 'checkout', 'account', 'login', 'register']
                    if any(p in low for p in skip_patterns):
                        continue

                    # 商品名称提取策略：
                    # 1. 尝试从链接文本提取（排除图片alt）
                    name = ''
                    text = a.get_text(strip=True)
                    if text and len(text) > 10 and 'wig' in text.lower():
                        name = text
                    
                    # 2. 如果没有，从URL提取（移除前缀和后缀，转为标题格式）
                    if not name:
                        # 从URL提取：/isee-water-wave-half-wig-...html -> Water Wave Half Wig
                        url_name = href.replace('.html', '').split('/')[-1]
                        if url_name.startswith('isee-'):
                            url_name = url_name[5:]  # 移除 'isee-' 前缀
                        # 将连字符替换为空格，每个单词首字母大写
                        name_parts = url_name.split('-')
                        # 过滤掉常见的连接词
                        filtered_parts = [p.capitalize() for p in name_parts if p not in ['for', 'with', 'the', 'and', 'or']]
                        name = ' '.join(filtered_parts)

                    if not name or len(name) < 5:
                        continue

                    # 尝试寻找价格
                    price = ''
                    old_price = ''
                    parent = a.parent
                    if parent:
                        price_elem = parent.find(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
                        if price_elem:
                            txt = price_elem.get_text(' ', strip=True)
                            matches = re.findall(r'\$[\d,]+\.?\d*', txt)
                            if matches:
                                price = matches[0]
                                if len(matches) > 1:
                                    old_price = matches[1]

                    if not price:
                        next_price_text = a.find_next(string=re.compile(r'\$[\d,]+\.?\d*'))
                        if next_price_text:
                            m = re.search(r'\$[\d,]+\.?\d*', next_price_text)
                            if m:
                                price = m.group(0)

                    # 图片URL
                    img = a.find('img')
                    image_url = ''
                    if img:
                        image_url = img.get('src') or img.get('data-src') or img.get('data-lazy') or ''
                        if image_url and not image_url.startswith('http'):
                            image_url = urljoin(BASE_URL, image_url)

                    product = {
                        'name': name,
                        'url': product_url,
                        'price': price,
                        'old_price': old_price,
                        'image': image_url,
                        'category': category_name,
                        'category_url': category_url
                    }

                    if not any(p['url'] == product['url'] for p in page_products):
                        page_products.append(product)

                print(f"    第 {page} 页找到 {len(page_products)} 个商品")
                if not page_products:
                    print(f"    第 {page} 页无商品，停止爬取")
                    break

                all_products.extend(page_products)

            except Exception as e:
                print(f"    爬取第 {page} 页失败: {e}")
                break

        print(f"  分类 {category_name} 共找到 {len(all_products)} 个商品")
        return all_products

    def scrape_all_products(self, categories: List[Dict[str, Any]], max_pages_per_category: int = 10) -> List[Dict[str, Any]]:
        print(f"开始爬取所有商品，共 {len(categories)} 个分类...")
        print(f"每个分类最多爬取 {max_pages_per_category} 页")

        for i, category in enumerate(categories, 1):
            print(f"\n进度: {i}/{len(categories)}")
            products = self.scrape_category_products(category['url'], category['name'], max_pages=max_pages_per_category)
            self.products.extend(products)

        # 全局去重
        unique = []
        seen = set()
        for p in self.products:
            if p['url'] not in seen:
                unique.append(p)
                seen.add(p['url'])
        self.products = unique
        print(f"\n共爬取到 {len(self.products)} 个不重复的商品")
        return self.products

    def save_products(self, filename: str = "products.json"):
        save_to_json(self.products, filename)
        print(f"商品数据已保存到: {filename}")


def main():
    try:
        with open("../data/categories.json", "r", encoding="utf-8") as f:
            categories = json.load(f)
    except FileNotFoundError:
        print("错误: 未找到分类数据文件，请先运行 menu.py")
        return

    scraper = ProductScraper()
    # 爬取所有分类，每个分类最多爬取20页
    products = scraper.scrape_all_products(categories, max_pages_per_category=20)
    scraper.save_products()

    print("\n=== 商品统计 ===")
    print(f"总商品数: {len(products)}")

    # 按分类统计
    stats = {}
    for prod in products:
        cat = prod.get('category', 'Unknown')
        stats[cat] = stats.get(cat, 0) + 1

    print("\n各分类商品数:")
    for cat, cnt in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {cnt}")

    # 打印前5个商品
    print("\n前5个商品:")
    for i, prod in enumerate(products[:5], 1):
        print(f"\n{i}. {prod['name']}")
        print(f"   价格: {prod.get('price','')}")
        if prod.get('old_price'):
            print(f"   原价: {prod.get('old_price')}")
        print(f"   分类: {prod.get('category')}")
        print(f"   链接: {prod.get('url')}")


if __name__ == "__main__":
    main()
    
    # 创建商品爬虫
    scraper = ProductScraper()
    
    # 爬取所有商品(每个分类爬取3页作为示例)
    products = scraper.scrape_all_products(categories[:5], max_pages_per_category=3)
    
    # 保存商品数据
    scraper.save_products()
    
    # 打印统计信息
    print("\n=== 商品统计 ===")
    print(f"总商品数: {len(products)}")
    
    # 按分类统计
    category_stats = {}
    for product in products:
        category = product.get('category', 'Unknown')
        category_stats[category] = category_stats.get(category, 0) + 1
    
    print("\n各分类商品数:")
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count}")
    
    # 显示前5个商品
    print("\n前5个商品:")
    for i, product in enumerate(products[:5], 1):
        print(f"\n{i}. {product['name']}")
        print(f"   价格: {product['price']}")
        if product['old_price']:
            print(f"   原价: {product['old_price']}")
        if product['rating']:
            print(f"   评分: {product['rating']}")
        print(f"   分类: {product['category']}")
        print(f"   链接: {product['url']}")


if __name__ == "__main__":
    main()
