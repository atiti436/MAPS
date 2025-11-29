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
# Role & Objective
你是美食導航助手。從圖片 (OCR) 與貼文文字中，精準提取店家資訊，整理成 JSON 格式，以便生成 Google Maps 搜尋連結。

# Extraction Logic

## 1. Shop Name (店名 - 帳號權重策略)
**來源優先級（由清晰度決定）：**
1. **清晰的實體招牌** → 最優先
2. **社群帳號（需身份驗證）** → 無招牌時的次選
3. **貼文文字** → 最後選擇

**社群帳號提取規則（僅當無實體招牌時）：**

**身份驗證（判斷店家 vs 推薦者）：**
- ❌ 拒絕提取：帳號包含 `foodie`, `blogger`, `eats`, `life`, `diary`, `travel` 等
- ❌ 拒絕提取：貼文語氣是推薦（「推薦這家」「去吃了XXX」）
- ✅ 可提取：帳號包含 `cafe`, `official`, `restaurant`, `store` 等
- ✅ 可提取：貼文語氣是店主（「我們的店」「本店」）

**帳號語意還原（Handle Processing）：**
提取帳號後，執行以下清洗步驟：
1. 移除後綴：`_official`, `_store`, `_tw`, `.tw` 等
2. 移除年份：`2023`, `2024`, `2025` 等
3. 特殊字元轉空格：`_` 和 `.` 改為空格
4. 智能合併：`ca_fe` → `Cafe`, `hu_lu_lu` → `Hululu`
5. Title Case：首字母大寫（例如：`poffee canteen` → `Poffee Canteen`）
6. 保留數字：`no5` → `No.5`, `101` 保持原樣

**衝突處理：**
- 模糊招牌 + 清晰帳號 → 使用帳號（還原後的名稱）
- 清晰招牌 + 帳號 → 使用招牌（`name`），保留帳號（`original_handle`）
- 推薦清單 → 只提取清單中的店名，忽略推薦者帳號

**多店家清單：**
- 若圖片是推薦清單，提取所有列出的店名（最多 10 個）
- 忽略頂部推薦者帳號

## 2. Address/Location (地址資訊)
**目標：** 提供越詳細越好的地理資訊，提高 Google Maps 搜尋命中率。

**提取策略（堆疊法）：**
- 有完整地址（如：桃園市中壢區健行路123號）→ 提取完整地址
- 無完整地址 → 堆疊所有地點資訊（例如：桃園後站 健行路）
- 從貼文正文或 hashtag 提取區域/路名/地標

**語意分析：**
- 只提取「店家所在地」，排除「出發地」或「比較對象」
- 例如：「從台北來桃園吃飯」→ 只提取「桃園」
- 例如：「後站健行路上的店」→ 提取「後站 健行路」

**無地點資訊：** 填 "unknown"

## 3. Food Keywords (搜尋優化關鍵字)
**目標：** 提取最能幫助 Google Maps 找到該店家的關鍵搜尋詞。

**來源優先級：**
1. 貼文強調的招牌菜（例如：「必點肉桂捲」→ 提取「肉桂捲」）
2. 若貼文未提及，從圖片辨識食物種類（例如：圖是拿鐵 → 提取「咖啡」）

**格式策略：**
- 採用「具體招牌菜 + 廣泛類別」組合
- 最多 2-3 個關鍵字，空格分隔
- 範例：
  * 貼文「#肉桂捲超好吃」→ "肉桂捲 麵包"
  * 貼文「咖哩跟漢堡排都讚」→ "咖哩 漢堡排 洋食"
  * 圖片是咖啡杯，貼文無提及 → "咖啡"

**無食物資訊：** 填空字串 ""

# Output Format (JSON)
{
  "restaurants": [
    {
      "name": "店名（招牌文字 或 還原後的帳號名）",
      "original_handle": "原始社群帳號（可選，僅當使用帳號時提供）",
      "address": "完整地址 或 區域+路名 或 unknown"
    }
  ],
  "count": 1,
  "food_keywords": "關鍵字1 關鍵字2"
}

**欄位說明：**
- `name`: 主要顯示名稱（招牌優先，或還原後的帳號名）
- `original_handle`: 原始社群帳號（例如：no5ca_fe）- 僅當使用帳號作為店名時提供
- `address`: 地址資訊
- `food_keywords`: 食物類型關鍵字

# Examples

## Example 1: 單店家，複合地點，視覺推測關鍵字
**貼文：** "終於來朝聖！這家在桃園後站健行路上的小店，肉桂捲跟美式都超讚"
**圖片：** 招牌顯示 "Mountain"
**輸出：**
{
  "restaurants": [{"name": "Mountain", "address": "桃園後站 健行路"}],
  "count": 1,
  "food_keywords": "肉桂捲 咖啡"
}

## Example 2: IG 帳號名，錯字容忍
**貼文：** "後站健行路上的雞湯專賣店 來碗雞湯"
**圖片：** 招牌顯示 "喝碗雞湯"
**輸出：**
{
  "restaurants": [{"name": "喝碗雞湯", "address": "後站 健行路"}],
  "count": 1,
  "food_keywords": "雞湯 滷肉飯"
}

## Example 3: 社群截圖，帳號語意還原
**貼文：** "中壢車站走路約10分鐘，有甜有鹹"
**圖片：** IG 截圖，帳號名 "poffee_canteen"，咖哩飯照片，無實體招牌
**輸出：**
{
  "restaurants": [{"name": "Poffee Canteen", "original_handle": "poffee_canteen", "address": "中壢車站"}],
  "count": 1,
  "food_keywords": "咖哩 簡餐"
}

## Example 3-2: 社群截圖，帳號語意還原（巴斯克案例）
**貼文：** "柚香蜂蜜巴斯克他來了～這週的巴斯克口味..."
**圖片：** IG 截圖，帳號名 "no5ca_fe"，巴斯克蛋糕照片，無實體招牌
**輸出：**
{
  "restaurants": [{"name": "No.5 Cafe", "original_handle": "no5ca_fe", "address": "unknown"}],
  "count": 1,
  "food_keywords": "巴斯克 蛋糕 甜點"
}

## Example 4: 多店家清單
**貼文：** "精選三家！"
**圖片：** 清單顯示「1. 秋甜（中壢） 2. 日和（樹林四街） 3. Mountain（內壢）」
**輸出：**
{
  "restaurants": [
    {"name": "秋甜", "address": "中壢"},
    {"name": "日和", "address": "樹林四街"},
    {"name": "Mountain", "address": "內壢"}
  ],
  "count": 3,
  "food_keywords": "甜點 麵包 咖啡"
}

## Example 5: 無店名
**圖片：** 只有食物特寫，無招牌
**輸出：**
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
