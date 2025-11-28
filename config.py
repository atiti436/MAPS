import os
from dotenv import load_dotenv

# 載入環境變數（本地開發用，Zeabur 會直接提供系統環境變數）
load_dotenv()

# 匯出環境變數
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# 確認必要的環境變數
if not LINE_CHANNEL_SECRET:
    raise ValueError("❌ LINE_CHANNEL_SECRET 環境變數未設定！")
if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("❌ LINE_CHANNEL_ACCESS_TOKEN 環境變數未設定！")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY 環境變數未設定！")
