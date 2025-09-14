import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
import threading

# 配置
BASE_URL = "http://127.0.0.1:8000/api/v1"
NUM_NODES = 10
HEARTBEAT_INTERVAL = 30  # 心跳间隔（秒）

# 模拟的节点信息
NODE_HOSTNAMES = [
    "worker-node-01", "worker-node-02", "worker-node-03", "worker-node-04", "worker-node-05",
    "worker-node-06", "worker-node-07", "worker-node-08", "worker-node-09", "worker-node-10"
]

NODE_IPS = [
    "192.168.1.101", "192.168.1.102", "192.168.1.103", "192.168.1.104", "192.168.1.105",
    "192.168.1.106", "192.168.1.107", "192.168.1.108", "192.168.1.109", "192.168.1.110"
]

NODE_OSES = ["LINUX", "WINDOWS", "MACOS"]
NODE_TAGS = ["gpu", "proxy", "chrome", "high-memory", "ssd", ""]

def send_heartbeat(hostname, ip):
    """发送心跳请求"""
    url = f"{BASE_URL}/nodes/heartbeat"
    os = random.choice(NODE_OSES)
    
    data = {
        "hostname": hostname,
        "ip": ip,
        "os": os
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ {hostname} 心跳上报成功")
            return True
        else:
            print(f"❌ {hostname} 心跳上报失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ {hostname} 心跳上报异常: {str(e)}")
        return False

def simulate_node(hostname, ip):
    """模拟单个节点的心跳"""
    # 首先发送一次心跳来注册节点
    send_heartbeat(hostname, ip)
    
    # 然后定期发送心跳
    while True:
        time.sleep(HEARTBEAT_INTERVAL)
        send_heartbeat(hostname, ip)

def main():
    print(f"开始模拟 {NUM_NODES} 台服务器节点的心跳上报...")
    print(f"心跳间隔: {HEARTBEAT_INTERVAL} 秒")
    print("=" * 50)
    
    # 使用线程池模拟多个节点并发上报心跳
    with ThreadPoolExecutor(max_workers=NUM_NODES) as executor:
        futures = []
        for i in range(NUM_NODES):
            hostname = NODE_HOSTNAMES[i]
            ip = NODE_IPS[i]
            future = executor.submit(simulate_node, hostname, ip)
            futures.append(future)
        
        # 等待所有线程完成（实际上不会完成，因为是无限循环）
        for future in futures:
            try:
                future.result(timeout=1)  # 短暂等待以检查是否有立即错误
            except:
                pass  # 忽略超时异常，因为心跳是持续进行的

if __name__ == "__main__":
    main()