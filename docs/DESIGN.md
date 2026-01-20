# animeloader 项目设计文档

## 1. 项目概述

animeloader 是一个用于订阅动画发布和管理动画下载内容的 Python 应用程序。系统采用客户端-服务端架构，支持用户通过命令行界面管理动画订阅、查看下载状态和配置定时任务。

### 1.1 当前实现状态

> **注意**：本项目处于开发阶段，以下为核心功能的实现状态：
>
> - ✅ **已完成**：动画管理（添加、查询、更新、删除）、RSS源管理（添加、查询、更新、删除）、智能解析功能（蜜柑计划网站）、基础API框架
> - 🚧 **开发中**：链接管理、下载器管理、下载任务管理、定时任务调度
> - 📋 **计划中**：RSS源自动检查、链接自动下载、下载状态同步、多下载器支持

### 1.2 核心功能

- **动画订阅管理**：添加、删除、修改、查询动画订阅信息
- **RSS源管理**：添加、删除、更新、查询RSS订阅源
- **智能解析功能**：
  - 支持从动画网站链接自动解析动画信息和RSS订阅链接
  - 当前支持 https://mikanani.me/（蜜柑计划）
  - 动画智能解析支持连锁操作，解析动画后可自动解析RSS源
  - RSS源智能解析需指定所属动画
  - 解析结果有多个时提供交互式选择界面
  - 支持多选和范围选择（如 1,2,3 或 1-3）
- **链接管理**：查看、过滤下载链接，支持多种链接类型（magnet、ed2k等）- *开发中*
- **下载器管理**：支持多种下载器（aria2、pikpak等），支持扩展新的下载器 - *开发中*
- **下载任务管理**：针对每个链接创建下载任务，支持暂停、恢复、取消 - *计划中*
- **定时下载任务**：自动检测新发布的动画并下载 - *计划中*
- **下载状态监控**：实时查看下载进度和状态，支持同步外部下载器状态 - *计划中*
- **命令行交互**：提供友好的 CLI 界面进行操作

### 1.3 目标用户

- 动画爱好者
- 需要自动化下载动画内容的用户

### 1.1 核心功能

- **动画订阅管理**：添加、删除、修改动画订阅信息
- **RSS源管理**：添加、删除、检查RSS订阅源
- **智能解析功能**：
  - 支持从动画网站链接自动解析动画信息和RSS订阅链接
  - 当前支持 https://mikanani.me/（蜜柑计划）
  - 动画智能解析支持连锁操作，解析动画后可自动解析RSS源
  - RSS源智能解析需指定所属动画
  - 解析结果有多个时提供交互式选择界面
  - 支持多选和范围选择（如 1,2,3 或 1-3）
- **链接管理**：查看、过滤下载链接，支持多种链接类型（magnet、ed2k等）
- **下载器管理**：支持多种下载器（aria2、pikpak等），支持扩展新的下载器
- **下载任务管理**：针对每个链接创建下载任务，支持暂停、恢复、取消
- **定时下载任务**：自动检测新发布的动画并下载
- **下载状态监控**：实时查看下载进度和状态，支持同步外部下载器状态
- **命令行交互**：提供友好的 CLI 界面进行操作

### 1.2 目标用户

- 动画爱好者
- 需要自动化下载动画内容的用户

## 2. 技术栈

### 2.1 开发环境

- **Python**: 3.12+
- **操作系统**: macOS / Linux / Windows

### 2.2 核心依赖

- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **CLI框架**: cmd2 (客户端命令行框架)
- **界面美化**: rich (客户端命令行交互美化)
- **HTTP客户端**: requests
- **RSS解析**: feedparser
- **HTML解析**: beautifulsoup4 (用于网站智能解析)
- **交互式选择**: inquirer (用于命令行交互选择)
- **任务调度**: APScheduler
- **日志**: logging
- **aria2 RPC**: aria2p (可选，用于aria2下载器)
- **配置管理**: pyyaml

### 2.3 可选依赖

- **配置管理**: pyyaml / toml
- **API框架**: FastAPI (如需提供 REST API)
- **测试框架**: pytest

## 3. 系统架构

### 3.1 整体架构

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│   CLI Client    │◄────────┤   Server        │
│                 │  HTTP   │                 │
└─────────────────┘         └─────────────────┘
                                     │
                                     │
                                     ▼
                              ┌─────────────────┐
                              │   SQLite DB     │
                              └─────────────────┘
                                     │
                                     │
                                     ▼
                              ┌─────────────────┐
                              │   Downloaders   │
                              │  ┌───────────┐  │
                              │  │   aria2   │  │
                              │  └───────────┘  │
                              │  ┌───────────┐  │
                              │  │   pikpak  │  │
                              │  └───────────┘  │
                              └─────────────────┘
