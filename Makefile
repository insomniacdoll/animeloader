.PHONY: help build-all build-test clean

# 显示帮助信息
help:
	@echo "AnimeLoader 打包工具"
	@echo ""
	@echo "可用命令:"
	@echo "  make build-all     - 构建服务端和客户端二进制文件"
	@echo "  make build-test    - 测试打包配置"
	@echo "  make clean         - 清理构建文件"
	@echo ""

# 测试打包配置
build-test:
	@echo "测试打包配置..."
	python build.py test

# 构建全部
build-all:
	@echo "开始完整构建过程..."
	python build.py full

# 清理构建文件
clean:
	@echo "清理构建文件..."
	rm -rf dist/ build/ *.spec server_standalone.py client_standalone.py __pycache__ */__pycache__ */*/__pycache__ */*/*/__pycache__ *.egg-info .pytest_cache
	@echo "清理完成"

# 默认目标
all: build-all