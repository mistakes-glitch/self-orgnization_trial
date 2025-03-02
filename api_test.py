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
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学公共管理专业毕业生，现入职芯片设计公司人大玫红光，你的员工编号是"+i+constitution}]

for i in range(6,16):
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学集成电路专业毕业生，并且是一位资深ic设计工程师，并对芯片生产全栈有所了解，现入职芯片设计公司人大玫红光，你的员工编号是"+i+constitution}]

for i in range(16,51):
  messages[i] = [{"role": "system", "content": "你是一位中国人民大学集成电路专业毕业生，对芯片生产全栈有所了解，现入职芯片设计公司人大玫红光，你的员工编号是"+i+constitution}]

message_overall=[{"role": "system", "content": oam}]
message_outside=[{"role": "system", "content": osm}]