```

### 3.2 目录结构

```
animeloader/
├── IFLOW.md              # 项目说明
├── DESIGN.md             # 设计文档
├── LICENSE               # 许可证
├── requirements.txt      # 依赖列表
├── server_config.yaml    # 服务端配置文件（仅用于开发）
├── client_config.yaml    # 客户端配置文件（仅用于开发）
├── server/               # 服务端代码
│   ├── __init__.py
│   ├── main.py           # 服务端入口
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   ├── anime.py      # 动画模型
│   │   ├── rss_source.py # RSS源模型
│   │   ├── link.py       # 链接模型
│   │   ├── downloader.py # 下载器配置模型
│   │   └── download.py   # 下载任务模型
│   ├── services/         # 业务逻辑
│   │   ├── __init__.py
│   │   ├── rss_service.py        # RSS源管理服务
│   │   ├── link_service.py       # 链接管理服务
│   │   ├── download_service.py   # 下载服务
│   │   ├── downloader_service.py # 下载器管理服务
│   │   ├── scheduler_service.py  # 调度服务
│   │   └── smart_parser_service.py # 智能解析服务
│   ├── link_parsers/    # 链接解析器（可扩展）
│   │   ├── __init__.py
│   │   ├── base_parser.py      # 基础解析器
│   │   ├── magnet_parser.py    # 磁力链接解析器
│   │   └── ed2k_parser.py      # ed2k链接解析器
│   ├── site_parsers/     # 网站智能解析器（可扩展）
│   │   ├── __init__.py
│   │   ├── base_site_parser.py # 基础网站解析器
│   │   └── mikan_parser.py     # 蜜柑计划解析器
│   ├── downloaders/       # 下载器实现（可扩展）
│   │   ├── __init__.py
│   │   ├── base_downloader.py   # 基础下载器接口
│   │   ├── aria2_downloader.py  # aria2下载器
│   │   └── pikpak_downloader.py # pikpak离线下载器
│   ├── api/              # API 接口
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── database/         # 数据库相关
│   │   ├── __init__.py
│   │   ├── session.py
│   │   └── init_db.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       ├── config.py     # 配置加载
│       └── logger.py
└── client/               # 客户端代码
    ├── __init__.py
    ├── main.py           # 客户端入口
    ├── commands/         # CLI 命令
    │   ├── __init__.py
    │   ├── anime_commands.py     # 动画命令
    │   ├── rss_commands.py       # RSS源命令
    │   ├── link_commands.py      # 链接命令
    │   ├── download_commands.py  # 下载命令
    │   ├── downloader_commands.py # 下载器命令
    │   └── status_commands.py    # 状态命令
    ├── api/              # API 客户端
    │   ├── __init__.py
    │   └── client.py
    └── utils/            # 工具函数
        ├── __init__.py
        └── config.py     # 客户端配置加载

# 用户目录（默认配置位置）
~/.animeloader/
├── server_config.yaml    # 服务端配置文件（默认位置）
├── client_config.yaml    # 客户端配置文件（默认位置）
├── data/                 # 数据库文件目录
│   └── animeloader.db
├── downloads/            # 下载目录
└── logs/                 # 日志目录
    └── animeloader.log
```

## 4. 服务端设计

### 4.1 数据模型

#### 4.1.1 Anime (动画信息)

```python
class Anime:
    id: int                    # 主键
    title: str                 # 动画标题
    title_en: str              # 英文标题
    description: str           # 描述
    cover_url: str             # 封面URL
    status: str                # 状态 (ongoing, completed, etc.)
    total_episodes: int        # 总集数
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### 4.1.2 RSSSource (RSS订阅源)

```python
class RSSSource:
    id: int                    # 主键
    anime_id: int              # 动画ID (外键)
    name: str                  # RSS源名称
    url: str                   # RSS订阅链接
    quality: str               # 画质 (1080p, 720p, etc.)
    is_active: bool            # 是否激活
    auto_download: bool        # 是否自动下载
    last_checked_at: datetime  # 最后检查时间
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### 4.1.3 Link (下载链接)

```python
class Link:
    id: int                    # 主键
    rss_source_id: int         # RSS源ID (外键)
    episode_number: int        # 集数
    episode_title: str         # 集标题
    link_type: str             # 链接类型 (magnet, ed2k, http, ftp, etc.)
    url: str                   # 链接地址
    file_size: int             # 文件大小 (bytes)
    publish_date: datetime     # 发布时间
    is_downloaded: bool        # 是否已下载
    is_available: bool         # 链接是否可用
    meta_data: str             # 元数据 (JSON格式，存储链接类型特定信息)
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### 4.1.4 Downloader (下载器配置)

```python
class Downloader:
    id: int                    # 主键
    name: str                  # 下载器名称
    downloader_type: str       # 下载器类型 (aria2, pikpak, etc.)
    config: str                # 配置信息 (JSON格式)
    is_active: bool            # 是否激活
    is_default: bool           # 是否为默认下载器
    max_concurrent_tasks: int  # 最大并发任务数
    created_at: datetime       # 创建时间
    updated_at: datetime       # 更新时间
```

#### 4.1.5 DownloadTask (下载任务)

```python
class DownloadTask:
    id: int                    # 主键
    link_id: int               # 链接ID (外键)
    rss_source_id: int         # RSS源ID (外键)
    downloader_id: int         # 下载器ID (外键)
    downloader_type: str       # 下载器类型 (冗余字段，便于查询)
    file_path: str             # 本地保存路径
    status: str                # 状态 (pending, downloading, completed, failed, seeding)
    progress: float            # 进度 (0-100)
    file_size: int             # 文件大小 (bytes)
    downloaded_size: int       # 已下载大小 (bytes)
    download_speed: float      # 下载速度 (bytes/s)
    upload_speed: float        # 上传速度 (bytes/s) - 用于BT种子
    error_message: str         # 错误信息
    retry_count: int           # 重试次数
    task_id_external: str      # 外部下载器任务ID (如aria2的gid)
    created_at: datetime       # 创建时间
    started_at: datetime       # 开始时间
    completed_at: datetime     # 完成时间
```

### 4.2 服务模块

#### 4.2.1 AnimeService (动画管理服务) ✅

- `create_anime(title, title_en, description, cover_url, status, total_episodes)` - 创建动画记录
- `get_anime(anime_id)` - 获取单个动画
- `get_animes(skip, limit, search, status)` - 获取动画列表，支持搜索和过滤
- `update_anime(anime_id, **kwargs)` - 更新动画信息
- `delete_anime(anime_id)` - 删除动画
- `count_animes(search, status)` - 统计动画数量

#### 4.2.2 RSSService (RSS源管理服务) ✅

