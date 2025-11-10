"""
命令行界面
"""

import sys
from menu import MenuScraper
from products import ProductScraper
from saver import load_from_json


def print_menu():
    """打印菜单"""
    print("\n" + "="*50)
    print("iseehair.com 爬虫工具")
    print("="*50)
    print("1. 爬取导航菜单(商品分类)")
    print("2. 爬取所有商品")
    print("3. 爬取导航菜单 + 所有商品")
    print("4. 查看统计信息")
    print("0. 退出")
    print("="*50)


def scrape_menu():
    """爬取导航菜单"""
    scraper = MenuScraper()
    categories = scraper.scrape_menu()
    scraper.save_categories()
    
    print(f"\n成功爬取 {len(categories)} 个分类")
    return categories


def scrape_products():
    """爬取所有商品"""
    try:
        categories = load_from_json("categories.json")
    except FileNotFoundError:
        print("错误: 未找到分类数据，请先爬取导航菜单")
        return []
    
    scraper = ProductScraper()
    products = scraper.scrape_all_products(categories)
    scraper.save_products()
    
    print(f"\n成功爬取 {len(products)} 个商品")
    return products


def scrape_all():
    """爬取导航菜单和所有商品"""
    print("开始完整爬取...")
    
    # 1. 爬取分类
    categories = scrape_menu()
    
    # 2. 爬取商品
    scraper = ProductScraper()
    products = scraper.scrape_all_products(categories)
    scraper.save_products()
    
    print(f"\n完成! 共爬取 {len(categories)} 个分类，{len(products)} 个商品")


def show_statistics():
    """显示统计信息"""
    try:
        categories = load_from_json("categories.json")
        products = load_from_json("products.json")
        
        print("\n=== 统计信息 ===")
        print(f"分类总数: {len(categories)}")
        print(f"商品总数: {len(products)}")
        
        # 按分类统计
        category_stats = {}
        for product in products:
            category = product.get('category', 'Unknown')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        print("\n各分类商品数:")
        for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {category}: {count}")
            
    except FileNotFoundError as e:
        print(f"错误: {e}")
        print("请先运行爬虫程序")


def main():
    """主函数"""
    while True:
        print_menu()
        
        choice = input("\n请选择操作 (0-4): ").strip()
        
        if choice == '1':
            scrape_menu()
        elif choice == '2':
            scrape_products()
        elif choice == '3':
            scrape_all()
        elif choice == '4':
            show_statistics()
        elif choice == '0':
            print("再见!")
            sys.exit(0)
        else:
            print("无效的选择，请重新输入")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    main()
