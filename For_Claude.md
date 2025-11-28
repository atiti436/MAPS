# LINE Bot 美食辨識專案 - Claude 交接文檔

## 📋 專案概述

**專案名稱：** Restaurant Recognition LINE Bot
**目的：** 辨識美食截圖中的店家資訊，自動生成 Google Maps 連結
**用戶：** @atiti436
**Repository：** https://github.com/atiti436/MAPS
**部署平台：** Zeabur (免費方案)

---

## 🎯 核心功能

### 主要流程
```
用戶傳美食截圖（IG/Threads/FB/推薦清單）
    ↓
LINE Bot 接收
    ↓
Gemini 2.5 Pro 視覺 AI 辨識
    ↓
提取店名 + 地址（可選）
    ↓
生成 Google Maps 連結
    ↓
Flex Message 卡片回傳
```

### 支援功能
- ✅ 單店家辨識：回傳單張卡片
- ✅ 多店家辨識：回傳 Carousel 輪播卡片（最多 10 個）
- ✅ 地址可選：只有店名也能辨識
- ✅ 貼圖友善回應
- ✅ 文字訊息提示

---

## 🏗️ 技術架構

### 核心技術棧
```
Python 3.x
├── Flask 3.1.0 (Web Framework)
├── Gunicorn 21.2.0 (Production WSGI Server)
├── LINE Bot SDK 3.12.0 (v3 API)
├── Google Generative AI 0.8.3 (Gemini 2.5 Pro)
├── Pillow 11.0.0 (圖片處理)
└── python-dotenv 1.0.0 (環境變數)
```

### 專案結構
```
MAPS_FOOD/
├── .env                    # 環境變數（不上傳 GitHub）
├── .gitignore             # Git 忽略規則
├── requirements.txt       # Python 套件清單
├── zbpack.json           # Zeabur 部署設定
├── config.py             # 環境變數載入
├── app.py                # LINE Bot 主程式
├── For_Claude.md         # 本文檔（交接用）
└── utils/
    ├── __init__.py       # 工具模組
    ├── gemini.py         # Gemini AI 辨識邏輯
    ├── validator.py      # 結果驗證
    └── maps.py           # Google Maps URL 生成
```

### 環境變數（Zeabur）
```
LINE_CHANNEL_SECRET=32碼
LINE_CHANNEL_ACCESS_TOKEN=170+碼
GEMINI_API_KEY=39碼
```

---

## 📈 版本演進史

### V1：初始版本（基礎架構）
**commit:** `5e0cba1`
- 建立完整專案結構
- LINE Bot 基礎功能
- Gemini API 整合
- ❌ 問題：模型名稱錯誤（gemini-2.5-pro 不存在）

### V2：修正模型名稱
**commit:** `3343a49`
- 改用 `gemini-1.5-flash`（當時以為 2.5 不存在）
- ❌ 問題：後來發現 2.5 確實存在，但 SDK API 改了

### V3：LINE Bot SDK v3 遷移
**commit:** `98c1252`
- 修正 `LineBotSdkDeprecatedIn30` 警告
- 改用 `linebot.v3.messaging` API
- 更新 Flex Message 格式

### V4：修正圖片下載 API
**commit:** `3c462f0`
- 使用 `MessagingApiBlob` 下載圖片（v3 正確用法）
- 恢復 `gemini-2.5-pro` 模型（用戶確認存在）
- ✅ 解決 401 Unauthorized 錯誤

### V5：放寬驗證邏輯
**commit:** `09656c6`
- 改進提示詞：專注社群媒體截圖，忽略雜訊
- 驗證邏輯：只要店名就 OK，地址改為可選
- Google Maps URL：沒地址時只搜店名
- Flex 卡片：沒地址顯示「📍 地址未提供」

### V6：生產環境優化
**commit:** `9f1fa56`
- 加上 Gunicorn 生產級 WSGI server
- 設定：2 workers, 120s timeout（Gemini 需要時間）
- 加上貼圖友善回應
- ✅ 消除 Flask development server 警告

