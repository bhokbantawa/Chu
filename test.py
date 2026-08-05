import requests
proxy = "http://A0s7hfRRSYOjI90:Dw8y5rDvityH0Wk@74.122.57.76:44384"
try:
    resp = requests.get("https://httpbun.com/ip", proxies={"http": proxy, "https": proxy}, timeout=10)
    print(resp.json())
except Exception as e:
    print("Proxy dead:", e)
    
   