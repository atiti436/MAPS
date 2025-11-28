from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    StickerMessageContent
)
import requests
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, GEMINI_API_KEY
from utils.gemini import recognize_restaurant
from utils.validator import validate_result
from utils.maps import generate_maps_url

app = Flask(__name__)

# LINE Bot API 設定
print(f"=== 環境變數檢查 ===")
print(f"LINE_CHANNEL_ACCESS_TOKEN 長度: {len(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else 'None'}")
print(f"LINE_CHANNEL_ACCESS_TOKEN 前10碼: {LINE_CHANNEL_ACCESS_TOKEN[:10] if LINE_CHANNEL_ACCESS_TOKEN else 'None'}")
print(f"LINE_CHANNEL_SECRET 長度: {len(LINE_CHANNEL_SECRET) if LINE_CHANNEL_SECRET else 'None'}")
print(f"GEMINI_API_KEY 長度: {len(GEMINI_API_KEY) if GEMINI_API_KEY else 'None'}")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE Bot webhook endpoint"""
    # 取得 X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # 取得 request body
    body = request.get_data(as_text=True)
    print(f"收到 webhook 請求，body: {body[:200]}...")  # 只印前 200 字元

    # 處理 webhook
    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print(f"簽名驗證失敗: {e}")
        abort(400)
    except Exception as e:
        print(f"處理 webhook 錯誤: {e}")
        import traceback
        traceback.print_exc()

    return 'OK'

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    """處理圖片訊息"""
    print("=== 觸發圖片訊息處理器 ===")
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            # 先回「辨識中...」
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text='🔍 辨識中...')]
                )
            )

            # 下載圖片（使用 MessagingApiBlob）
            message_id = event.message.id
            print(f"開始下載圖片，message_id: {message_id}")

            # LINE Bot SDK v3 使用 MessagingApiBlob 下載圖片
            blob_api = MessagingApiBlob(api_client)
            image_data = blob_api.get_message_content(message_id)
            print(f"圖片下載完成，大小: {len(image_data)} bytes")

            # 辨識店家資訊
            print("開始辨識店家資訊...")
            result = recognize_restaurant(image_data)
            print(f"辨識結果: {result}")

            # 驗證結果
            if validate_result(result):
                # 辨識成功
                name = result['name']
                address = result.get('address', 'unknown')

                # 生成 Google Maps URL
                maps_url = generate_maps_url(name, address)

                # 建立卡片內容
                card_contents = [
                    {
                        "type": "text",
                        "text": "🏪 找到店家！",
                        "weight": "bold",
                        "size": "md",
                        "color": "#1DB446"
                    },
                    {
                        "type": "text",
                        "text": name,
                        "weight": "bold",
                        "size": "xl",
                        "margin": "md"
                    }
                ]

                # 如果有地址，才顯示地址
                if address and address != 'unknown' and address.strip():
                    card_contents.append({
                        "type": "text",
                        "text": address,
                        "size": "sm",
                        "color": "#999999",
                        "margin": "md",
                        "wrap": True
                    })
                else:
                    card_contents.append({
                        "type": "text",
                        "text": "📍 地址未提供",
                        "size": "sm",
                        "color": "#AAAAAA",
                        "margin": "md"
                    })

                # 建立 Flex Message 卡片
                flex_message_json = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": card_contents
                    },
                    "footer": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "style": "primary",
                                "color": "#1DB446",
                                "action": {
                                    "type": "uri",
                                    "label": "🗺️ 開啟地圖",
                                    "uri": maps_url
                                }
                            }
                        ]
                    }
                }

                flex_message = FlexMessage(
                    alt_text=f'{name} - {address}',
                    contents=FlexContainer.from_dict(flex_message_json)
                )

                # 推送訊息
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=event.source.user_id,
                        messages=[flex_message]
                    )
                )

            else:
                # 辨識失敗
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=event.source.user_id,
                        messages=[TextMessage(text='😅 抱歉辨識不出來')]
                    )
                )

    except Exception as e:
        print(f"處理圖片錯誤: {e}")
        try:
            with ApiClient(configuration) as api_client:
                line_bot_api = MessagingApi(api_client)
                line_bot_api.push_message(
                    PushMessageRequest(
                        to=event.source.user_id,
                        messages=[TextMessage(text='😅 抱歉辨識不出來')]
                    )
                )
        except:
            pass

@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event):
    """處理貼圖訊息"""
    print("=== 觸發貼圖訊息處理器 ===")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='貼圖很可愛！但我需要美食截圖才能幫你找店家喔 📸')]
            )
        )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
    print("=== 觸發文字訊息處理器 ===")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text='請傳截圖給我！📸')]
            )
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
