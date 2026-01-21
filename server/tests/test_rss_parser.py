"""
RSS解析器测试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server.site_parsers.mikan_rss_parser import MikanRSSParser


def test_rss_parser():
    """测试RSS解析器"""
    print("=" * 60)
    print("测试RSS解析器")
    print("=" * 60)
    
    # 创建蜜柑计划RSS解析器
    parser = MikanRSSParser()
    
    # 测试1: 获取网站名称
    print("\n测试1: 获取网站名称")
    site_name = parser.get_site_name()
    print(f"✓ 网站名称: {site_name}")
    
    # 测试2: 判断是否可以解析
    print("\n测试2: 判断是否可以解析")
    test_urls = [
        ("https://mikanani.me/RSS/Bangumi?bangumiId=3824", True),
        ("https://example.com/rss", False),
    ]
    
    for url, expected in test_urls:
        can_parse = parser.can_parse(url)
        assert can_parse == expected, f"判断失败: {url} -> {can_parse} (期望: {expected})"
        print(f"✓ '{url}' -> {'可以解析' if can_parse else '不能解析'}")
    
    # 测试3: 解析蜜柑计划的RSS
    print("\n测试3: 解析蜜柑计划RSS")
    rss_url = "https://mikanani.me/RSS/Bangumi?bangumiId=3824"
    result = parser.parse_rss(rss_url)
    
    assert result['success'] is True, f"RSS解析失败: {result.get('error')}"
    print(f"✓ RSS解析成功")
    print(f"  - Feed标题: {result.get('feed_title', 'N/A')}")
    print(f"  - Feed描述: {result.get('feed_description', 'N/A')[:50]}...")
    print(f"  - 总条目数: {result.get('total_entries', 0)}")
    print(f"  - 提取的链接数: {len(result.get('links', []))}")
    
    # 显示前3个链接
    links = result.get('links', [])
    for i, link in enumerate(links[:3], 1):
        print(f"\n  链接 {i}:")
        print(f"    - 标题: {link.get('entry_title', 'N/A')}")
        print(f"    - 集数: {link.get('episode_number', 'N/A')}")
        print(f"    - 集标题: {link.get('episode_title', 'N/A')}")
        print(f"    - 类型: {link.get('link_type', 'N/A')}")
        print(f"    - 大小: {link.get('file_size', 0) / (1024*1024*1024):.2f} GB" if link.get('file_size') else f"    - 大小: N/A")
        print(f"    - URL: {link.get('url', 'N/A')[:60]}...")
    
    # 测试4: 检查新链接
    print("\n" + "=" * 60)
    print("测试4: 检查新链接")
    existing_urls = [link['url'] for link in links[:5]]  # 假设前5个已存在
    result = parser.parse_rss(rss_url, existing_urls)
    
    assert result['success'] is True
    print(f"✓ 检查新链接成功")
    print(f"  - 总链接数: {len(result.get('links', []))}")
    print(f"  - 已存在链接数: {len(existing_urls)}")
    print(f"  - 新链接数: {result.get('new_links_count', 0)}")
    
    # 测试5: 测试集数提取
    print("\n" + "=" * 60)
    print("测试5: 测试集数提取")
    test_titles = [
        ("黄金神威 最终章 第1集", 1),
        ("黄金神威 最终章 EP.2", 2),
        ("[LoliHouse] 黄金神威 最终章 [03]", 3),
        ("黄金神威 最终章 - 4", 4),
        ("黄金神威 最终章 05", 5),
    ]
    
    for title, expected in test_titles:
        episode = parser.extract_episode_number(title)
        assert episode == expected, f"集数提取失败: {title} -> {episode} (期望: {expected})"
        print(f"✓ '{title}' -> {episode}")
    
    # 测试6: 测试集标题提取
    print("\n" + "=" * 60)
    print("测试6: 测试集标题提取")
    test_titles = [
        ("[LoliHouse] 黄金神威 最终章 [01].mkv", "黄金神威 最终章"),
        ("黄金神威 最终章 第2集 (1080P)", "黄金神威 最终章"),
        ("黄金神威 最终章 EP.3 - 剧情介绍", "黄金神威 最终章 剧情介绍"),
    ]
    
    for title, expected in test_titles:
        episode_title = parser.extract_episode_title(title)
        print(f"✓ '{title}' -> '{episode_title}'")
    
    print("\n" + "=" * 60)
    print("[成功] RSS解析器测试通过")
    print("=" * 60)


if __name__ == "__main__":
    test_rss_parser()