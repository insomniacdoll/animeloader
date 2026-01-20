# 测试文档

## 测试目录结构

```
animeloader/
├── server/tests/              # 服务端测试
│   ├── __init__.py
│   ├── test_smart_parser.py  # 蜜柑计划解析器测试 ✅
│   ├── test_smart_add.py     # 智能添加功能测试 ✅
│   └── test_api.py           # 服务端API测试 ✅
├── client/tests/              # 客户端测试
│   ├── __init__.py
│   └── test_smart_add.py     # 客户端智能添加测试 ✅
└── run_tests.py              # 运行所有测试的脚本 ✅
```

## 运行测试

### 运行所有测试

```bash
# 使用虚拟环境
source venv/bin/activate
python run_tests.py
```

### 单独运行测试

#### 服务端测试

```bash
# 蜜柑计划解析器测试（不需要服务端）
python server/tests/test_smart_parser.py

# 智能添加功能测试（不需要服务端）
python server/tests/test_smart_add.py

# 服务端API测试（需要先启动服务端）
python -m server.main --config server_config.yaml &
python server/tests/test_api.py
```

#### 客户端测试

```bash
# 客户端智能添加测试（需要先启动服务端）
python -m server.main --config server_config.yaml &
python client/tests/test_smart_add.py
```

## 测试说明

### 1. 蜜柑计划解析器测试 (`test_smart_parser.py`) ✅

测试蜜柑计划网站的解析功能，包括：
- 动画信息提取（标题、描述、封面等）
- RSS 源提取（默认 RSS 和字幕组 RSS）
- 解析结果验证

**运行条件**：无需启动服务端

**测试 URL**：https://mikanani.me/Home/Bangumi/3824

**测试文件位置**：`server/tests/test_smart_parser.py`

### 2. 智能添加功能测试 (`test_smart_add.py`) ✅

测试智能添加动画的完整流程，包括：
- 智能解析动画信息
- 创建动画记录
- 添加 RSS 源
- 查询动画和 RSS 源

**运行条件**：无需启动服务端

**测试文件位置**：`server/tests/test_smart_add.py`

### 3. 服务端 API 测试 (`test_api.py`) ✅

测试服务端 REST API，包括：
- 健康检查
- 智能解析 API
- 智能添加 API
- 获取动画列表
- 获取支持的网站

**运行条件**：需要先启动服务端

**测试文件位置**：`server/tests/test_api.py`

### 4. 客户端智能添加测试 (`test_smart_add.py`) ✅

测试客户端的智能添加交互流程，包括：
- 调用智能解析 API
- 显示解析结果
- 选择动画和 RSS 源
- 调用智能添加 API

**运行条件**：需要先启动服务端

**测试文件位置**：`client/tests/test_smart_add.py`

## 测试结果

所有测试应通过，输出如下：

```
============================================================
测试结果汇总
============================================================
1. 蜜柑计划解析器测试: ✓ 通过
2. 服务端API测试: ✓ 通过
3. 智能添加测试: ✓ 通过
4. 客户端测试: ✓ 通过

============================================================
[成功] 所有测试通过
============================================================
```

## 测试覆盖率

当前测试覆盖的功能模块：

- ✅ **智能解析服务**：蜜柑计划网站解析器
- ✅ **动画管理服务**：创建、查询动画
- ✅ **RSS源管理服务**：创建、查询RSS源
- ✅ **服务端API**：动画相关API、智能解析API
- ✅ **客户端命令**：智能添加命令

待测试的功能模块：

- 📋 **链接管理服务**
- 📋 **下载器管理服务**
- 📋 **下载任务管理服务**
- 📋 **调度服务**
- 📋 **其他客户端命令**（rss、link、downloader、download、status）

## 测试环境要求

- Python 3.12+
- 已安装所有依赖包（见 `requirements.txt`）
- 网络连接（用于测试蜜柑计划网站解析）
- SQLite 数据库支持

## 注意事项

1. **服务端API测试**需要先启动服务端，建议在后台运行
2. **客户端测试**需要服务端正在运行
3. 测试过程中可能会创建临时数据库文件，测试结束后会自动清理
4. 测试蜜柑计划解析器时，请确保网络连接正常
5. 如果测试失败，请检查：
   - 是否已正确安装所有依赖
   - 服务端是否正在运行（对于需要服务端的测试）
   - 网络连接是否正常（对于网站解析测试）
   - 端口是否被占用（默认服务端端口为 8000）