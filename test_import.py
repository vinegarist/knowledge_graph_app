print("开始测试...")

try:
    import requests
    print("requests 导入成功")
except Exception as e:
    print(f"requests 导入失败: {e}")

try:
    response = requests.get("http://localhost:5000", timeout=5)
    print(f"后端连接成功: {response.status_code}")
except Exception as e:
    print(f"后端连接失败: {e}")

print("测试完成") 