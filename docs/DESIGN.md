# animeloader 项目设计文档

## 1. 项目概述

animeloader 是一个用于订阅动画发布和管理动画下载内容的 Python 应用程序。系统采用客户端-服务端架构，支持用户通过命令行界面管理动画订阅、查看下载状态和配置定时任务。

### 1.1 核心功能

- **动画订阅管理**：添加、删除、修改动画订阅信息
- **RSS源管理**：添加、删除、检查RSS订阅源
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
├── requirements.txt      # 依赖列表
├── config.yaml           # 默认配置文件（仅用于开发）
├── server/               # 服务端代码
│   ├── __init__.py
│   ├── main.py           # 服务端入口
│   ├── config.yaml       # 服务端配置文件（部署时与应用在一起）
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
│   │   └── scheduler_service.py  # 调度服务
│   ├── parsers/          # 链接解析器（可扩展）
│   │   ├── __init__.py
│   │   ├── base_parser.py      # 基础解析器
│   │   ├── magnet_parser.py    # 磁力链接解析器
│   │   └── ed2k_parser.py      # ed2k链接解析器
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
│       └── logger.py
└── client/               # 客户端代码
    ├── __init__.py
    ├── main.py           # 客户端入口
    ├── commands/         # CLI 命令
    │   ├── __init__.py
    │   ├── rss_commands.py       # RSS源命令
    │   ├── link_commands.py      # 链接命令
    │   ├── download_commands.py  # 下载命令
    │   ├── downloader_commands.py # 下载器命令
    │   └── status_commands.py    # 状态命令
    └── api/              # API 客户端
        ├── __init__.py
        └── client.py
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

#### 4.2.1 RSSService (RSS源管理服务)

- `add_rss_source(anime_id, name, url, quality, auto_download)` - 添加RSS源
- `remove_rss_source(rss_source_id)` - 删除RSS源
- `update_rss_source(rss_source_id, **kwargs)` - 更新RSS源
- `get_rss_sources(anime_id)` - 获取动画的所有RSS源
- `get_rss_source(rss_source_id)` - 获取单个RSS源
- `fetch_rss_feed(rss_source_id)` - 获取RSS源的最新内容
- `parse_rss_feed(rss_url)` - 解析RSS订阅内容
- `check_new_links(rss_source_id)` - 检查RSS源的新链接

#### 4.2.2 LinkService (链接管理服务)

- `add_link(rss_source_id, episode_number, episode_title, link_type, url, **kwargs)` - 添加链接
- `get_links(rss_source_id, is_downloaded=None)` - 获取RSS源的所有链接
- `get_link(link_id)` - 获取单个链接
- `mark_as_downloaded(link_id)` - 标记链接为已下载
- `update_link_status(link_id, is_available)` - 更新链接可用状态
- `get_available_links(rss_source_id)` - 获取可用的下载链接
- `filter_links_by_type(rss_source_id, link_type)` - 按链接类型过滤

#### 4.2.3 DownloadService (下载服务)

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

#### 4.2.4 DownloaderService (下载器管理服务)

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

#### 4.2.5 SchedulerService (调度服务)

- `start_scheduler()` - 启动调度器
- `stop_scheduler()` - 停止调度器
- `add_check_job(rss_source_id, interval)` - 添加RSS源检查任务
- `remove_check_job(job_id)` - 移除检查任务
- `check_rss_source(rss_source_id)` - 检查RSS源的新链接

#### 4.2.6 LinkParserService (链接解析服务 - 可扩展)

- `parse_link(link_type, url)` - 根据链接类型解析链接
- `get_parser(link_type)` - 获取对应链接类型的解析器
- `register_parser(link_type, parser_class)` - 注册新的链接类型解析器
- `validate_link(link_type, url)` - 验证链接格式是否正确

#### 4.2.7 DownloaderManagerService (下载器管理服务 - 可扩展)

- `get_downloader(downloader_type)` - 获取对应类型的下载器实例
- `register_downloader(downloader_type, downloader_class)` - 注册新的下载器类型
- `get_supported_downloader_types()` - 获取支持的下载器类型列表
- `validate_downloader_config(downloader_type, config)` - 验证下载器配置

### 4.3 API 接口

#### RESTful API 设计

