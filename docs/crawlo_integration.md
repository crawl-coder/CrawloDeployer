# Crawlo 爬虫框架集成指南

## 概述

CrawloDeployer 系统现已支持多种爬虫框架的集成，包括 Crawlo、Scrapy 以及通用脚本。用户可以通过系统界面直接运行相应的命令来执行爬虫任务。

## 使用方法

### 1. 创建支持 Crawlo 的任务

在任务创建界面中：

1. 选择"执行器类型"为"Crawlo爬虫"
2. 在"爬虫名称"字段中指定要运行的爬虫名称（如 `myspider`）或使用 `all` 运行所有爬虫
3. 根据需要选择额外选项：
   - "JSON输出"：以 JSON 格式输出结果
   - "无统计信息"：运行时不显示统计信息
4. 可在"执行参数"中添加其他自定义参数（JSON格式）

### 2. Crawlo 命令映射

系统会将界面配置转换为以下 Crawlo 命令：

```
# 基本用法
crawlo run <spider_name>|all [--json] [--no-stats]

# 示例
crawlo run myspider
crawlo run all
crawlo run all --json --no-stats
```

### 3. 创建支持 Scrapy 的任务

在任务创建界面中：

1. 选择"执行器类型"为"Scrapy爬虫"
2. 在"爬虫名称"字段中指定要运行的爬虫名称
3. 可选地配置输出设置：
   - "输出文件名"：指定输出文件名
   - "输出格式"：选择输出格式（JSON、CSV、XML等）
   - "禁用日志"：运行时不显示日志信息
4. 可在"执行参数"中添加其他自定义参数（JSON格式）

### 4. Scrapy 命令映射

系统会将界面配置转换为以下 Scrapy 命令：

```
# 基本用法
scrapy crawl <spider_name> [-o output_file] [-t output_format] [--nolog]

# 示例
scrapy crawl myspider
scrapy crawl myspider -o output.json
scrapy crawl myspider -t csv --nolog
```

### 5. 创建通用脚本任务

对于不使用特定框架的脚本：

1. 选择"执行器类型"为"通用脚本"
2. 在"入口文件"字段中指定脚本文件名（如 `run.py`、`start.sh` 等）
3. 在"执行参数"中添加需要传递给脚本的参数（JSON格式）

## 参数说明

### Crawlo 参数
- `spider_name`：要运行的爬虫名称，可以是具体的爬虫名或 `all`（运行所有爬虫）
- `--json`：以 JSON 格式输出结果
- `--no-stats`：运行时不显示统计信息

### Scrapy 参数
- `spider_name`：要运行的爬虫名称
- `-o output_file`：指定输出文件名
- `-t output_format`：指定输出格式（json、csv、xml等）
- `--nolog`：运行时不显示日志信息

## 技术实现

### 后端实现

在 `backend/app/tasks/crawler_tasks.py` 中，我们扩展了 `_build_command` 函数来支持多种命令：

```python
def _build_command(entrypoint: str, args: dict = None, worker_os: str = "LINUX") -> list:
    # 检查是否是Crawlo命令
    if args and args.get("crawlo_command"):
        # 构建Crawlo命令
        
    # 检查是否是Scrapy命令
    if args and args.get("scrapy_command"):
        # 构建Scrapy命令
        
    # 默认处理通用脚本
```

### 前端实现

在前端任务管理界面中，我们添加了多种执行器类型的选择：

1. 执行器类型选择（通用脚本/Crawlo爬虫/Scrapy爬虫）
2. 针对不同执行器类型的特定表单字段
3. 动态显示相关配置选项

## 注意事项

1. 确保 Worker 节点已正确安装所需的框架（Crawlo、Scrapy等）
2. 项目环境需要包含爬虫所需的依赖
3. 所有任务仍然遵循系统的任务调度和监控机制
4. 对于通用脚本，确保入口文件具有正确的执行权限