- `create_rss_source(anime_id, name, url, quality, is_active, auto_download)` - 创建RSS源记录
- `get_rss_source(rss_source_id)` - 获取单个RSS源
- `get_rss_sources(anime_id)` - 获取动画的所有RSS源
- `update_rss_source(rss_source_id, **kwargs)` - 更新RSS源信息
- `delete_rss_source(rss_source_id)` - 删除RSS源

#### 4.2.3 SmartParserService (智能解析服务) ✅

- `parse_anime(url: str) -> List[Dict]` - 解析动画链接，返回可能的动画信息列表
- `parse_rss(url: str, anime_id: int) -> List[Dict]` - 解析RSS链接，返回可能的RSS源信息列表（需指定所属动画）
- `parse_anime_with_rss(url, auto_add_rss, anime_index, rss_indices, db)` - 解析动画链接并自动解析RSS源（连锁解析），并创建动画记录
- `get_supported_sites() -> List[str]` - 获取支持的动画网站列表
- `get_site_name_from_url(url: str) -> str` - 根据URL获取网站名称
- `register_site_parser(parser)` - 注册新的网站解析器

#### 4.2.4 LinkService (链接管理服务) 🚧

*开发中 - 功能尚未实现*

- `add_link(rss_source_id, episode_number, episode_title, link_type, url, **kwargs)` - 添加链接
- `get_links(rss_source_id, is_downloaded=None)` - 获取RSS源的所有链接
- `get_link(link_id)` - 获取单个链接
- `mark_as_downloaded(link_id)` - 标记链接为已下载
- `update_link_status(link_id, is_available)` - 更新链接可用状态
- `get_available_links(rss_source_id)` - 获取可用的下载链接
- `filter_links_by_type(rss_source_id, link_type)` - 按链接类型过滤

#### 4.2.5 DownloadService (下载服务) 🚧

*开发中 - 功能尚未实现*

- `create_download_task(link_id, rss_source_id, downloader_id=None)` - 创建下载任务
- `start_download(task_id)` - 开始下载
- `pause_download(task_id)` - 暂停下载
- `resume_download(task_id)` - 恢复下载
- `cancel_download(task_id)` - 取消下载
- `get_download_status(task_id)` - 获取下载状态
- `get_download_tasks(rss_source_id)` - 获取RSS源的所有下载任务
- `get_download_tasks_by_link(link_id)` - 获取链接的所有下载任务
- `get_active_downloads()` - 获取所有活跃的下载任务
- `sync_download_status(task_id)` - 同步下载器状态到本地

#### 4.2.6 DownloaderService (下载器管理服务) 🚧

*开发中 - 功能尚未实现*

- `add_downloader(name, downloader_type, config, is_default=False)` - 添加下载器
- `remove_downloader(downloader_id)` - 删除下载器
- `update_downloader(downloader_id, **kwargs)` - 更新下载器配置
- `get_downloaders()` - 获取所有下载器
- `get_downloader(downloader_id)` - 获取单个下载器
- `get_default_downloader()` - 获取默认下载器
- `set_default_downloader(downloader_id)` - 设置默认下载器
- `get_downloader_by_type(downloader_type)` - 根据类型获取下载器
- `test_downloader(downloader_id)` - 测试下载器连接
- `get_downloader_status(downloader_id)` - 获取下载器状态（当前任务数等）

#### 4.2.7 SchedulerService (调度服务) 📋

*计划中 - 功能尚未实现*

- `start_scheduler()` - 启动调度器
- `stop_scheduler()` - 停止调度器
- `add_check_job(rss_source_id, interval)` - 添加RSS源检查任务
- `remove_check_job(job_id)` - 移除检查任务
- `check_rss_source(rss_source_id)` - 检查RSS源的新链接

#### 4.2.8 LinkParserService (链接解析服务 - 可扩展) 📋

*计划中 - 功能尚未实现*

- `parse_link(link_type, url)` - 根据链接类型解析链接
- `get_parser(link_type)` - 获取对应链接类型的解析器
- `register_parser(link_type, parser_class)` - 注册新的链接类型解析器
- `validate_link(link_type, url)` - 验证链接格式是否正确

#### 4.2.9 DownloaderManagerService (下载器管理服务 - 可扩展) 📋

*计划中 - 功能尚未实现*

- `get_downloader(downloader_type)` - 获取对应类型的下载器实例
- `register_downloader(downloader_type, downloader_class)` - 注册新的下载器类型
- `get_supported_downloader_types()` - 获取支持的下载器类型列表
- `validate_downloader_config(downloader_type, config)` - 验证下载器配置

智能解析服务用于从动画网站链接自动解析动画信息和RSS订阅链接信息。

- `parse_anime(url: str) -> List[Dict]` - 解析动画链接，返回可能的动画信息列表
- `parse_rss(url: str, anime_id: int) -> List[Dict]` - 解析RSS链接，返回可能的RSS源信息列表（需指定所属动画）
- `parse_anime_with_rss(url: str, auto_add_rss: bool = True) -> Dict` - 解析动画链接并自动解析RSS源（连锁解析）
- `get_supported_sites() -> List[str]` - 获取支持的动画网站列表
- `register_site_parser(site_name: str, parser_class)` - 注册新的网站解析器

**智能解析流程：**

1. **动画智能解析**：
   - 用户提供一个动画网站链接
   - 系统识别网站类型并调用对应的解析器
   - 解析器提取动画基本信息（标题、描述、封面等）
   - 如果解析结果有多个，返回列表供用户选择
   - 用户选择后，系统创建动画记录
   - 如果启用连锁解析，自动解析该动画下的RSS源

2. **RSS源智能解析**：
   - 用户提供一个RSS网站链接，并指定所属的动画
   - 系统识别网站类型并调用对应的解析器
   - 解析器提取RSS源信息（名称、URL、画质等）
   - 如果解析结果有多个，返回列表供用户选择
   - 用户选择后，系统创建RSS源记录

