# iseehair.com 爬虫

爬取 iseehair.com 网站的商品分类和商品信息。

## 功能

1. **爬取导航菜单** - 抓取网站的所有商品分类
2. **爬取商品信息** - 抓取所有商品的详细信息，包括名称、价格、图片、分类等

## 安装依赖

```bash
pip install requests beautifulsoup4
```

## 使用方法

### 方式 1: 使用命令行界面

```bash
cd src
python cli.py
```

然后按照提示选择操作:

- 选项 1: 爬取导航菜单(商品分类)
- 选项 2: 爬取所有商品
- 选项 3: 一次性爬取导航菜单和所有商品
- 选项 4: 查看统计信息

### 方式 2: 单独运行脚本

#### 1. 爬取导航菜单

```bash
cd src
python menu.py
```

这将爬取所有商品分类并保存到 `data/categories.json`

#### 2. 爬取所有商品

```bash
cd src
python products.py
```

这将爬取所有商品信息并保存到 `data/products.json`

**注意**: 运行此脚本前需要先运行 `menu.py` 生成分类数据

## 数据格式

### 分类数据 (categories.json)

```json
[
  {
    "name": "分类名称",
    "url": "完整URL",
    "path": "相对路径"
  }
]
```

### 商品数据 (products.json)

```json
[
  {
    "name": "商品名称",
    "url": "商品URL",
    "price": "价格",
    "old_price": "原价(如有折扣)",
    "image": "图片URL",
    "rating": "评分",
    "reviews": "评论数/销量",
    "category": "所属分类"
  }
]
```

## 文件说明

- `config.py` - 配置文件(URL、请求头、超时设置等)
- `httpclient.py` - HTTP 客户端封装
- `menu.py` - 导航菜单爬虫
- `products.py` - 商品信息爬虫
- `saver.py` - 数据保存模块
- `cli.py` - 命令行界面

## 注意事项

1. 爬虫会自动添加请求延迟，避免请求过快
2. 数据会保存在 `data/` 目录下
3. 建议先爬取分类数据，再爬取商品数据
4. 如遇到网络问题，程序会自动重试

## 示例

```bash
# 完整流程
cd src
python cli.py

# 选择选项 3 - 爬取导航菜单 + 所有商品
# 等待爬取完成，数据将保存在 data/ 目录
```
