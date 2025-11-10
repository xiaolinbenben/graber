"""
爬取网站导航菜单(商品分类)
"""

import json
import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from httpclient import HttpClient
from config import BASE_URL
from saver import save_to_json


class MenuScraper:
    """导航菜单爬虫类"""
    
    def __init__(self):
        self.client = HttpClient()
        self.categories = []
        
    def scrape_menu(self) -> List[Dict[str, Any]]:
        """
        爬取导航菜单
        
        Returns:
            分类列表
        """
        print("开始爬取导航菜单...")
        
        # 获取首页HTML
        response = self.client.get(BASE_URL, delay=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找导航菜单
        # 方法1: 查找主导航栏
        nav_menus = soup.find_all('nav') or soup.find_all('div', class_=re.compile(r'nav|menu|header', re.I))
        
        for nav in nav_menus:
            # 查找所有链接
            links = nav.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 过滤掉空文本和无效链接
                if not text or not href:
                    continue
                    
                # 构建完整URL
                if href.startswith('/'):
                    full_url = BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                    
                # 判断是否是分类链接(通常包含关键词)
                if any(keyword in href.lower() for keyword in [
                    'category', 'collection', 'wig', 'hair', 'bundle', 
                    'lace', 'closure', 'frontal', 'wave', 'curly', 'straight'
                ]):
                    category = {
                        'name': text,
                        'url': full_url,
                        'path': href
                    }
                    
                    # 避免重复
                    if not any(c['url'] == full_url for c in self.categories):
                        self.categories.append(category)
                        print(f"发现分类: {text} -> {full_url}")
        
        # 方法2: 查找特定的分类页面链接(通过抓取页面中的.html链接)
        all_links = soup.find_all('a', href=re.compile(r'\.html$'))
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if not text or len(text) > 100:  # 过滤过长的文本
                continue
                
            # 构建完整URL
            if href.startswith('/'):
                full_url = BASE_URL + href
            elif href.startswith('http'):
                full_url = href
            else:
                continue
            
            # 过滤掉特定页面
            skip_keywords = ['privacy', 'terms', 'about', 'contact', 'faq', 'blog', 'cart', 'checkout']
            if any(keyword in href.lower() for keyword in skip_keywords):
                continue
                
            category = {
                'name': text,
                'url': full_url,
                'path': href
            }
            
            # 避免重复
            if not any(c['url'] == full_url for c in self.categories):
                self.categories.append(category)
                print(f"发现分类: {text} -> {full_url}")
        
        print(f"共发现 {len(self.categories)} 个分类")
        return self.categories
        
    def save_categories(self, filename: str = "categories.json"):
        """
        保存分类数据到JSON文件
        
        Args:
            filename: 文件名
        """
        save_to_json(self.categories, filename)
        print(f"分类数据已保存到: {filename}")


def main():
    """主函数"""
    scraper = MenuScraper()
    categories = scraper.scrape_menu()
    scraper.save_categories()
    
    # 打印统计信息
    print("\n=== 分类统计 ===")
    print(f"总分类数: {len(categories)}")
    
    # 显示前10个分类
    print("\n前10个分类:")
    for i, cat in enumerate(categories[:10], 1):
        print(f"{i}. {cat['name']} - {cat['url']}")


if __name__ == "__main__":
    main()