**支持的网站：**
- https://mikanani.me/（蜜柑计划）

**网站解析器接口设计：**
```python
class BaseSiteParser(ABC):
    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """判断是否可以解析该URL"""
        pass

    @abstractmethod
    def parse_anime(self, url: str) -> List[Dict]:
        """解析动画信息，返回可能的动画列表"""
        pass

    @abstractmethod
    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        """解析RSS源信息，返回可能的RSS源列表"""
        pass

    @abstractmethod
    def get_site_name(self) -> str:
        """获取网站名称"""
        pass
```

**智能解析返回数据格式：**

动画信息格式：
```python
{
    'title': '鬼灭之刃',
    'title_en': 'Demon Slayer',
    'description': '动画描述',
    'cover_url': 'https://example.com/cover.jpg',
    'status': 'ongoing',
    'total_episodes': 12,
    'rss_sources': [  # 可选，如果解析器能同时解析RSS
        {
            'name': '蜜柑计划 1080P',
            'url': 'https://mikanani.me/RSS/Bangumi/12345',
            'quality': '1080p'
        }
    ]
}
```

RSS源信息格式：
```python
{
    'name': '蜜柑计划 1080P',
    'url': 'https://mikanani.me/RSS/Bangumi/12345',
    'quality': '1080p',
    'auto_download': True
}
```

### 4.3 API 接口

#### RESTful API 设计

**已实现的 API：**

```
# 动画相关 ✅
GET    /api/anime                   # 获取动画列表，支持搜索和过滤
GET    /api/anime/{anime_id}        # 获取动画详情
POST   /api/anime                   # 创建动画
PUT    /api/anime/{anime_id}        # 更新动画
DELETE /api/anime/{anime_id}        # 删除动画
POST   /api/anime/smart-parse       # 智能解析动画信息
POST   /api/anime/smart-add         # 智能添加动画（支持连锁解析RSS）

# RSS源相关 ✅
GET    /api/anime/{anime_id}/rss-sources  # 获取动画的所有RSS源
GET    /api/rss-sources/{rss_source_id}   # 获取单个RSS源
POST   /api/rss-sources            # 创建RSS源
PUT    /api/rss-sources/{rss_source_id}   # 更新RSS源
DELETE /api/rss-sources/{rss_source_id}   # 删除RSS源

# 智能解析相关 ✅
GET    /api/smart-parser/sites     # 获取支持的网站列表
POST   /api/smart-parser/parse-anime  # 解析动画链接
POST   /api/smart-parser/parse-rss    # 解析RSS链接（待实现）

# 健康检查 ✅
GET    /api/health                  # 健康检查
```

**计划中的 API：**

```
# RSS源相关 📋
POST   /api/rss-sources/{id}/check  # 手动检查RSS源新链接
POST   /api/rss-sources/smart-parse # 智能解析RSS源信息
POST   /api/rss-sources/smart-add   # 智能添加RSS源

# 链接相关 📋
GET    /api/rss-sources/{id}/links  # 获取RSS源的所有链接（包含下载状态）
GET    /api/links/{id}              # 获取单个链接
GET    /api/links                   # 获取链接列表（支持过滤）
POST   /api/links/{id}/mark-downloaded  # 标记为已下载

# 下载器相关 📋
GET    /api/downloaders             # 获取所有下载器
POST   /api/downloaders             # 添加下载器
GET    /api/downloaders/{id}        # 获取单个下载器
PUT    /api/downloaders/{id}        # 更新下载器
DELETE /api/downloaders/{id}        # 删除下载器
POST   /api/downloaders/{id}/test   # 测试下载器连接
POST   /api/downloaders/{id}/set-default  # 设置为默认下载器
GET    /api/downloaders/default     # 获取默认下载器
GET    /api/downloaders/types       # 获取支持的下载器类型

# 下载任务相关 📋
GET    /api/downloads               # 获取所有下载任务
GET    /api/downloads/{id}          # 获取单个下载任务
POST   /api/downloads               # 创建下载任务
POST   /api/downloads/{id}/start    # 开始下载
POST   /api/downloads/{id}/pause    # 暂停下载
POST   /api/downloads/{id}/resume   # 恢复下载
POST   /api/downloads/{id}/cancel   # 取消下载
POST   /api/downloads/{id}/sync     # 同步下载状态
GET    /api/downloads/active        # 获取所有活跃的下载任务
GET    /api/links/{id}/downloads    # 获取链接的所有下载任务
```

## 5. 客户端设计

### 5.1 智能解析用户体验

智能解析功能通过交互式的方式为用户提供便捷的添加体验。当用户使用 `smart-add` 命令时，系统会：

1. **解析链接**：自动识别网站类型并提取信息
2. **显示选项**：如果解析结果有多个，以表格形式展示供用户选择
3. **交互选择**：用户可以通过输入数字或范围（如 1,2,3 或 1-3）选择多个选项
4. **确认添加**：显示即将添加的信息，用户确认后执行添加操作
5. **连锁操作**：对于动画智能解析，可选择是否继续解析RSS源

