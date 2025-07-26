from . import discord_webhook
from flask import current_app

# 2025.7.26 Blackcat: Using Social Mode Instead webhook

class social_mode:
    PendingPost     = 1
    ApprovedPost    = 2

def send(_social_mode: social_mode, anon_id: str, nickname: str, content: str, ip: str, user_agent: str, post_time: str):
    if _social_mode == social_mode.PendingPost:
        # 待審核投稿：發文Discord
        discord_posted_url = current_app.config.get('DISCORD_POSTED_URL')
        if discord_posted_url:
            result = discord_webhook.send(discord_posted_url, 
                                          anon_id, 
                                          nickname, 
                                          content, 
                                          ip, 
                                          user_agent, 
                                          post_time)
            return result
    elif _social_mode == social_mode.ApprovedPost:
        # 審核通過投稿：發文 Discord 與 FB Post
        discord_verified_url = current_app.config.get('DISCORD_VERIFY_URL')
        if discord_verified_url:
            result = discord_webhook.send(discord_verified_url, 
                                          anon_id, 
                                          nickname, 
                                          content)
            return result
    
    return None
