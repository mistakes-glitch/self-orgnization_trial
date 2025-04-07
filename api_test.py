from openai import OpenAI

with open('api_key.ignore', 'r') as file: 
  content = file.read() 

clients={}
for i in range(1,51):
  clients[i] = OpenAI(api_key=content, base_url="https://api.deepseek.com")

client_overall=OpenAI(api_key=content, base_url="https://api.deepseek.com")
client_outside=OpenAI(api_key=content, base_url="https://api.deepseek.com")

# init 
with open('initpromt_employee.in', 'r') as file: 
  constitution = file.read() 
with open('initpromt_overall.in', 'r') as file: 
  oam = file.read() 
with open('initpromt_outside.in', 'r') as file: 
  osm = file.read() 

messages={}
for i in range(1,6):
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学公共管理专业毕业生，现入职芯片设计公司人大玫红光，你的员工编号是"+str(i)+constitution}]

for i in range(6,16):
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学集成电路专业毕业生，并且是一位资深ic设计工程师，并对芯片生产全栈有所了解，现入职芯片设计公司人大玫红光，你的员工编号是"+str(i)+constitution}]

for i in range(16,51):
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学集成电路专业毕业生，对芯片生产全栈有所了解，现入职芯片设计公司人大玫红光，你的员工编号是"+str(i)+constitution}]

message_overall=[{"role": "system", "content": oam}]
message_outside=[{"role": "system", "content": osm}]

# 初始化轮次
for i in range(1,11):
  response={}
  for j in range(1,51):
    response[j] = clients[j].chat.completions.create(model="deepseek-chat", messages=messages[j])
    messages[j].append(response[j].choices[0].message)
  
  # 添加其他员工的回复
  for j in range(1,51):
    for k in range(1,51):
      if j != k:
        content = response[k].choices[0].message.content  # 修复这里
        messages[j].append({"role": "user", "content": f"第{k}位员工说{content}"})
  
  # 添加总体管理信息
  message_overall.append({"role": "user", "content": f"这是第{i}轮"})  # 修正拼写错误
  for j in range(1,51):
    content = response[j].choices[0].message.content  # 修复这里
    message_overall.append({"role": "user", "content": f"第{j}位员工说{content}"})

# 处理初始响应
response_init = client_overall.chat.completions.create(model="deepseek-chat", messages=message_overall)
print(response_init.choices[0].message.content)
message_overall.append(response_init.choices[0].message)
message_outside.append({"role": "user", "content": response_init.choices[0].message.content})

for k in range(1,51):
  messages[k].append({"role": "user", "content": response_init.choices[0].message.content})

# 正式轮次
for _ in range(1,51):  # 建议使用更有意义的变量名
  response = {}
  for j in range(1,51):
    response[j] = clients[j].chat.completions.create(model="deepseek-chat", messages=messages[j])
    messages[j].append(response[j].choices[0].message)
  
  # 添加其他员工的回复
  for j in range(1,51):
    for k in range(1,51):
      if j != k:
        content = response[k].choices[0].message.content  # 修复这里
        messages[j].append({"role": "user", "content": f"第{k}位员工说{content}"})
  
  # 处理总体管理信息
  for j in range(1,51):
    content = response[j].choices[0].message.content  # 修复这里
    message_overall.append({"role": "user", "content": f"第{j}位员工说{content}"})
  
  response_overall = client_overall.chat.completions.create(model="deepseek-chat", messages=message_overall)
  overall_content = response_overall.choices[0].message.content  # 修复这里
  
  for k in range(1,51):
    messages[k].append({"role": "user", "content": overall_content})
  
  response_outside = client_outside.chat.completions.create(model="deepseek-chat", messages=message_outside)
  message_outside.append(response_outside.choices[0].message)  # 修复这里

# 保存结果时建议使用json格式
import json
with open('message_overall.out', 'w') as file: 
  json.dump(message_overall, file, ensure_ascii=False, indent=2)

with open('message_outside.out', 'w') as file: 
  json.dump(message_outside, file, ensure_ascii=False, indent=2)