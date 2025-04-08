import json
import random
from openai import OpenAI
from tiktoken import get_encoding
import concurrent.futures  # 新增多线程支持库


# 初始化编码器
enc = get_encoding("cl100k_base")

# 读取API密钥
with open('api_key.ignore', 'r') as file:
    api_key = file.read().strip()

# 初始化客户端
clients = {i: OpenAI(api_key=api_key, base_url="https://api.deepseek.com") for i in range(1, 51)}
client_overall = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
client_outside = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

# 消息截断函数
def trim_messages(message_list, max_tokens=30000):
    """保持消息总长度不超过max_tokens"""
    total = 0
    trimmed = []
    for msg in reversed(message_list):
        tokens = len(enc.encode(msg["content"]))
        if total + tokens > max_tokens:
            break
        trimmed.append(msg)
        total += tokens
    return list(reversed(trimmed))

# 读取初始化提示
def load_prompt(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

constitution = load_prompt('initpromt_employee.in')
oam = load_prompt('initpromt_overall.in')
osm = load_prompt('initpromt_outside.in')

# 初始化消息系统
messages = {}
for i in range(1, 6):
    messages[i] = [{
        "role": "system",
        "content": f"你是一位中国人民大学公共管理专业毕业生，现入职芯片设计公司人大玫红光，你的员工编号是{i}{constitution}"
    }]

for i in range(6, 16):
    messages[i] = [{
        "role": "system", 
        "content": f"你是一位中国人民大学集成电路专业毕业生，资深IC设计工程师，现入职芯片设计公司人大玫红光，你的员工编号是{i}{constitution}"
    }]

for i in range(16, 51):
    messages[i] = [{
        "role": "system",
        "content": f"你是一位中国人民大学集成电路专业毕业生，现入职芯片设计公司人大玫红光，你的员工编号是{i}{constitution}"
    }]

message_overall = [{"role": "system", "content": oam}]
message_outside = [{"role": "system", "content": osm}]

def process_employee(client_id, client, message_history, max_tokens):
    """多线程处理单个员工的函数"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=trim_messages(message_history, max_tokens)
        )
        message_obj = response.choices[0].message
        return {
            "client_id": client_id,
            "response": response,
            "new_message": {
                "role": message_obj.role,
                "content": message_obj.content
            },
            "error": None
        }
    except Exception as e:
        print(f"员工{client_id}处理异常: {str(e)}")
        return {
            "client_id": client_id,
            "response": None,
            "new_message": None,
            "error": str(e)
        }

# 修改后的初始化阶段（示例修改部分）
for init_round in range(1, 3):
    print(f"正在处理初始化轮次 {init_round}/2")
    
    # 使用线程池处理员工响应
    responses = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:  # 控制并发数
        futures = []
        for j in range(1, 51):
            futures.append(
                executor.submit(
                    process_employee,
                    client_id=j,
                    client=clients[j],
                    message_history=messages[j],
                    max_tokens=2000
                )
            )
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result["new_message"]:
                messages[result["client_id"]].append(result["new_message"])
                responses[result["client_id"]] = result["response"]

    # 员工间通信也改为多线程
    def process_communication(client_id):
        colleagues = random.sample(range(1, 51), 3)
        for k in colleagues:
            if client_id != k and k in responses:
                message_obj = responses[k].choices[0].message
                messages[client_id].append({
                    "role": "user",
                    "content": f"第{k}位员工观点摘要：{message_obj.content[:100]}..."
                })
        messages[client_id] = trim_messages(messages[client_id], 5000)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_communication, range(1, 51))
    
    # ...（保持原有摘要生成逻辑不变）...
    summary_prompt = [{
        "role": "user",
        "content": "请用200字概括本阶段讨论重点：" + "\n".join(
            [f"员工{j}: {responses[j].choices[0].message.content[:200]}" 
             for j in responses if j in responses]
        )
    }]
    
    try:
        summary_resp = client_overall.chat.completions.create(
            model="deepseek-chat",
            messages=trim_messages([*message_overall, *summary_prompt], 30000)
        )
        message_overall.append({
            "role": "assistant",
            "content": summary_resp.choices[0].message.content[:1000]
        })
    except Exception as e:
        print(f"摘要生成失败: {str(e)}")

# 修改后的正式处理阶段
for round in range(1, 11):
    print(f"正在处理正式轮次 {round}/10")
    
    # 多线程处理员工响应
    responses = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for j in range(1, 51):
            futures.append(
                executor.submit(
                    process_employee,
                    client_id=j,
                    client=clients[j],
                    message_history=messages[j],
                    max_tokens=3000
                )
            )
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result["new_message"]:
                messages[result["client_id"]].append(result["new_message"])
                responses[result["client_id"]] = result["response"]

    # 多线程处理跨员工通信
    def process_round_communication(client_id):
        colleagues = random.sample(range(1, 51), 5)
        for k in colleagues:
            if client_id != k and k in responses:
                message_obj = responses[k].choices[0].message
                messages[client_id].append({
                    "role": "user",
                    "content": f"第{round}轮第{k}位同事观点：{message_obj.content[:200]}..."
                })
        messages[client_id] = trim_messages(messages[client_id], 6000)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(process_round_communication, range(1, 51))
    
    # 生成管理摘要
    try:
        summary_resp = client_overall.chat.completions.create(
            model="deepseek-chat",
            messages=trim_messages([
                *message_overall,
                {"role": "user", "content": f"汇总第{round}轮50位员工的以下观点：" + 
                 "\n".join([f"{k}: {v.choices[0].message.content[:200]}" 
                          for k, v in responses.items()])}
            ], 40000)
        )
        message_overall.append({
            "role": "assistant",
            "content": summary_resp.choices[0].message.content[:1500]
        })
    except Exception as e:
        print(f"正式摘要生成失败: {str(e)}")
    
    # 外部沟通
    try:
        outside_resp = client_outside.chat.completions.create(
            model="deepseek-chat",
            messages=trim_messages(message_outside, 30000))
        message_outside.append({
            "role": outside_resp.choices[0].message.role,
            "content": outside_resp.choices[0].message.content
        })
    except Exception as e:
        print(f"外部沟通失败: {str(e)}")

# 保存结果
with open('message_overall.out', 'w', encoding='utf-8') as f:
    json.dump(message_overall, f, ensure_ascii=False, indent=2)

with open('message_outside.out', 'w', encoding='utf-8') as f:
    json.dump(message_outside, f, ensure_ascii=False, indent=2)

print("处理完成，结果已保存")