"""
使用示例
演示如何使用爬虫脚本
"""

from menu import MenuScraper
from products import ProductScraper
import json


def example_1_scrape_menu():
    """示例1: 爬取导航菜单"""
    print("=== 示例1: 爬取导航菜单 ===\n")
    
    # 创建菜单爬虫
    scraper = MenuScraper()
    
    # 爬取分类
    categories = scraper.scrape_menu()
    
    # 保存数据
    scraper.save_categories()
    
    # 显示结果
    print(f"\n共发现 {len(categories)} 个分类")
    print("\n前5个分类:")
    for i, cat in enumerate(categories[:5], 1):
        print(f"{i}. {cat['name']} - {cat['url']}")


def example_2_scrape_products():
    """示例2: 爬取商品信息"""
    print("\n=== 示例2: 爬取商品信息 ===\n")
    
    # 加载分类数据
    try:
        with open("../data/categories.json", "r", encoding="utf-8") as f:
            categories = json.load(f)
    except FileNotFoundError:
        print("错误: 请先运行示例1爬取分类数据")
        return
    
    # 创建商品爬虫
    scraper = ProductScraper()
    
    # 只爬取前3个分类作为示例(节省时间)
    print("注意: 为了演示，只爬取前3个分类的商品")
    products = scraper.scrape_all_products(categories[:3])
    
    # 保存数据
    scraper.save_products()
    
    # 显示结果
    print(f"\n共爬取 {len(products)} 个商品")
    if products:
        print("\n前3个商品:")
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. {product['name']}")
            print(f"   价格: {product['price']}")
            print(f"   分类: {product['category']}")
            print(f"   链接: {product['url']}")


def example_3_full_scrape():
    """示例3: 完整爬取流程"""
    print("\n=== 示例3: 完整爬取流程 ===\n")
    
    # 步骤1: 爬取分类
    print("步骤1: 爬取分类...")
    menu_scraper = MenuScraper()
    categories = menu_scraper.scrape_menu()
    menu_scraper.save_categories()
    
    # 步骤2: 爬取商品
    print("\n步骤2: 爬取商品...")
    product_scraper = ProductScraper()
    
    # 这里可以选择爬取所有分类或部分分类
    # 全部: products = product_scraper.scrape_all_products(categories)
    # 部分: products = product_scraper.scrape_all_products(categories[:5])
    
    products = product_scraper.scrape_all_products(categories[:5])  # 只爬取前5个分类
    product_scraper.save_products()
    
    # 步骤3: 统计信息
    print("\n步骤3: 统计信息")
    print(f"分类总数: {len(categories)}")
    print(f"商品总数: {len(products)}")
    
    # 按分类统计
    category_stats = {}
    for product in products:
        category = product.get('category', 'Unknown')
        category_stats[category] = category_stats.get(category, 0) + 1
    
    print("\n各分类商品数:")
    for category, count in category_stats.items():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    print("iseehair.com 爬虫使用示例")
    print("="*60)
    
    # 运行示例
    # 取消注释你想运行的示例
    
    # example_1_scrape_menu()        # 只爬取分类
    # example_2_scrape_products()    # 只爬取商品(需要先有分类数据)
    example_3_full_scrape()          # 完整流程
    
    print("\n" + "="*60)
    print("完成! 查看 data/ 目录下的 JSON 文件获取数据")
