from urllib.parse import quote

def generate_maps_url(name, address, keywords='', original_handle=''):
    """
    生成 Google Maps 搜尋連結

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

    # 加入原始帳號（如果有）- 提高搜尋命中率
    if original_handle and original_handle.strip():
        query_parts.append(original_handle)

    # 加入地址（如果有）
    if address and address != 'unknown' and address.strip():
        query_parts.append(address)

    # 加入食物關鍵字（如果有）
    if keywords and keywords.strip():
        query_parts.append(keywords)

    query = ' '.join(query_parts)

    # URL encode
    encoded_query = quote(query)

    # 生成 Google Maps 搜尋連結
    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    return maps_url
