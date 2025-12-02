"""
尝试查找和使用网站的API接口
"""

import json
import re
from typing import List, Dict, Any
from httpclient import HttpClient
from config import BASE_URL
from saver import save_to_json


class ApiScraper:
    """API爬虫类"""
    
    def __init__(self):
        self.client = HttpClient()
        
    def test_api_endpoints(self):
        """测试可能的API端点"""
        print("正在测试可能的API端点...")
        
        # 常见的API端点模式
        api_patterns = [
            "/api/products",
            "/api/v1/products",
            "/api/catalog/products",
            "/rest/products",
            "/graphql",
            "/api/search",
        ]
        
        for pattern in api_patterns:
            url = BASE_URL + pattern
            try:
                print(f"尝试: {url}")
                response = self.client.get(url)
                if response.status_code == 200:
                    print(f"✓ 找到可用端点: {url}")
                    print(f"  响应预览: {response.text[:200]}")
            except Exception as e:
                print(f"✗ {pattern}: 不可用")
                
    def analyze_page_scripts(self, url: str):
        """分析页面中的JavaScript代码,查找API调用"""
        print(f"\n分析页面: {url}")
        
        try:
            response = self.client.get(url, delay=False)
            html = response.text
            
            # 查找script标签
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
            
            print(f"找到 {len(scripts)} 个script标签")
            
            # 查找可能的API调用
            api_patterns = [
                r'fetch\(["\']([^"\']+)["\']',
                r'axios\.[get|post]+\(["\']([^"\']+)["\']',
                r'\.get\(["\']([^"\']+)["\']',
                r'url:\s*["\']([^"\']+)["\']',
                r'api["\']:\s*["\']([^"\']+)["\']',
            ]
            
            found_apis = set()
            for script in scripts[:10]:  # 只检查前10个
                for pattern in api_patterns:
                    matches = re.findall(pattern, script, re.IGNORECASE)
                    for match in matches:
                        if '/api/' in match or '.json' in match:
                            found_apis.add(match)
            
            if found_apis:
                print("\n找到可能的API调用:")
                for api in found_apis:
                    print(f"  - {api}")
            else:
                print("未找到明显的API调用")
                
            # 查找JSON数据
            json_pattern = r'var\s+\w+\s*=\s*(\{[^;]+\})'
            json_matches = re.findall(json_pattern, html)
            
            if json_matches:
                print(f"\n找到 {len(json_matches)} 个可能的JSON数据对象")
                for i, match in enumerate(json_matches[:3], 1):
                    try:
                        # 尝试解析JSON
                        data = json.loads(match)
                        print(f"\n对象 {i}:")
                        print(f"  键: {list(data.keys())[:10]}")
                    except:
                        pass
                        
        except Exception as e:
            print(f"分析失败: {e}")


def main():
    """主函数"""
    scraper = ApiScraper()
    
    print("="*60)
    print("网站API分析工具")
    print("="*60)
    
    # 1. 测试常见API端点
    scraper.test_api_endpoints()
    
    # 2. 分析首页
    print("\n" + "="*60)
    scraper.analyze_page_scripts(BASE_URL)
    
    # 3. 分析分类页面
    print("\n" + "="*60)
    scraper.analyze_page_scripts(BASE_URL + "/half-wig.html")


if __name__ == "__main__":
    main()