**交互式选择示例：**
```
正在解析链接: https://mikanani.me/Home/Bangumi/12345
找到 2 个可能的动画：

┌────┬────────────────────────────────────┬──────────────────────────┬────────┬────────┐
│ ID │ 标题                               │ 英文标题                 │ 状态   │ 集数   │
├────┼────────────────────────────────────┼──────────────────────────┼────────┼────────┤
│  1 │ 鬼灭之刃                           │ Demon Slayer             │ 连载中 │ 12集   │
│  2 │ 鬼灭之刃 柱训练篇                  │ Demon Slayer: Hashira    │ 连载中 │ 8集    │
│    │                                    │ Training Arc             │        │        │
└────┴────────────────────────────────────┴──────────────────────────┴────────┴────────┘

请选择要添加的动画（输入ID，如 1）：1

✓ 动画添加成功：鬼灭之刃

是否自动解析RSS源？[Y/n]: y

找到 3 个RSS源：

┌────┬────────────────┬──────────┬──────────────────┐
│ ID │ 名称           │ 画质     │ 自动下载         │
├────┼────────────────┼──────────┼──────────────────┤
│  1 │ 蜜柑计划 1080P │ 1080p    │ 是               │
│  2 │ 蜜柑计划 720P  │ 720p     │ 是               │
│  3 │ 蜜柑计划 480P  │ 480p     │ 是               │
└────┴────────────────┴──────────┴──────────────────┘

请选择要添加的RSS源（可多选，如 1,2 或 1-3）：1,2

✓ RSS源添加成功：蜜柑计划 1080P
✓ RSS源添加成功：蜜柑计划 720P
```

### 5.2 CLI 命令结构

基于 **cmd2** 框架构建命令行架构，提供交互式 Shell 环境，并集成 **rich** 库进行界面美化，支持表格、进度条、彩色输出、语法高亮等丰富的视觉效果。

**技术栈组合说明：**
- **cmd2**: 负责命令解析、参数处理、命令路由、交互式 Shell 等核心功能
- **rich**: 负责输出美化、表格渲染、进度条显示、颜色主题等视觉效果

**当前实现的命令：**

```
animeloader> help
Documented commands (type help <topic>):
========================================
anime       动画相关命令 ✅ (部分实现)
rss         RSS源相关命令 📋
link        链接相关命令 📋
downloader  下载器相关命令 📋
download    下载相关命令 📋
status      状态查询命令 📋
config      查看当前配置 ✅
exit/quit   退出程序 ✅
clear       清屏 ✅
```

**动画命令 (anime) ✅：**

```
animeloader> anime <子命令> [选项]

子命令:
  add         添加动画 ✅
  list        列出所有动画 ✅
  show        显示动画详情 ✅
  smart-add   智能添加动画（从链接自动解析）✅

示例:
  animeloader> anime add --title "鬼灭之刃" --title-en "Demon Slayer"
  animeloader> anime list --keyword "鬼灭"
  animeloader> anime show --id 1
  animeloader> anime smart-add --url "https://mikanani.me/Home/Bangumi/12345"
```

**RSS源命令 (rss) 📋：**

```
animeloader> rss <子命令> [选项]

子命令:
  add         添加RSS源 📋
  smart-add   智能添加RSS源（从链接自动解析）📋
  list        列出RSS源 📋
  remove      删除RSS源 📋
  update      更新RSS源 📋
  check       手动检查RSS源新链接 📋
  show        显示RSS源详情 📋
```

**链接命令 (link) 📋：**

```
animeloader> link <子命令> [选项]

子命令:
  list    列出链接 📋
  show    显示链接详情 📋
  filter  按类型过滤链接 📋
```

**下载器命令 (downloader) 📋：**

```
animeloader> downloader <子命令> [选项]

子命令:
  add          添加下载器 📋
  list         列出下载器 📋
  remove       删除下载器 📋
  update       更新下载器 📋
  show         显示下载器详情 📋
  test         测试下载器连接 📋
  set-default  设置默认下载器 📋
  types        查看支持的下载器类型 📋
```

**下载命令 (download) 📋：**

```
animeloader> download <子命令> [选项]

子命令:
  list    列出下载任务 📋
  pause   暂停下载 📋
  resume  恢复下载 📋
  start   开始下载 📋
  cancel  取消下载 📋
  status  查看下载状态 📋
  sync    同步下载状态 📋
```

**状态命令 (status) 📋：**

```
animeloader> status <子命令> [选项]

子命令:
  server  查看服务器状态 📋
  system  查看系统信息 📋
```

### 5.3 命令示例

**已实现的命令：**

```bash
# 添加动画
animeloader> anime add --title "鬼灭之刃" --title-en "Demon Slayer" --description "鬼灭之刃"

# 智能添加动画（从链接自动解析）
animeloader> anime smart-add --url "https://mikanani.me/Home/Bangumi/12345"
# 系统会自动解析链接，提取动画信息
# 如果解析结果有多个，会显示列表供用户选择：
# ┌────┬────────────────┬──────────────────────────┬────────┬────────┐
# │ ID │ 标题           │ 英文标题                 │ 状态   │ 集数   │
# ├────┼────────────────┼──────────────────────────┼────────┼────────┤
# │  1 │ 鬼灭之刃       │ Demon Slayer             │ 连载中 │ 12集   │
# │  2 │ 鬼灭之刃 柱训练篇 │ Demon Slayer: Hashira  │ 连载中 │ 8集    │
# └────┴────────────────┴──────────────────────────┴────────┴────────┘
# 请选择要添加的动画（输入ID，如 1）：1
# ✓ 动画添加成功：鬼灭之刃
# 是否自动解析RSS源？[Y/n]: y
# 找到 3 个RSS源：
# ┌────┬────────────────┬──────────┬──────────────────┐
# │ ID │ 名称           │ 画质     │ 自动下载         │
# ├────┼────────────────┼──────────┼──────────────────┤
# │  1 │ 蜜柑计划 1080P │ 1080p    │ 是               │
# │  2 │ 蜜柑计划 720P  │ 720p     │ 是               │
# │  3 │ 蜜柑计划 480P  │ 480p     │ 是               │
# └────┴────────────────┴──────────┴──────────────────┘
# 请选择要添加的RSS源（可多选，如 1,2 或 1-3）：1,2
# ✓ RSS源添加成功：蜜柑计划 1080P
# ✓ RSS源添加成功：蜜柑计划 720P

# 列出动画
animeloader> anime list

# 搜索动画
animeloader> anime list --keyword "鬼灭"

# 显示动画详情
animeloader> anime show --id 1

# 查看当前配置
animeloader> config

# 清屏
animeloader> clear

# 退出程序
animeloader> exit
# 或
animeloader> quit
```