```
# 动画相关
GET    /api/anime                   # 搜索动画
GET    /api/anime/{id}              # 获取动画详情
POST   /api/anime                   # 创建动画

# RSS源相关
GET    /api/anime/{id}/rss-sources  # 获取动画的所有RSS源
POST   /api/anime/{id}/rss-sources  # 添加RSS源
GET    /api/rss-sources/{id}        # 获取单个RSS源
PUT    /api/rss-sources/{id}        # 更新RSS源
DELETE /api/rss-sources/{id}        # 删除RSS源
POST   /api/rss-sources/{id}/check  # 手动检查RSS源新链接

# 链接相关
GET    /api/rss-sources/{id}/links  # 获取RSS源的所有链接（包含下载状态）
GET    /api/links/{id}              # 获取单个链接
GET    /api/links                   # 获取链接列表（支持过滤）
POST   /api/links/{id}/mark-downloaded  # 标记为已下载

# 下载器相关
GET    /api/downloaders             # 获取所有下载器
POST   /api/downloaders             # 添加下载器
GET    /api/downloaders/{id}        # 获取单个下载器
PUT    /api/downloaders/{id}        # 更新下载器
DELETE /api/downloaders/{id}        # 删除下载器
POST   /api/downloaders/{id}/test   # 测试下载器连接
POST   /api/downloaders/{id}/set-default  # 设置为默认下载器
GET    /api/downloaders/default     # 获取默认下载器
GET    /api/downloaders/types       # 获取支持的下载器类型

# 下载任务相关
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

### 5.1 CLI 命令结构

基于 **cmd2** 框架构建命令行架构，提供交互式 Shell 环境，并集成 **rich** 库进行界面美化，支持表格、进度条、彩色输出、语法高亮等丰富的视觉效果。

**技术栈组合说明：**
- **cmd2**: 负责命令解析、参数处理、命令路由、交互式 Shell 等核心功能
- **rich**: 负责输出美化、表格渲染、进度条显示、颜色主题等视觉效果

```
animeloader> help
Documented commands (type help <topic>):
========================================
anime       动画相关命令
rss         RSS源相关命令
link        链接相关命令
downloader  下载器相关命令
download    下载相关命令
status      状态查询命令

