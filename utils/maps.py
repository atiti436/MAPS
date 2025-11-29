from urllib.parse import quote
import re

# 菜市場名清單（店名太普通時才需要加關鍵字）
GENERIC_NAMES = [
    '麵包店', '咖啡廳', '咖啡店', '小吃店', '早餐店',
    '麵店', '火鍋店', '便當店', '餐廳', '飲料店',
    '茶飲', '手搖', '烘焙坊', '甜點店', '蛋糕店'
]

# 台灣常見行政區（用於提取）
TAIWAN_AREAS = [
    '中壢', '內壢', '平鎮', '桃園', '龜山', '八德', '蘆竹', '大園', '楊梅', '新屋', '觀音', '龍潭',
    '台北', '信義', '大安', '中正', '松山', '萬華', '大同', '中山', '文山', '南港', '內湖', '士林', '北投',
    '新北', '板橋', '新莊', '三重', '永和', '中和', '土城', '樹林', '鶯歌', '三峽', '淡水', '汐止',
    '台中', '北區', '西區', '南區', '東區', '中區', '西屯', '南屯', '北屯', '豐原', '大里', '太平',
    '台南', '東區', '南區', '北區', '中西區', '安平', '安南', '永康', '新營', '佳里',
    '高雄', '前金', '新興', '苓雅', '鹽埕', '鼓山', '前鎮', '三民', '左營', '楠梓', '小港'
]

def extract_area(address):
    """
    從地址中提取行政區

    參數:
        address: str - 地址字串

    回傳:
        str - 提取到的行政區，若無則回傳空字串
    """
    if not address or address == 'unknown':
        return ''

    # 檢查是否包含行政區關鍵字
    for area in TAIWAN_AREAS:
        if area in address:
            return area

    return ''

def is_generic_name(name):
    """
    判斷店名是否為菜市場名（太普通）

    參數:
        name: str - 店名

    回傳:
        bool - 是否為菜市場名
    """
    if not name:
        return False

    # 檢查是否包含菜市場關鍵字
    for generic in GENERIC_NAMES:
        if generic in name:
            return True

    # 店名太短（少於 3 個字）也視為普通
    if len(name) < 3:
        return True

    return False

def generate_maps_url(name, address, keywords='', original_handle=''):
    """
    生成 Google Maps 搜尋連結（Golden Query 優化）

    策略：
    - 優先組合：店名 + original_handle + 行政區
    - 只有店名很菜市場才加 keywords
    - 提高 Google Maps 直接彈出店家頁面的機率

    參數:
        name: str - 店家名稱（還原後的名稱或招牌文字）
        address: str - 店家地址（可為 "unknown"）
        keywords: str - 食物類型關鍵字（可選，例如：麵包、咖啡）
        original_handle: str - 原始社群帳號（可選，例如：no5ca_fe）

    回傳:
        str: Google Maps 搜尋 URL
    """
    # 組合查詢字串
    query_parts = [name]

    # 加入原始帳號（如果有）- 帳號是全世界唯一的，大幅提升信心度
    if original_handle and original_handle.strip():
        query_parts.append(original_handle)

    # 提取行政區（而非完整地址）- 大範圍定位，容錯率高
    area = extract_area(address)
    if area:
        query_parts.append(area)
    elif address and address != 'unknown' and address.strip():
        # 如果提取不到行政區，就用原始地址（但可能降低信心度）
        query_parts.append(address)

    # 只有店名很菜市場才加關鍵字（避免干擾）
    if is_generic_name(name) and keywords and keywords.strip():
        # 只取第一個關鍵字（避免太多雜訊）
        first_keyword = keywords.split()[0] if keywords else ''
        if first_keyword:
            query_parts.append(first_keyword)

    query = ' '.join(query_parts)

    # URL encode
    encoded_query = quote(query)

    # 生成 Google Maps 搜尋連結
    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    return maps_url
