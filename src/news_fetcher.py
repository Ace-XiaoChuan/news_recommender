"""
模块一：新闻数据获取模块
功能：通过NewsAPI获取指定分类的新闻数据，并做基础清洗
"""

import requests
import json
from datetime import datetime
from config import settings  # 导入配置文件


class NewsFetcher:
    def __init__(self):
        self.api_key = settings.NEWS_API_KEY  # 从配置文件读取密钥
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def fetch_news(self, category="technology", page_size=20):
        """
        获取指定分类的新闻数据
        :param category: 新闻分类（technology/business等）
        :param page_size: 每页数量（默认20条）
        :return: 结构化的新闻数据列表
        """
        params = {
            "category": category,
            "pageSize": page_size,
            "country": "us",  # 以美国新闻为例
            "apiKey": self.api_key
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # 自动触发HTTP错误异常
            raw_data = response.json()

            return self._clean_data(raw_data.get('articles', []))

        except requests.exceptions.RequestException as e:
            print(f"新闻获取失败: {str(e)}")
            return []

    def _clean_data(self, raw_articles):
        """
        数据清洗私有方法：
        1. 过滤无内容的文章
        2. 添加获取时间戳
        3. 计算预估阅读时间
        """
        cleaned = []
        for article in raw_articles:
            # 基础字段校验
            if not article.get('title') or not article.get('url'):
                continue

            # 计算阅读时间（假设500字/分钟）
            content = article.get('content', "") or ""
            read_time = max(1, len(content.split()) // 500)

            cleaned.append({
                "title": article['title'],
                "description": article.get('description', '暂无描述'),
                "url": article['url'],
                "source": article.get('source', {}).get('name', '未知来源'),
                "published_at": article.get('publishedAt', datetime.now().isoformat()),
                "content_length": len(content),
                "estimated_read_time": read_time,
                "category": article.get('category', 'general')  # NewsAPI不返回分类，需后续处理
            })

        return cleaned


# 测试代码（直接运行该文件时执行）
if __name__ == "__main__":
    fetcher = NewsFetcher()
    tech_news = fetcher.fetch_news(category="technology")

    print(f"获取到{len(tech_news)}条科技新闻：")
    for idx, news in enumerate(tech_news[:2], 1):  # 仅打印前2条示例
        print(f"\n{idx}. {news['title']}")
        print(f"   来源：{news['source']}")
        print(f"   预计阅读时间：{news['estimated_read_time']}分钟")
        print(f"   链接：{news['url']}")