**计划中的命令：**

```bash
# RSS源相关命令（计划中）
animeloader> rss add --anime-id 1 --name "DMHY 1080P" --url "https://example.com/rss" --quality 1080p
animeloader> rss smart-add --url "https://mikanani.me/RSS/Bangumi/12345" --anime-id 1
animeloader> rss list --anime-id 1
animeloader> rss show --id 1
animeloader> rss update --id 1 --quality 720p
animeloader> rss remove --id 1
animeloader> rss check --id 1

# 链接相关命令（计划中）
animeloader> link list --rss-source-id 1
animeloader> link filter --rss-source-id 1 --link-type magnet
animeloader> link show --id 1

# 下载器相关命令（计划中）
animeloader> downloader add --name "本地aria2" --type aria2 --config '{"host": "127.0.0.1", "port": 6800}'
animeloader> downloader list
animeloader> downloader show --id 1
animeloader> downloader test --id 1
animeloader> downloader set-default --id 1
animeloader> downloader types
animeloader> downloader remove --id 1

# 下载相关命令（计划中）
animeloader> download start --link-id 1
animeloader> download list
animeloader> download pause --task-id 1
animeloader> download resume --task-id 1
animeloader> download cancel --task-id 1
animeloader> download status --task-id 1
animeloader> download sync --task-id 1

# 状态查询命令（计划中）
animeloader> status server
animeloader> status system
```

## 6. 数据库设计

### 6.1 数据库初始化

```sql
-- 创建表时会自动生成
-- 使用 SQLAlchemy ORM 自动管理
```

### 6.2 索引设计

```python
# RSSSource 表
Index('idx_rss_source_anime_id', RSSSource.anime_id)
Index('idx_rss_source_is_active', RSSSource.is_active)

# Link 表
Index('idx_link_rss_source_id', Link.rss_source_id)
Index('idx_link_type', Link.link_type)
Index('idx_link_is_downloaded', Link.is_downloaded)
Index('idx_link_is_available', Link.is_available)
Index('idx_link_publish_date', Link.publish_date)

# Downloader 表
Index('idx_downloader_type', Downloader.downloader_type)
Index('idx_downloader_is_active', Downloader.is_active)
Index('idx_downloader_is_default', Downloader.is_default)

# DownloadTask 表
Index('idx_download_rss_source_id', DownloadTask.rss_source_id)
Index('idx_download_link_id', DownloadTask.link_id)
Index('idx_download_downloader_id', DownloadTask.downloader_id)
Index('idx_download_downloader_type', DownloadTask.downloader_type)
Index('idx_download_status', DownloadTask.status)
```

## 7. 配置管理

### 7.1 配置文件分离

系统采用分离的配置文件设计：
- **服务端配置**：可由用户指定位置（默认为 `~/.animeloader/server_config.yaml`），存储服务端运行所需的配置，包括数据库路径、下载目录等
- **客户端配置** (`client_config.yaml`)：可由客户端随意指定位置，存储客户端连接和显示设置

### 7.2 服务端配置文件

服务端配置文件可由用户通过命令行参数指定位置（默认为 `~/.animeloader/server_config.yaml`），存储服务端运行所需的配置，包括数据库路径、下载目录等。

```yaml
# ~/.animeloader/server_config.yaml
server:
  host: "127.0.0.1"
  port: 8000
  debug: false

database:
  path: "~/.animeloader/data/animeloader.db"  # 数据库文件路径，默认在用户目录下

rss:
  check_interval: 3600      # RSS检查间隔（秒）
  timeout: 30               # RSS请求超时（秒）
  max_links_per_source: 100 # 每个RSS源保留的最大链接数
  link_retention_days: 30   # 链接保留天数

download:
  download_dir: "~/.animeloader/downloads"  # 下载目录，默认在用户目录下
  max_concurrent_downloads: 3
  chunk_size: 8192
  retry_count: 3            # 下载失败重试次数
  retry_interval: 60        # 重试间隔（秒）
  auto_sync_interval: 30    # 自动同步下载状态间隔（秒）

link_types:
  enabled:
    - magnet                # 支持的链接类型
    - ed2k
  parsers:
    magnet: "server.link_parsers.magnet_parser.MagnetParser"
    ed2k: "server.link_parsers.ed2k_parser.Ed2kParser"

downloaders:
  enabled:
    - aria2                 # 支持的下载器类型
    - pikpak
  implementations:
    aria2: "server.downloaders.aria2_downloader.Aria2Downloader"
    pikpak: "server.downloaders.pikpak_downloader.PikPakDownloader"
  default_type: aria2       # 默认下载器类型

# aria2 默认配置模板
aria2:
  host: "127.0.0.1"
  port: 6800
  secret: ""
  timeout: 30

# pikpak 默认配置模板
pikpak:
  api_endpoint: "https://api-drive.mypikpak.com"  # PikPak API地址
  username: ""
  password: ""
  timeout: 60

scheduler:
  enabled: true

smart_parser:
  timeout: 30                # 网站解析超时时间（秒）
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"  # 用户代理
  max_results: 10            # 最大返回结果数
  auto_add_rss: true         # 智能添加动画时是否自动解析RSS源

logging:
  level: "INFO"
  file: "~/.animeloader/logs/animeloader.log"  # 日志文件路径，默认在用户目录下
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

### 7.3 客户端配置文件

客户端配置文件可由用户随意指定位置（默认为 `~/.animeloader/client_config.yaml`），包含连接服务器和显示相关的配置。

```yaml
# client_config.yaml
server:
  url: "http://127.0.0.1:8000"  # 服务端URL
  timeout: 30                    # 请求超时时间（秒）
  retry_count: 3                 # 请求失败重试次数

