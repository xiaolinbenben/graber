"""
爬取网站所有商品信息
"""

import json
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from httpclient import HttpClient
from config import BASE_URL
from saver import save_to_json


class ProductScraper:
    """商品爬虫类"""
    
    def __init__(self):
        self.client = HttpClient()
        self.products = []
        self.visited_urls = set()
        
    def scrape_category_products(self, category_url: str, category_name: str) -> List[Dict[str, Any]]:
        """
        爬取某个分类下的所有商品
        
        Args:
            category_url: 分类URL
            category_name: 分类名称
            
        Returns:
            商品列表
        """
        print(f"正在爬取分类: {category_name} ({category_url})")
        
        if category_url in self.visited_urls:
            print(f"跳过已访问的URL: {category_url}")
            return []
            
        self.visited_urls.add(category_url)
        
        try:
            response = self.client.get(category_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            products = []
            
            # 方法1: 查找商品列表容器
            product_items = soup.find_all(['div', 'li'], class_=re.compile(r'product|item', re.I))
            
            for item in product_items:
                product = self._parse_product_item(item, category_name)
                if product:
                    products.append(product)
                    
            # 方法2: 查找所有商品链接
            product_links = soup.find_all('a', href=re.compile(r'\.html$'))
            
            for link in product_links:
                href = link.get('href', '')
                
                # 过滤非商品页面
                if any(keyword in href.lower() for keyword in [
                    'privacy', 'terms', 'about', 'contact', 'faq', 'blog', 
                    'cart', 'checkout', 'account', 'category', 'collection'
                ]):
                    continue
                
                # 构建完整URL
                if href.startswith('/'):
                    product_url = BASE_URL + href
                elif href.startswith('http'):
                    product_url = href
                else:
                    continue
                    
                # 获取商品名称
                product_name = link.get_text(strip=True)
                
                if product_name and len(product_name) > 5:  # 过滤太短的名称
                    # 查找价格信息
                    price_elem = link.find_next(['span', 'div'], class_=re.compile(r'price', re.I))
                    price = price_elem.get_text(strip=True) if price_elem else ""
                    
                    # 查找图片
                    img = link.find('img')
                    image_url = img.get('src', '') or img.get('data-src', '') if img else ""
                    if image_url and not image_url.startswith('http'):
                        image_url = urljoin(BASE_URL, image_url)
                    
                    product = {
                        'name': product_name,
                        'url': product_url,
                        'price': price,
                        'image': image_url,
                        'category': category_name,
                        'category_url': category_url
                    }
                    
                    # 避免重复
                    if not any(p['url'] == product_url for p in products):
                        products.append(product)
            
            print(f"从分类 {category_name} 中找到 {len(products)} 个商品")
            return products
            
        except Exception as e:
            print(f"爬取分类 {category_name} 失败: {e}")
            return []
    
    def _parse_product_item(self, item: BeautifulSoup, category_name: str) -> Optional[Dict[str, Any]]:
        """
        解析商品项
        
        Args:
            item: BeautifulSoup对象
            category_name: 分类名称
            
        Returns:
            商品信息字典
        """
        try:
            # 查找商品链接
            link = item.find('a', href=True)
            if not link:
                return None
                
            href = link.get('href', '')
            if not href or not href.endswith('.html'):
                return None
                
            # 构建完整URL
            if href.startswith('/'):
                product_url = BASE_URL + href
            elif href.startswith('http'):
                product_url = href
            else:
                return None
            
            # 获取商品名称
            name_elem = item.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'name|title', re.I))
            product_name = name_elem.get_text(strip=True) if name_elem else link.get_text(strip=True)
            
            if not product_name or len(product_name) < 5:
                return None
            
            # 获取价格
            price_elem = item.find(['span', 'div', 'p'], class_=re.compile(r'price', re.I))
            price = price_elem.get_text(strip=True) if price_elem else ""
            
            # 获取原价(如果有折扣)
            old_price_elem = item.find(['span', 'del'], class_=re.compile(r'old|original|regular', re.I))
            old_price = old_price_elem.get_text(strip=True) if old_price_elem else ""
            
            # 获取图片
            img = item.find('img')
            image_url = ""
            if img:
                image_url = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy', '')
                if image_url and not image_url.startswith('http'):
                    image_url = urljoin(BASE_URL, image_url)
            
            # 获取评分和评论数
            rating_elem = item.find(class_=re.compile(r'rating|star', re.I))
            rating = rating_elem.get_text(strip=True) if rating_elem else ""
            
            reviews_elem = item.find(class_=re.compile(r'review|sold', re.I))
            reviews = reviews_elem.get_text(strip=True) if reviews_elem else ""
            
            return {
                'name': product_name,
                'url': product_url,
                'price': price,
                'old_price': old_price,
                'image': image_url,
                'rating': rating,
                'reviews': reviews,
                'category': category_name
            }
            
        except Exception as e:
            print(f"解析商品项失败: {e}")
            return None
    
    def scrape_all_products(self, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        爬取所有分类的商品
        
        Args:
            categories: 分类列表
            
        Returns:
            所有商品列表
        """
        print(f"开始爬取所有商品，共 {len(categories)} 个分类...")
        
        for i, category in enumerate(categories, 1):
            print(f"\n进度: {i}/{len(categories)}")
            
            products = self.scrape_category_products(
                category['url'], 
                category['name']
            )
            
            self.products.extend(products)
        
        # 去重
        unique_products = []
        seen_urls = set()
        
        for product in self.products:
            if product['url'] not in seen_urls:
                unique_products.append(product)
                seen_urls.add(product['url'])
        
        self.products = unique_products
        print(f"\n共爬取到 {len(self.products)} 个不重复的商品")
        
        return self.products
    
    def save_products(self, filename: str = "products.json"):
        """
        保存商品数据到JSON文件
        
        Args:
            filename: 文件名
        """
        save_to_json(self.products, filename)
        print(f"商品数据已保存到: {filename}")


def main():
    """主函数"""
    # 读取分类数据
    try:
        with open("../data/categories.json", "r", encoding="utf-8") as f:
            categories = json.load(f)
    except FileNotFoundError:
        print("错误: 未找到分类数据文件，请先运行 menu.py")
        return
    
    # 创建商品爬虫
    scraper = ProductScraper()
    
    # 爬取所有商品
    products = scraper.scrape_all_products(categories)
    
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
        print(f"{i}. {product['name']}")
        print(f"   价格: {product['price']}")
        print(f"   分类: {product['category']}")
        print(f"   链接: {product['url']}")


if __name__ == "__main__":
    main()
