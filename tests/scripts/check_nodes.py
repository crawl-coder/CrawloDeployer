import sys
import os
from datetime import datetime

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from backend.app.core.config import settings

def check_nodes():
    # 创建数据库引擎
    engine = create_engine(settings.DATABASE_URL)
    
    # 查询节点
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT id, hostname, ip_address, status, os, 
                   last_heartbeat, registered_at, version, 
                   cpu_cores, memory_gb, disk_gb
            FROM cp_nodes 
            ORDER BY id
        """))
        nodes = result.fetchall()
        
        print("数据库中的节点信息:")
        print("=" * 120)
        print(f"{'ID':<3} {'主机名':<20} {'IP地址':<15} {'状态':<8} {'OS':<8} {'最后心跳':<20} {'注册时间':<20} {'CPU':<4} {'内存(GB)':<8} {'磁盘(GB)':<8}")
        print("=" * 120)
        for node in nodes:
            last_heartbeat = node[5].strftime('%Y-%m-%d %H:%M:%S') if node[5] else 'N/A'
            registered_at = node[6].strftime('%Y-%m-%d %H:%M:%S') if node[6] else 'N/A'
            cpu_cores = node[7] if node[7] else 'N/A'
            memory_gb = f"{node[8]:.1f}" if node[8] else 'N/A'
            disk_gb = f"{node[9]:.1f}" if node[9] else 'N/A'
            
            print(f"{node[0]:<3} {node[1]:<20} {node[2]:<15} {node[3]:<8} {node[4]:<8} {last_heartbeat:<20} {registered_at:<20} {cpu_cores:<4} {memory_gb:<8} {disk_gb:<8}")

if __name__ == "__main__":
    check_nodes()