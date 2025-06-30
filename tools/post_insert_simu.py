# main.py
import csv
import requests

url = 'http://127.0.0.1:5000/create_post'

def import_sample_data():
    with open('sample_data.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # 模擬使用者投稿
            data = {
                'nickname': row['Nickname'],
                'content': row['Content']
            }
            headers = {
                'User-Agent': row['User-Agent']
            }

            response = requests.post(url, data=data, headers=headers)
            if response.status_code == 200:
                continue
            else:
                print(f"Import Failed: {data['nickname']} - {data['content']}，Err：{response.status_code} / {response.text}")


if __name__ == "__main__":
    import_sample_data()