display:
  theme: "auto"                  # 主题: auto, light, dark
  table_max_rows: 20             # 表格默认显示的最大行数
  show_progress: true            # 是否显示下载进度条
  refresh_interval: 5            # 自动刷新间隔（秒，用于实时状态监控）
  
  # 颜色配置
  colors:
    success: "green"
    error: "red"
    warning: "yellow"
    info: "blue"
    download_speed: "cyan"
    upload_speed: "magenta"

ui:
  use_rich: true                 # 是否使用 rich 库进行美化显示
  use_cmd2: true                 # 是否使用 cmd2 框架（启用交互式 Shell）
  emoji: true                    # 是否在输出中使用 emoji
  compact_mode: false            # 紧凑模式（减少空白行）
  verbose: false                 # 详细输出模式
  
  # cmd2 选项
  cmd2:
    allow_cli_args: true         # 允许命令行参数
    shortcuts: true              # 启用快捷键
    persistent_history_file: "~/.animeloader/.cmd2_history"  # 命令历史文件

logging:
  level: "INFO"                  # 客户端日志级别
  file: ""                       # 客户端日志文件路径（空则不记录文件）

smart_parser:
  auto_select: false             # 当只有一个解析结果时是否自动选择
  show_details: true             # 是否显示详细信息
  confirm_before_add: true       # 添加前是否要求确认
```

### 7.4 配置文件加载优先级

**服务端配置加载顺序：**
1. 命令行参数指定的配置文件路径（`--config`）
2. `~/.animeloader/server_config.yaml`（用户主目录）
3. `server_config.yaml`（相对于项目根目录，仅用于开发环境）
4. 环境变量覆盖（可选）

**客户端配置加载顺序：**
1. 命令行参数指定的配置文件路径（`--config`）
2. `~/.animeloader/client_config.yaml`（用户主目录）
3. `client_config.yaml`（相对于项目根目录，仅用于开发环境）
4. 环境变量覆盖（可选）

## 8. 部署方案

### 8.1 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m server.database.init_db

# 启动服务端（使用项目根目录的 server_config.yaml）
python -m server.main

# 启动服务端（指定配置文件）
python -m server.main --config /path/to/custom_config.yaml

# 启动客户端（使用项目根目录的 client_config.yaml）
python -m client.main

# 启动客户端（指定配置文件）
python -m client.main --config /path/to/custom_config.yaml

# 添加默认下载器（可选）
animeloader> downloader add --name "本地aria2" --type aria2 --config '{"host": "127.0.0.1", "port": 6800, "secret": ""}' --default
```

### 8.2 生产环境

**服务端部署：**
```bash
# 创建服务端配置目录
mkdir -p ~/.animeloader

# 复制或创建配置文件
cp server_config.yaml ~/.animeloader/server_config.yaml

# 编辑配置文件，设置数据库路径、下载目录等
vim ~/.animeloader/server_config.yaml

# 使用 systemd 管理
# /etc/systemd/system/animeloader.service

[Unit]
Description=AnimeLoader Server
After=network.target

[Service]
Type=simple
User=anime
WorkingDirectory=/opt/animeloader
ExecStart=/usr/bin/python3 -m server.main --config /home/anime/.animeloader/server_config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**客户端部署：**
客户端可部署在任何能访问服务端的机器上，配置文件位置可自由指定：

```bash
# 创建客户端配置目录
mkdir -p ~/.animeloader

# 复制或创建配置文件
cp client_config.yaml ~/.animeloader/

# 编辑配置文件，设置服务端地址
vim ~/.animeloader/client_config.yaml

# 启动客户端
python -m client.main
```

## 9. 扩展性考虑

### 9.1 多用户支持

- 添加用户认证系统
- 实现用户权限管理
- 支持多用户独立订阅

### 9.2 链接类型扩展

系统采用插件化的解析器架构，支持灵活扩展新的链接类型：

**解析器接口设计：**
```python
class BaseParser(ABC):
    @abstractmethod
    def parse(self, url: str) -> dict:
        """解析链接，返回链接元数据"""
        pass

    @abstractmethod
    def validate(self, url: str) -> bool:
        """验证链接格式是否正确"""
        pass

    @abstractmethod
    def get_download_command(self, url: str, save_path: str) -> str:
        """获取下载命令"""
        pass
```

**添加新链接类型的步骤：**
1. 在 `server/link_parsers/` 目录下创建新的解析器类，继承 `BaseParser`
2. 实现抽象方法：`parse()`, `validate()`, `get_download_command()`
3. 在配置文件中注册新链接类型
4. 在 `Link.link_type` 中添加新类型

**示例：添加 HTTP 链接支持**
```python
# server/link_parsers/http_parser.py
class HttpParser(BaseParser):
    def parse(self, url: str) -> dict:
        # 解析HTTP链接
        return {"file_size": 0, "filename": ""}

    def validate(self, url: str) -> bool:
        return url.startswith("http://") or url.startswith("https://")

    def get_download_command(self, url: str, save_path: str) -> str:
        return f"wget -O {save_path} {url}"