animeloader> anime --help
Usage: anime [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add     添加动画
  list    列出所有动画
  show    显示动画详情

animeloader> rss --help
Usage: rss [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add     添加RSS源
  list    列出RSS源
  remove  删除RSS源
  update  更新RSS源
  check   手动检查RSS源新链接
  show    显示RSS源详情

animeloader> link --help
Usage: link [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  list    列出链接
  show    显示链接详情
  filter  按类型过滤链接

animeloader> downloader --help
Usage: downloader [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  add     添加下载器
  list    列出下载器
  remove  删除下载器
  update  更新下载器
  show    显示下载器详情
  test    测试下载器连接
  set-default 设置默认下载器
  types   查看支持的下载器类型

animeloader> download --help
Usage: download [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  list    列出下载任务
  pause   暂停下载
  resume  恢复下载
  start   开始下载
  cancel  取消下载
  status  查看下载状态
  sync    同步下载状态

animeloader> status --help
Usage: status [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  server  查看服务器状态
  system  查看系统信息
```

### 5.2 命令示例

```bash
# 添加动画
animeloader> anime add --title "鬼灭之刃" --title-en "Demon Slayer" --description "鬼灭之刃"

# 列出动画
animeloader> anime list

# 显示动画详情
animeloader> anime show --id 1

# 添加RSS源
animeloader> rss add --anime-id 1 --name "DMHY 1080P" --url "https://example.com/rss" --quality 1080p --auto-download

# 列出RSS源
animeloader> rss list --anime-id 1

# 显示RSS源详情（包含已下载的链接）
animeloader> rss show --id 1

# 手动检查RSS源新链接
animeloader> rss check --id 1

# 更新RSS源
animeloader> rss update --id 1 --quality 720p

# 删除RSS源
animeloader> rss remove --id 1

# 列出链接
animeloader> link list --rss-source-id 1

# 按类型过滤链接
animeloader> link filter --rss-source-id 1 --link-type magnet

# 显示链接详情
animeloader> link show --id 1

# 添加aria2下载器
animeloader> downloader add --name "本地aria2" --type aria2 --config '{"host": "127.0.0.1", "port": 6800, "secret": ""}' --default

# 添加pikpak下载器
animeloader> downloader add --name "PikPak离线" --type pikpak --config '{"username": "", "password": ""}'

# 列出下载器
animeloader> downloader list

# 显示下载器详情
animeloader> downloader show --id 1

# 测试下载器连接
animeloader> downloader test --id 1

# 设置默认下载器
animeloader> downloader set-default --id 2

# 查看支持的下载器类型
animeloader> downloader types

# 删除下载器
animeloader> downloader remove --id 2

# 开始下载（使用默认下载器）
animeloader> download start --link-id 1

# 开始下载（指定下载器）
animeloader> download start --link-id 1 --downloader-id 1

# 查看下载任务
animeloader> download list

# 查看链接的下载任务
animeloader> download list --link-id 1

# 暂停下载
animeloader> download pause --task-id 1

# 恢复下载
animeloader> download resume --task-id 1

# 取消下载
animeloader> download cancel --task-id 1

# 同步下载状态
animeloader> download sync --task-id 1

# 查看下载状态
animeloader> download status --task-id 1

# 查看服务器状态
animeloader> status server
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
- **服务端配置** (`server/config.yaml`)：部署时与应用在一起，存储服务端运行所需的配置
- **客户端配置** (`client_config.yaml`)：可由客户端随意指定位置，存储客户端连接和显示设置

### 7.2 服务端配置文件

服务端配置文件位于 `server/config.yaml`，部署时与服务器应用目录在一起。

```yaml
# server/config.yaml
server:
  host: "127.0.0.1"
  port: 8000
  debug: false

database:
  path: "./data/animeloader.db"

rss:
  check_interval: 3600      # RSS检查间隔（秒）
  timeout: 30               # RSS请求超时（秒）
  max_links_per_source: 100 # 每个RSS源保留的最大链接数
  link_retention_days: 30   # 链接保留天数

download:
  download_dir: "./downloads"
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
    magnet: "server.parsers.magnet_parser.MagnetParser"
    ed2k: "server.parsers.ed2k_parser.Ed2kParser"

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

logging:
  level: "INFO"
  file: "./logs/animeloader.log"
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
```

### 7.4 配置文件加载优先级

**服务端配置加载顺序：**
1. `server/config.yaml`（相对于服务器应用目录）
2. 环境变量覆盖（可选）

**客户端配置加载顺序：**
1. 命令行参数指定的配置文件路径（`--config`）
2. `~/.animeloader/client_config.yaml`（用户主目录）
3. 环境变量覆盖（可选）

## 8. 部署方案

### 8.1 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -m server.database.init_db

# 启动服务端（使用 server/config.yaml 配置）
python -m server.main

# 启动客户端（使用默认配置 ~/.animeloader/client_config.yaml）
python -m client.main

# 启动客户端（指定配置文件）
python -m client.main --config /path/to/custom_config.yaml

# 添加默认下载器（可选）
animeloader> downloader add --name "本地aria2" --type aria2 --config '{"host": "127.0.0.1", "port": 6800, "secret": ""}' --default
```

### 8.2 生产环境

**服务端部署：**
```bash
# 使用 systemd 管理
# /etc/systemd/system/animeloader.service

[Unit]
Description=AnimeLoader Server
After=network.target

[Service]
Type=simple
User=anime
WorkingDirectory=/opt/animeloader
ExecStart=/usr/bin/python3 -m server.main
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
1. 在 `server/parsers/` 目录下创建新的解析器类，继承 `BaseParser`
2. 实现抽象方法：`parse()`, `validate()`, `get_download_command()`
3. 在配置文件中注册新链接类型
4. 在 `Link.link_type` 中添加新类型

**示例：添加 HTTP 链接支持**
```python
# server/parsers/http_parser.py
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

### 9.5 分布式下载

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

### 11.2 集成测试

- 测试 API 接口
- 测试客户端-服务端交互
- 测试下载流程

### 11.3 测试覆盖率目标

- 核心功能: 80%+
- 业务逻辑: 70%+
- 整体: 60%+