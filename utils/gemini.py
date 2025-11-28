import google.generativeai as genai
import json
import re
from config import GEMINI_API_KEY
from PIL import Image
import io

# 初始化 Gemini 1.5 Flash 模型（快速且便宜）
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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
你是圖片內容分析專家，專門從圖片中提取店家資訊。

【任務】從圖片中找出「店家名稱」和「地址」

【判斷邏輯】
店家名稱：最大、最顯眼的文字，可能是 Logo、招牌
地址：包含「市、區、路、街、巷、號」的完整地址

【重要規則】
1. 找不到就填 "unknown"，不要瞎猜
2. 必須回傳有效的 JSON

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
