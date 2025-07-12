以下实现基于DeepSeek-V3的旅行规划助手系统。整个过程分为四个主要阶段：


### **第一阶段：环境准备与Cherry Studio安装**
#### 1. 系统要求检查
- 操作系统：Ubuntu 20.04+/Windows 10+（推荐Linux）
- 硬件要求：
  - CPU：8核+（推荐Intel Xeon或AMD EPYC）
  - GPU：NVIDIA A100 40GB+（最低RTX 3090 24GB）
  - 内存：64GB+
  - 存储：1TB SSD（用于模型存储）

#### 2. 安装Cherry Studio
```bash
# Linux安装步骤
wget https://cherrystudio.org/release/latest/cherry-studio-linux-x86_64.tar.gz
tar -xzvf cherry-studio-linux-x86_64.tar.gz
cd cherry-studio
./install.sh --with-cuda=12.1  # 匹配NVIDIA驱动版本

# Windows安装
下载 https://cherrystudio.org/windows/CherryStudioSetup.exe
以管理员身份运行，选择"Complete Installation"
```

#### 3. 验证安装
```bash
cherry-cli --version  # 应输出 v2.3.0+
cherry-server status  # 显示"Service Active"
```

---

### **第二阶段：模型服务部署**
#### 1. 下载DeepSeek-V3模型
```bash
# 使用HuggingFace镜像加速
huggingface-cli download deepseek-ai/deepseek-v3 --resume-download --local-dir ./models/deepseek-v3
```

#### 2. 配置模型服务
创建 `configs/deepseek-v3.yaml`：
```yaml
model_id: deepseek-v3
device_map: auto
quantization: bnb_4bit  # 节省显存
max_seq_len: 128000
api_endpoint: 0.0.0.0:8001
system_prompt: |
  你是一名资深旅行规划专家，精通全球目的地、交通方案和预算管理...
```

#### 3. 启动服务
```bash
cherry-server start -c configs/deepseek-v3.yaml
```

#### 4. 测试API
```bash
curl -X POST http://localhost:8001/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "规划3天上海行程"}]
  }'
```

---

### **第三阶段：MCP服务配置**
#### 1. 安装12306 MCP Server
```bash
git clone https://github.com/travel-mcp/12306-mcp-server
cd 12306-mcp-server
pip install -r requirements.txt
```

#### 2. 配置服务文件 `mcp_config.ini`
```ini
[core]
model_endpoint = http://localhost:8001/v1/chat
enable_web_search = true
search_api = https://api.search.travel/data

[plugins]
train_ticket = true
hotel_booking = true
weather_api = true
```

#### 3. 启动MCP服务
```bash
python mcp_server.py --port 8080 --config mcp_config.ini
```

#### 4. 验证连通性
```bash
# 检查服务状态
curl http://localhost:8080/healthcheck  # 应返回 {"status": "OK"}

# 测试联网能力
curl -X POST http://localhost:8080/query \
  -d '{"query": "查询从北京到上海的高铁最新票价"}'
```

---

### **第四阶段：旅行规划助手实现**
#### 1. 创建Web服务接口 `app.py`
```python
from flask import Flask, request
import requests

app = Flask(__name__)
MCP_ENDPOINT = "http://localhost:8080/query"

@app.route('/plan', methods=['POST'])
def plan_trip():
    user_request = request.json
    response = requests.post(MCP_ENDPOINT, json={
        "query": f"作为旅行规划专家，请规划行程：{user_request['demand']}",
        "web_search": True  # 启用联网模式
    })
    return response.json()

if __name__ == '__main__':
    app.run(port=5000)
```

#### 2. 启动服务
```bash
python app.py
```

#### 3. 测试完整流程
```bash
curl -X POST http://localhost:5000/plan \
  -H "Content-Type: application/json" \
  -d '{
    "demand": "一家四口（2成人+2儿童）7月20-25日北京自由行，预算2万元，包含故宫、长城和科技馆"
  }'
```

---

### **关键功能验证**
| 测试项目          | 预期结果                     |
|-------------------|-----------------------------|
| 联网票价查询      | 返回实时12306高铁票价数据    |
| 酒店推荐          | 展示携程/Booking真实房源     |
| 天气自适应调整    | 遇降雨自动推荐室内替代方案   |
| 预算分配          | 生成Excel格式费用明细表      |

---

### **常见问题解决**
1. **GPU内存不足**：
   ```bash
   # 修改模型配置
   quantization: bnb_8bit  # 更低精度
   max_seq_len: 32000      # 缩短上下文
   ```

2. **联网模式失效**：
   - 检查防火墙设置：`sudo ufw allow 8080`
   - 验证API密钥：在`mcp_config.ini`中添加`search_api_key=YOUR_KEY`

3. **行程优化建议**：
   ```python
   # 在app.py中添加优化指令
   "query": "作为专家优化行程：{demand}，要求：1)交通时间最小化 2)儿童友好设施 3)餐饮就近原则"
   ```

> 完整项目结构：
> ```
> /travel-planner
> ├── cherry-studio/      # 核心服务
> ├── models/             # DeepSeek-V3模型权重
> ├── 12306-mcp-server/   # MCP服务
> ├── app.py              # Web接口
> └── itineraries/        # 生成的行程PDF存档
> ```