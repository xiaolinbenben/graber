"""检查网站的真实链接格式"""
import requests
import urllib3
from bs4 import BeautifulSoup

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_links(url):
    """检查页面上的所有链接"""
    print(f"正在检查页面: {url}\n")
    
    try:
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30,
            verify=False
        )
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        # 查找所有商品链接 - 尝试不同的选择器
        selectors = [
            '.product-item-link',
            '.product-item a',
            '.product-item-info a',
            'a[href*=".html"]',
        ]
        
        all_links = set()
        
        for selector in selectors:
            elements = soup.select(selector)
            print(f"\n选择器 '{selector}' 找到 {len(elements)} 个元素")
            
            for elem in elements[:10]:  # 只看前10个
                if elem.has_attr('href'):
                    href = elem['href']
                    text = elem.get_text(strip=True)
                    print(f"  - {text[:50]}: {href}")
                    all_links.add(href)
        
        print(f"\n总共找到 {len(all_links)} 个唯一链接")
        
        # 分析链接模式
        print("\n=== 链接分析 ===")
        has_isee = [link for link in all_links if 'isee-' in link]
        print(f"包含 'isee-' 的链接: {len(has_isee)}")
        if has_isee:
            print("示例:")
            for link in list(has_isee)[:5]:
                print(f"  {link}")
        
        many_hyphens = [link for link in all_links if link.count('-') >= 3]
        print(f"\n包含 ≥3 个连字符的链接: {len(many_hyphens)}")
        if many_hyphens:
            print("示例:")
            for link in list(many_hyphens)[:5]:
                print(f"  {link}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == '__main__':
    # 测试一个分类页面
    check_links('https://www.iseehair.com/half-wig.html')
