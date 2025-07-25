import requests

# 2025.6.28 Blackcat: Fix Some Post Not Displaying Issue
# 2025.7.26 Blackcat: Using Social Mode Instead webhook

def send(webhook_url: str, anon_id: str, nickname: str, content: str, ip: str, user_agent: str, post_time: str):
    """
    發送訊息到 Discord Webhook (Embed格式)。
    :param webhook_url: Discord Webhook 的 URL
    :param anon_id: 匿名ID
    :param ip: 發布者的 IP 地址
    :param user_agent: 發布者的 User-Agent
    :param content: 要發送的訊息內容
    :param post_time: 發布時間 (必須由外部傳入)
    """
    embed = {
        "title": f"新的匿名投稿",
        "color": 0x7289DA,  # Discord blurple
        "footer": {"text": f"發布時間：{post_time}"},
        "fields": [
            {
                "name": "投稿ID",
                "value": f"{anon_id}",
                "inline": True
            },
            {
                "name": "內容",
                "value": f"{content}"
            }
        ]
    }
    
    if (nickname is not None):
        embed["fields"].append({
                "name": "暱稱",
                "value": f"{nickname}",
                "inline": True
            })

    if (ip is not None):
        embed["fields"].append({
                "name": "IP 地址",
                "value": f"{ip}",
                "inline": True
            })

    if (user_agent is not None):
        embed["fields"].append({
                "name": "User-Agent",
                "value": f"{user_agent}",
                "inline": True
            })

    data = {
        "username": "場次姬 Anicon DIVA",
        "embeds": [embed]
    }

    response = requests.post(webhook_url, json=data)
    response.raise_for_status()
    return response