# CosplayDivaBlack
場次姬 - 匿名投稿平台

# 介紹
本專案是一套專為Cosplay社團設計的匿名投稿管理系統。<br>
原意是旨在協助圈內社群蒐集、整理、查閱各類黑名單事件，同時能在需要的時候提供相關證明，保障同好交流安全、提升圈內自我保護意識。<br>
若想使用該專案到你的社團/想要建置一份屬於自己的匿名平台，可以自由Clone（複製）該份專案並做些修改，爾後即可發布。

## Deploy
```
pip install -r requirement.txt
```

## Run
1. 將`config_example.ini`改名成`config.ini`，並且修改以下參數：
```ini
[web]
chinese_name = 場次姬                        # 網頁中文名稱
english_name = Cosplay Diva Black           # 網頁英文名稱


[app]
secret_key = Your_Super_Secret_Key_123456   # Secret
admin_password = 1234567890abcdef           # 管理員密碼
sql_file = web.db                           # Sqlite資料庫名稱
debug = true                                # Flask Debug模式開關

[security]
hash_salt = MyUltraHashSalt_XYZ             # 密碼鹽 (Hash)
```
2. 輸入以下指令運行。
```
python app.py
```
3. 在瀏覽器輸入`http://127.0.0.1:5000/`瀏覽網頁。

# 專案架構
```
root/
├── app.py                      # 主入口
├── templates/
│   ├── index.html              # 公開投稿/查詢頁面
│   ├── header.html             # 共用頁首
│   ├── footer.html             # 共用頁尾
│   ├── login.html              # 管理員登入頁面
│   ├── navbar.html             # 公開頁面共用導航欄
│   ├── admin_navbar.html       # 管理員共用導航欄
│   ├── admin_users.html        # 使用者管理頁面
│   ├── admin_view_post.html    # 管理員檢視全文頁面
│   └── admin.html              # 管理員主頁面
├── sources/
│   ├── admin.py                # 管理員功能模組
│   ├── post.py                 # 公開投稿/查詢模組
│   └── dba.py                  # 資料庫存取
├── config.ini                  # 設定檔案
├── README.md                   # 此專案介紹，部署教學，專案架構...等
└── requirements.txt            # Pip 必要模組
```

# 授權
本專案使用MIT License授權發布。
```
Copyright 2025 blakcat (XOT)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```