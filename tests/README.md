# 测试目录结构说明

## 目录结构

```
tests/
├── scripts/          # 各种测试脚本和工具
├── archive/          # 归档的测试报告和历史文件
└── __init__.py       # Python包初始化文件
```

## scripts目录

包含各种用于测试、检查和开发的脚本：

- `add_crawlo_project.py` - 添加Crawlo示例项目的脚本
- `add_crawlo_task.py` - 添加Crawlo任务的脚本
- `check_*.py` - 各种检查数据库、节点、任务等的脚本
- `demo.py` - 示例演示脚本
- `run_crawlo_task.py` - 运行Crawlo任务的脚本
- `simulate_nodes.py` - 模拟节点的脚本
- `test_*.py` - 各种测试脚本

## archive目录

包含归档的历史测试报告和相关文档：

- `node_test_report.md` - 节点测试报告

## 使用说明

可以直接运行这些脚本进行测试和检查：

```bash
# 检查数据库状态
python tests/scripts/check_database.py

# 模拟节点
python tests/scripts/simulate_nodes.py

# 运行任务
python tests/scripts/run_crawlo_task.py <task_id>
```