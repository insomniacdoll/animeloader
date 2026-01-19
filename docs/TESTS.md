# 测试文档

## 测试目录结构

```
animeloader/
├── server/tests/              # 服务端测试
│   ├── __init__.py
│   ├── test_smart_parser.py  # 蜜柑计划解析器测试
│   ├── test_smart_add.py     # 智能添加功能测试
│   └── test_api.py           # 服务端API测试
├── client/tests/              # 客户端测试
│   ├── __init__.py
│   └── test_smart_add.py     # 客户端智能添加测试
└── run_tests.py              # 运行所有测试的脚本
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

### 1. 蜜柑计划解析器测试 (`test_smart_parser.py`)

测试蜜柑计划网站的解析功能，包括：
- 动画信息提取（标题、描述、封面等）
- RSS 源提取（默认 RSS 和字幕组 RSS）
- 解析结果验证

**运行条件**：无需启动服务端

**测试 URL**：https://mikanani.me/Home/Bangumi/3824

### 2. 智能添加功能测试 (`test_smart_add.py`)

测试智能添加动画的完整流程，包括：
- 智能解析动画信息
- 创建动画记录
- 添加 RSS 源
- 查询动画和 RSS 源

**运行条件**：无需启动服务端

### 3. 服务端 API 测试 (`test_api.py`)

测试服务端 REST API，包括：
- 健康检查
- 智能解析 API
- 智能添加 API
- 获取动画列表
- 获取支持的网站

**运行条件**：需要先启动服务端

### 4. 客户端智能添加测试 (`test_smart_add.py`)

测试客户端的智能添加交互流程，包括：
- 调用智能解析 API
- 显示解析结果
- 选择动画和 RSS 源
- 调用智能添加 API

**运行条件**：需要先启动服务端

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