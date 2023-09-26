import requests
import json

url = "http://0.0.0.0:8000/patient/"

payload = json.dumps({
  "messages": [
    {
      "role": "system",
      "content": "Bạn tên là gì?"
    },
    {
      "role": "user",
      "content": "Tôi tên là Bùi Văn Hợp"
    },
    {
      "role": "system",
      "content": "Bạn cảm thấy bây giờ thế nào?"
    },
    {
      "role": "user",
      "content": "Tôi thấy hơi sốt nhẹ"
    }
  ]
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
