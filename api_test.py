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

for i in range(1,11):
  response={}
  for j in range(1,51):
    response[j] = clients[j].chat.completions.create(model="deepseek-chat",messages=messages[j])
    messages[j].append(response[j].choices[0].message)
  for j in range(1,51):
    for k in range(1,51):
      if(j!=k):
        messages[j].append({"role": "user","content":"第"+str(k)+"位员工说"+response[k]["content"]})
  message_overall.apend({"role":"user","content":"这是第"+str(i)+"轮"})
  for j in range(1,51):
    message_overall.append({"role":"user","content":"第"+str(j)+"位员工说"+response[j]["content"]})

response_init=clients[j].chat.completions.create(model="deepseek-chat",messages=message_overall)
print(response_init)
message_overall.append(response_init)
message_outside.append({"role":"user","content":response_init["content"]})
for k in range(1,51):
  messages[k].append({"role": "user","content":response_init["content"]})
response_init=clients[j].chat.completions.create(model="deepseek-chat",messages=message_overall)
print(response_init)
message_outside.append(response_init)
for k in range(1,51):
  messages[k].append({"role": "user","content":response_init["content"]})

#formal
for i in range(1,51):
  response={}
  for j in range(1,51):
    response[j] = clients[j].chat.completions.create(model="deepseek-chat",messages=messages[j])
    messages[j].append(response[j].choices[0].message)
  for j in range(1,51):
    for k in range(1,51):
      if(j!=k):
        messages[j].append({"role": "user","content":"第"+str(k)+"位员工说"+response[k]["content"]})
  for j in range(1,51):
    message_overall.append({"role":"user","content":"第"+str(j)+"位员工说"+response[j]["content"]})
  response_overall=clients[j].chat.completions.create(model="deepseek-chat",messages=message_overall)
  for k in range(1,51):
    messages[k].append({"role": "user","content":response_overall["content"]})
  response_outside=clients[j].chat.completions.create(model="deepseek-chat",messages=message_overall)
  message_outside.append(response_outside)
  for k in range(1,51):
    messages[k].append({"role": "user","content":response_outside["content"]})
  print(message_overall)
  print(message_outside)