### V7：多店家辨識（最終版）
**commit:** `3cbfee9` ⭐ **目前版本**
- Gemini 智能判斷單/多店家
- 支援推薦清單截圖（最多 10 家）
- Carousel 卡片：滑動瀏覽，每個店獨立「開啟地圖」
- 向後相容：單店家照常運作

---

## 💡 重要決策記錄

### 決策 1：只做截圖辨識，不做連結解析
**討論點：** 用戶想支援 Threads/IG 連結直接解析

**決定：** ❌ 不做

**理由：**
- 每個平台 API 不同（IG/Threads/小紅書/Twitter...）
- 反爬蟲限制嚴格，隨時可能失效
- 維護成本爆炸（平台改版就壞）
- **截圖是完美的通用解：**
  - Gemini 視覺 AI 什麼都看得懂
  - 所有平台通用
  - 穩定可靠
  - 用戶習慣（本來就會截圖分享）

### 決策 2：地址改為可選
**討論點：** 很多社群貼文只有店名，沒完整地址

**決定：** ✅ 只要店名就通過驗證

**理由：**
- 實際使用情境：「秋甜」這種只有店名的貼文很常見
- Google Maps 搜店名通常找得到
- 提高辨識成功率

### 決策 3：多店家用 Carousel，不用多點路線或 My Maps
**討論點：** 如何處理「推薦 10 家店」的清單

**考慮過的方案：**
- A. 多點 Google Maps 路線 → ❌ 用戶不是要馬上去，只是想收藏
- B. Google My Maps 匯入 → ❌ 要下載檔案、開網頁，3 步驟太麻煩
- C. 文字清單 → ❌ 沒有跟 Google Maps 整合

**最終決定：** ✅ Carousel 卡片

**理由：**
- 用戶能自己選要存哪幾家（10 家只想去 3 家）
- 視覺化呈現，滑動瀏覽
- 每個店獨立「開啟地圖」按鈕
- 符合真實使用情境

---

## 🤔 用戶的突發奇想（討論過但未實作）

### 想法 1：Threads/IG 連結解析
**狀態：** 已討論，決定不做
**原因：** 見「決策 1」

**WebFetch 測試結果：**
- 能抓到部分內容（如「岸本食堂」）
- 但抓不到完整 bio、結構化資料
- 有登入牆、反爬蟲限制
- 投資報酬率低

### 想法 2：一鍵批次存到 Google Maps
**狀態：** 已討論，用 Carousel 替代

**技術限制：**
- Google 沒有開放「直接加入已儲存地點」的 API
- 用戶還是要手動點「儲存」

**現行方案（Carousel）：**
- 雖然要點多次，但能自選
- 符合實際需求（不是全部都想存）

### 想法 3：從帳號 bio 抓地址
**狀態：** 已測試，效果不佳

**問題：**
- WebFetch 抓不到完整 bio
- Threads 有登入牆
- 需要 Instagram Graph API（要申請權限）
- 可行性 < 30%

---

## 🐛 已知問題與解決方案

### 問題 1：Zeabur 部署卡在 "Pulling image"
**症狀：** 部署超過 10 分鐘，卡在下載 Docker 映像檔

**原因：** Zeabur registry 網路問題（基礎設施層面）

**解決方法：**
1. 取消部署，重新 Redeploy
2. 換時間部署（避開高峰期）
3. 等待（通常 15-30 分鐘會好）

**非代碼問題！** 程式沒問題，是 Zeabur 那邊的網路問題。

### 問題 2：Flask Development Server 警告
**症狀：** `WARNING: This is a development server...`

**解決：** ✅ 已修正（V6）
- 改用 Gunicorn 生產級伺服器
- 設定 2 workers, 120s timeout

### 問題 3：LINE Bot SDK v3 Deprecated 警告
**症狀：** `LineBotSdkDeprecatedIn30`

**解決：** ✅ 已修正（V3）
- 遷移到 `linebot.v3` API
- 使用 `MessagingApi` 和 `MessagingApiBlob`

