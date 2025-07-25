# Anicon DIVA - Anomynous Post Site
場次姬 - 匿名投稿平台

# 介紹
本專案是一套專為Cosplay愛好者們設計的匿名投稿管理系統。<br>
核心宗旨在於透過經驗分享、提醒與討論，促進圈內健康互動，並幫助受害者或知情人揭露不當行為以保護自己與他人。<br>
所有內容由使用者自行張貼，本站僅提供匿名發表平台，不承擔任何使用者言論之法律責任。若經查證涉及違法或重大糾紛，站長與管理員將在符合法定程序下，提供必要資料配合法律機關調查。<br>
若想使用該專案到你的社團/建置一份屬於自己的匿名平台，可以自由 Clone（複製）/ Fork 本專案並進行修改。

# 功能
- 發布 / 查看投稿
    - 使用 Discord Webhook 同步發布內容
- 管理員功能
    - 可管理、刪除投稿內容
    - 新增其他管理員
    - 匯入 / 匯出投稿檔案

## Prequires
- Python 3.12.X
- MySQL / SQLite

## Deploy
- 至Terminal下輸入以下指令安裝套件包。
```
pip install -r requirement.txt
```

## Run
1. 可設定以下環境變數至系統，或者創建.env檔案設定以下環境變數：

| 變數名稱 | 用途 |
|---------|------|
|WEB_SECRET_KEY|網站 Secret Key|
|ADMIN_PASSWORD|預設 Admin 帳號密碼|
|PASSWORD_HASH_SALT|密碼哈希加鹽|
|DEBUG_MODE|除錯模式，若輸入True則預設使用SQLite|
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
├── templates/
│   ├── index.html              # 平台首頁
│   ├── header.html             # 共用頁首
│   ├── footer.html             # 共用頁尾
│   ├── login.html              # 登入
│   ├── rules.html              # (公開頁面) 發文規則
│   ├── view_post.html          # (公開頁面) 檢視已發布投稿
│   ├── create_post.html        # (公開頁面) 創建投稿
│   ├── navbar.html             # (公開頁面) 共用導航欄
│   ├── admin_navbar.html       # (管理員) 共用導航欄
│   ├── admin_all_posts.html    # (管理員) 全部投稿
│   ├── admin_pending.html      # (管理員) 待審核投稿
│   ├── admin_env.html          # (管理員) 系統一覽
│   ├── admin_users.html        # (管理員) 使用者管理
│   ├── admin_view_post.html    # (管理員) 檢視全文
│   └── admin_index.html        # (管理員) 主頁面
├── tools/
│   ├── fake_data_gen.py        # 假資料產生器
├── static/
│   ├── theme.css               # 網站配色
│   └── favicon.ico             # 網站icon
├── sources/
│   ├── __init__.py             
│   ├── dba
│   │   ├── __init__.py
│   │   ├── admin.py            # Database Admin 操作模組
│   │   ├── guest.py            # Database Guest 操作模組
│   │   ├── init.py             # Database 初始化模組
│   │   ├── model.py            # Database 模型
│   │   └── post.py             # Database Post 操作模組
│   ├── utils
│   │   ├── config.py           # 共用變數
│   │   └── envload.py          # 環境變數載入
│   ├── admin.py                # Web Admin 頁面功能模組
│   ├── post.py                 # Web 公開頁面功能模組
│   └── webhook.py              # Discord Webhook 模組
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