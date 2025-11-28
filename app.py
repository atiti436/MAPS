from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)
import requests
from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN
from utils.gemini import recognize_restaurant
from utils.validator import validate_result
from utils.maps import generate_maps_url

app = Flask(__name__)

# LINE Bot API 設定
configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE Bot webhook endpoint"""
    # 取得 X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # 取得 request body
    body = request.get_data(as_text=True)

    # 處理 webhook
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=ImageMessageContent)
def handle_image_message(event):
    """處理圖片訊息"""
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

            # 下載圖片
            message_id = event.message.id
            message_content = line_bot_api.get_message_content(message_id)
            image_data = message_content

            # 辨識店家資訊
            result = recognize_restaurant(image_data)

            # 驗證結果
            if validate_result(result):
                # 辨識成功
                name = result['name']
                address = result['address']

                # 生成 Google Maps URL
                maps_url = generate_maps_url(name, address)

                # 建立 Flex Message 卡片
                flex_message_json = {
                    "type": "bubble",
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
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
                            },
                            {
                                "type": "text",
                                "text": address,
                                "size": "sm",
                                "color": "#999999",
                                "margin": "md",
                                "wrap": True
                            }
                        ]
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

@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """處理文字訊息"""
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
