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
你是圖片文字辨識專家，從社群媒體截圖中提取店家資訊。

【核心原則】
1. 只辨識圖片中「實際看到的文字」，不要推理、不要猜測、不要補全
2. 即使模糊、歪斜、部分遮擋，也要盡力辨識
3. 看到什麼就寫什麼：看到「日和」就寫「日和」，不要擴充成「日和麵包」

【辨識步驟】
步驟1：找出圖片上的招牌/Logo/店名文字（即使模糊）
步驟2：找出圖片上的地址文字（如果有）
步驟3：判斷單店家還是清單（多店家）

【判斷規則】
- 單店家：招牌照、店面照、單一介紹 → 回傳 1 個
- 多店家：推薦清單、多個店名並列 → 回傳所有（最多 10 個）

【提取規則】
✅ 要提取：
- 圖片上的店名/招牌文字（即使模糊、不完整）
- 圖片上的地址數字/路名（如果清晰可見）
- 貼文中的 hashtag 地址（如 #樹林四街、#桃園後站）
- 貼文中的食物類型關鍵字（從文字推測，例如：#肉桂捲 → 麵包、#拿鐵 → 咖啡）

❌ 要忽略：
- 廣告文案、心情感想
- 按讚數、留言數
- 一般性 hashtag（如 #好吃、#推薦）
- 編號（如「1.」「2.」）

【關鍵：不要過度推理】
- 圖片上看到「日和」→ 就寫「日和」（不要猜是「日和麵包店」）
- 圖片上看到「鮮芋仙」→ 就寫「鮮芋仙」（不要加地址去猜分店）
- 如果只看到模糊的部分文字 → 寫出辨識到的部分即可

【地址處理】
- 圖片有明確地址 → 提取完整地址
- 圖片無地址，但貼文有地點 hashtag（如 #樹林四街）→ 提取 hashtag 地址
- 都沒有 → 填 "unknown"

【回傳格式】
{
  "restaurants": [
    {"name": "圖片上看到的店名", "address": "地址或unknown"},
    ...
  ],
  "count": N,
  "food_keywords": "食物類型關鍵字，例如：麵包、咖啡、拉麵、火鍋（如果無法判斷則留空字串）"
}

範例：
- 貼文有 #肉桂捲 #可頌 → food_keywords: "麵包"
- 貼文有 #拿鐵 → food_keywords: "咖啡"
- 貼文無食物資訊 → food_keywords: ""

如果完全找不到店名（圖片是風景/食物特寫/無文字），回傳：
{
  "restaurants": [],
  "count": 0,
  "food_keywords": ""
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
                    'count': 1,
                    'food_keywords': ''
                }
            else:
                result = {
                    'restaurants': [],
                    'count': 0,
                    'food_keywords': ''
                }

        # 確保 count 欄位
        if 'count' not in result:
            result['count'] = len(result.get('restaurants', []))

        # 確保 food_keywords 欄位
        if 'food_keywords' not in result:
            result['food_keywords'] = ''

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
            'count': 0,
            'food_keywords': ''
        }
