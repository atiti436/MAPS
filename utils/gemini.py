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
    辨識圖片中的店家資訊（支援單個或多個店家）

    參數:
        image_data: 圖片的 bytes 資料

    回傳:
        dict: {
            "restaurants": [
                {"name": str, "address": str},
                ...
            ],
            "count": int
        }
    """
    try:
        # 將 bytes 轉換為 PIL Image
        image = Image.open(io.BytesIO(image_data))

        # 設計 Prompt
        prompt = """
你是一個美食偵探，專門從社群媒體截圖（IG/Threads/Facebook/推薦清單）中找出店家資訊。

【任務】
從圖片中識別「所有實體店名」或「景點名稱」

【判斷規則】
- 如果圖片是單個店家（招牌、單一介紹）→ 只回傳 1 個
- 如果圖片是清單/推薦文（多個店家）→ 回傳所有店家（最多 10 個）

【重要規則】
1. 忽略：廣告、心情文案、按讚數、留言、hashtag、編號
2. 專注找：店名/招牌/Logo 上的文字
3. 地址：如果有明確地址就提取，沒有就填 "unknown"
4. 不要瞎猜：找不到店名就填 "unknown"
5. 清單格式：如果是「1. 店名A 2. 店名B」這種，每個都要提取

【回傳格式】
{
  "restaurants": [
    {"name": "店家名稱或unknown", "address": "完整地址或unknown"},
    {"name": "店家名稱或unknown", "address": "完整地址或unknown"}
  ],
  "count": 2
}

如果只有一個店家，restaurants 陣列只有一個元素。
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
        if 'restaurants' not in result:
            # 向後相容：如果是舊格式，轉換成新格式
            if 'name' in result:
                result = {
                    'restaurants': [
                        {
                            'name': result.get('name', 'unknown'),
                            'address': result.get('address', 'unknown')
                        }
                    ],
                    'count': 1
                }
            else:
                result = {
                    'restaurants': [],
                    'count': 0
                }

        # 確保 count 欄位
        if 'count' not in result:
            result['count'] = len(result.get('restaurants', []))

        # 過濾掉 name 是 unknown 的店家
        valid_restaurants = [
            r for r in result.get('restaurants', [])
            if r.get('name') != 'unknown' and r.get('name', '').strip()
        ]

        result['restaurants'] = valid_restaurants
        result['count'] = len(valid_restaurants)

        return result

    except Exception as e:
        print(f"辨識錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {
            'restaurants': [],
            'count': 0
        }
