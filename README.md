# Anicon DIVA - Anomynous Post Site
場次姬 - 匿名投稿平台

# 介紹
本專案是一套專為Cosplay愛好者們設計的匿名投稿管理系統。<br>
原意是旨在協助圈內社群蒐集、整理、查閱各類黑名單事件，同時能在需要的時候提供相關證明，保障同好交流安全、提升圈內自我保護意識。<br>
若想使用該專案到你的社團/想要建置一份屬於自己的匿名平台，可以自由Clone（複製）/ Fork 此份專案並做些修改。

# 功能
- 發布 / 查看投稿
    - 使用Connection Pool 加快連線速度
    - 使用Discord Webhook同步發布內容
- 管理員功能
    - 可管理、刪除投稿內容
    - 新增其他管理員
    - 匯入 / 匯出投稿檔案

## Prequires
- Python 3.10.X
- MySQL / MariaDB

## Deploy
- 至Terminal下輸入以下指令安裝套件包。
```
pip install -r requirement.txt
```

## Run
1. 設定以下環境變數至系統，或者創建.env檔案設定以下環境變數：

| 變數名稱 | 用途 |
|---------|------|
|WEB_SECRET_KEY|網站 Secret Key|
|ADMIN_PASSWORD|預設 Admin 帳號密碼|
|PASSWORD_HASH_SALT|密碼哈希加鹽|
|DEBUG_MODE|除錯模式|
|DISCORD_POSTED_WEBHOOK|Discord 未發布投稿 Webbook URL|
|DISCORD_VERIFIED_WEBHOOK|Discord 已審核投稿 Webbook URL|
|MYSQL_URL|MySQL 網址|
|MYSQL_PORT|MySQL 連線埠|
|MYSQL_USER|MySQL 使用者|
|MYSQL_PASSWORD|MySQL 密碼|
|MYSQL_DATABASE|MySQL 資料庫|

2. 輸入以下指令運行。
```
python main.py
```
or
```
gunicorn main:app (Only Works On Linux)
```
3. 在瀏覽器輸入`http://127.0.0.1:5000/`瀏覽網頁。

# 專案架構
```
root/
├── main.py                     # 主入口
├── envload.py                  # 讀取環境變數
├── templates/
│   ├── index.html              # 平台首頁
│   ├── header.html             # 共用頁首
│   ├── footer.html             # 共用頁尾
│   ├── login.html              # 登入頁面
│   ├── rules.html              # 發文規則
│   ├── view_post.html          # 檢視已發布投稿頁面
│   ├── create_post.html        # 創建投稿頁面
│   ├── navbar.html             # 公開頁面共用導航欄
│   ├── admin_navbar.html       # (管理員) 共用導航欄
│   ├── admin_env.html          # (管理員) 系統一覽頁面
│   ├── admin_users.html        # (管理員) 使用者管理頁面
│   ├── admin_view_post.html    # (管理員) 檢視全文頁面
│   ├── admin_verified.html     # (管理員) 檢視已發布投稿頁面
│   └── admin_index.html        # (管理員) 主頁面
├── tools/
│   ├── fake_data_gen.py        # 假資料產生器
├── static/
│   ├── theme.css               # 網站配色
├── sources/
│   ├── admin.py                # 管理員功能模組
│   ├── post.py                 # 公開投稿/查詢模組
│   ├── webhook.py              # Discord Webhook 模組
│   ├── dba.py                  # 資料庫存取模組
│   └── utils.py                # 共用變數模組
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