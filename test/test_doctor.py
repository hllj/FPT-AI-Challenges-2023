import requests
import json

url = "http://0.0.0.0:8001/doctor"

payload = json.dumps({
  "summary": "Bạn có thể kê đơn một số loại thuốc mà tôi có thể dùng khi gặp phải các triệu chứng sau: Cổ họng sưng đỏ, khó nuốt, sốt 38-39 độ, ho , chảy nước mũi, mệt mỏi ?"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.json()['data']['response']['response'])
