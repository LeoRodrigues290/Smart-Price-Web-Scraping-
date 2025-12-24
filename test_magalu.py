import requests

def test_magalu():
    url = "https://www.magazineluiza.com.br/busca/iphone 13/"
    headers = {
         "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Length: {len(response.text)}")
        
        if "iphone" in response.text.lower():
            print("✅ 'iphone' found in response.")
        else:
            print("❌ 'iphone' NOT found in response.")
            
        with open("debug_magalu.html", "w") as f:
            f.write(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_magalu()