```

### 9.3 下载器类型扩展

系统采用插件化的下载器架构，支持灵活扩展新的下载器类型：

**下载器接口设计：**
```python
class BaseDownloader(ABC):
    @abstractmethod
    def connect(self, config: dict) -> bool:
        """连接到下载器"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass

    @abstractmethod
    def add_task(self, url: str, options: dict) -> str:
        """添加下载任务，返回任务ID"""
        pass

    @abstractmethod
    def remove_task(self, task_id: str) -> bool:
        """移除下载任务"""
        pass

    @abstractmethod
    def pause_task(self, task_id: str) -> bool:
        """暂停下载任务"""
        pass

    @abstractmethod
    def resume_task(self, task_id: str) -> bool:
        """恢复下载任务"""
        pass

    @abstractmethod
    def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        pass

    @abstractmethod
    def get_global_status(self) -> dict:
        """获取下载器全局状态"""
        pass

    @abstractmethod
    def validate_config(self, config: dict) -> tuple[bool, str]:
        """验证配置是否正确，返回(是否有效, 错误信息)"""
        pass
```

**添加新下载器类型的步骤：**
1. 在 `server/downloaders/` 目录下创建新的下载器类，继承 `BaseDownloader`
2. 实现抽象方法：`connect()`, `disconnect()`, `add_task()`, `remove_task()`, `pause_task()`, `resume_task()`, `get_task_status()`, `get_global_status()`, `validate_config()`
3. 在配置文件中注册新下载器类型
4. 在 `Downloader.downloader_type` 中添加新类型

**示例：添加 qBittorrent 下载器支持**
```python
# server/downloaders/qbittorrent_downloader.py
class QBittorrentDownloader(BaseDownloader):
    def __init__(self):
        self.client = None

    def connect(self, config: dict) -> bool:
        from qbittorrentapi import Client
        self.client = Client(
            host=config.get('host', 'localhost'),
            port=config.get('port', 8080),
            username=config.get('username', ''),
            password=config.get('password', '')
        )
        try:
            self.client.auth_log_in()
            return True
        except Exception as e:
            return False

    def disconnect(self) -> bool:
        if self.client:
            self.client.auth_log_out()
        return True

    def add_task(self, url: str, options: dict) -> str:
        torrent = self.client.torrents_add(urls=[url], **options)
        return torrent

    def remove_task(self, task_id: str) -> bool:
        self.client.torrents_delete(delete_files=False, torrent_hashes=task_id)
        return True

    def pause_task(self, task_id: str) -> bool:
        self.client.torrents_pause(torrent_hashes=task_id)
        return True

    def resume_task(self, task_id: str) -> bool:
        self.client.torrents_resume(torrent_hashes=task_id)
        return True

    def get_task_status(self, task_id: str) -> dict:
        torrents = self.client.torrents_info(torrent_hashes=task_id)
        if torrents:
            t = torrents[0]
            return {
                'status': t.state,
                'progress': t.progress * 100,
                'download_speed': t.dlspeed,
                'upload_speed': t.upspeed,
                'downloaded_size': t.downloaded,
                'file_size': t.size
            }
        return {}

    def get_global_status(self) -> dict:
        info = self.client.transfer_info()
        return {
            'download_speed': info.dl_info_speed,
            'upload_speed': info.up_info_speed,
            'active_downloads': len(self.client.torrents_info(status_filter='downloading'))
        }

    def validate_config(self, config: dict) -> tuple[bool, str]:
        required_keys = ['host', 'port', 'username', 'password']
        for key in required_keys:
            if key not in config:
                return False, f"Missing required config key: {key}"
        return True, ""
```

### 9.4 多源支持

- 抽象来源接口
- 支持多个动画来源站点
- 实现来源插件机制

### 9.5 网站解析器扩展

系统采用插件化的网站解析器架构，支持灵活扩展新的动画网站：

**网站解析器接口设计：**
```python
class BaseSiteParser(ABC):
    @abstractmethod
    def can_parse(self, url: str) -> bool:
        """判断是否可以解析该URL"""
        pass

    @abstractmethod
    def parse_anime(self, url: str) -> List[Dict]:
        """解析动画信息，返回可能的动画列表"""
        pass

    @abstractmethod
    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        """解析RSS源信息，返回可能的RSS源列表"""
        pass

    @abstractmethod
    def get_site_name(self) -> str:
        """获取网站名称"""
        pass
```

**添加新网站支持的步骤：**
1. 在 `server/site_parsers/` 目录下创建新的网站解析器类，继承 `BaseSiteParser`
2. 实现抽象方法：`can_parse()`, `parse_anime()`, `parse_rss()`, `get_site_name()`
3. 在智能解析服务中注册新网站解析器
4. 更新支持的网站列表

**示例：添加 DMHY 支持器**
```python
# server/site_parsers/dmhy_parser.py
class DMHYParser(BaseSiteParser):
    def can_parse(self, url: str) -> bool:
        return 'dmhy.org' in url

    def parse_anime(self, url: str) -> List[Dict]:
        # 解析DMHY动画页面
        return [
            {
                'title': '动画标题',
                'title_en': 'English Title',
                'description': '描述',
                'cover_url': '封面URL',
                'status': 'ongoing',
                'total_episodes': 12
            }
        ]

    def parse_rss(self, url: str, anime_id: int) -> List[Dict]:
        # 解析DMHY RSS页面
        return [
            {
                'name': 'DMHY 1080P',
                'url': 'RSS链接',
                'quality': '1080p',
                'auto_download': True
            }
        ]

    def get_site_name(self) -> str:
        return "DMHY"
```

### 9.6 分布式下载

- 支持多节点部署
- 实现任务分发
- 负载均衡

## 10. 安全考虑

### 10.1 数据安全

- 敏感信息加密存储
- 定期数据库备份
- 访问日志记录

### 10.2 网络安全

- HTTPS 加密传输
- API 访问限流
- 输入验证和过滤

## 11. 测试策略

### 11.1 单元测试

- 测试各个服务模块
- 测试数据库操作
- 测试业务逻辑
- 测试智能解析服务（网站解析器、链接解析等）
- 测试配置加载和路径展开

### 11.2 集成测试

- 测试 API 接口
- 测试客户端-服务端交互
- 测试下载流程
- 测试智能添加流程（动画和RSS源的智能解析）
- 测试多选择交互逻辑

### 11.3 测试覆盖率目标

- 核心功能: 80%+
- 业务逻辑: 70%+
- 智能解析: 75%+
- 整体: 60%+