---

## 📝 Gemini 提示詞（核心邏輯）

```python
# utils/gemini.py: L33-60

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
    {"name": "店家名稱", "address": "完整地址或unknown"},
    ...
  ],
  "count": N
}
```

**設計理念：**
- 忽略社群媒體雜訊（廣告、文案、按讚數）
- 智能判斷單/多店家
- 地址可選（符合實際貼文內容）
- 結構化輸出（JSON）

---

## 🔧 常見操作

### 本地測試（如果需要）
```bash
# 1. 設定環境變數
# 編輯 .env，填入三個 API keys

# 2. 安裝套件
pip install -r requirements.txt

# 3. 運行（開發模式）
python app.py

# 3. 運行（生產模式）
gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app
```

### 推送更新到 Zeabur
```bash
git add .
git commit -m "描述"
git push

# Zeabur 會自動偵測並重新部署
# 等 2-3 分鐘即可
```

### 查看 Zeabur Logs
```
Zeabur 專案頁面 → Logs
```

**重點 Debug 資訊：**
```
=== 環境變數檢查 ===
LINE_CHANNEL_ACCESS_TOKEN 長度: 172
GEMINI_API_KEY 長度: 39

=== 觸發圖片訊息處理器 ===
開始下載圖片，message_id: XXX
圖片下載完成，大小: XXX bytes
辨識結果: {...}
辨識到 N 個店家
```

---

## 🚀 潛在改進方向（未來可做）

### 優先度：高
- [ ] **辨識歷史記錄**
  - 用戶可查看之前辨識過的店家
  - 需要資料庫（SQLite 或 Zeabur KV）

- [ ] **收藏清單功能**
  - 用戶可建立「想去清單」「去過清單」
  - 直接在 Bot 內管理

### 優先度：中
- [ ] **圖片辨識優化**
  - 處理模糊、角度歪、手寫字
  - 可能需要圖片預處理

- [ ] **多語言支援**
  - 日文、英文店名
  - 目前主要針對台灣繁中

### 優先度：低
- [ ] **評分/評論整合**
  - 抓取 Google Maps 評分
  - 需要 Google Places API（付費）

- [ ] **推薦系統**
  - 根據用戶喜好推薦
  - 需要 ML/推薦算法

---

## ⚠️ 重要提醒

### 給下一個 Claude

1. **不要做連結解析！**
   - 已討論過，投資報酬率極低
   - 截圖辨識是完美解

2. **Gemini 模型名稱：`gemini-2.5-pro`**
   - 這是正確的！不要改成 1.5
   - 用戶確認過 Google 官方有這個模型

3. **環境變數在 Zeabur**
   - 不用修改 `.env`（本地開發用）
   - 直接在 Zeabur 後台設定

4. **LINE Bot SDK 用 v3 API**
   - `linebot.v3.messaging.MessagingApi`
   - `linebot.v3.messaging.MessagingApiBlob` （下載圖片）

5. **Zeabur 部署問題通常是網路**
   - 不是代碼問題
   - 重新 Redeploy 或換時間試

6. **用戶需求：簡單、直覺**
   - 不要過度設計
   - 專注核心功能：截圖 → 辨識 → 地圖

---

## 📞 聯絡資訊

**GitHub:** https://github.com/atiti436/MAPS
**Zeabur:** (用戶的 Zeabur 專案)
**LINE Bot:** @懶惰Maps Admin

---

## 📚 參考資源

- [LINE Bot SDK v3 文檔](https://github.com/line/line-bot-sdk-python)
- [Gemini API 文檔](https://ai.google.dev/docs)
- [Zeabur 文檔](https://zeabur.com/docs)
- [Flex Message Simulator](https://developers.line.biz/flex-simulator/)

---

**最後更新：** 2025-11-28
**當前版本：** V7 (commit: 3cbfee9)
**狀態：** ✅ 生產環境運行中

---

_交接完成！祝下一位 Claude 接手順利！_ 🚀
