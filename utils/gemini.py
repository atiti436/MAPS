import google.generativeai as genai
import json
import re
from config import GEMINI_API_KEY
from PIL import Image
import io

# 初始化 Gemini 2.5 Pro 模型
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro')

def recognize_restaurant(image_data):
    """
    辨識圖片中的店家資訊

    參數:
        image_data: 圖片的 bytes 資料

    回傳:
        dict: {name: str, address: str, found: bool}
    """
    try:
        # 將 bytes 轉換為 PIL Image
        image = Image.open(io.BytesIO(image_data))

        # 設計 Prompt
        prompt = """
你是一個美食偵探，專門從社群媒體截圖（IG/Threads/Facebook）中找出店家資訊。

【任務】
從圖片中識別「實體店名」或「景點名稱」

【重要規則】
1. 忽略：廣告、心情文案、按讚數、留言、hashtag
2. 專注找：店名/招牌/Logo 上的文字
3. 地址：如果有明確地址就提取，沒有就填 "unknown"
4. 不要瞎猜：找不到店名就填 "unknown"

【回傳格式】
{
  "name": "店家名稱或unknown",
  "address": "完整地址或unknown",
  "found": true
}
"""

        # 呼叫 Gemini API
        response = model.generate_content([prompt, image])

        # 解析回應
        response_text = response.text.strip()

        # 清理 markdown 標記（可能包含 ```json 或 ```）
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'^```\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)
        response_text = response_text.strip()

        # 解析 JSON
        result = json.loads(response_text)

        # 確保包含必要的欄位
        if 'name' not in result:
            result['name'] = 'unknown'
        if 'address' not in result:
            result['address'] = 'unknown'
        if 'found' not in result:
            result['found'] = False

        return result

    except Exception as e:
        print(f"辨識錯誤: {e}")
        return {
            'name': 'unknown',
            'address': 'unknown',
            'found': False
        }
