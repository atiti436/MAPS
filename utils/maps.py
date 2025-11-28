from urllib.parse import quote

def generate_maps_url(name, address):
    """
    生成 Google Maps 搜尋連結

    參數:
        name: str - 店家名稱
        address: str - 店家地址（可為 "unknown"）

    回傳:
        str: Google Maps 搜尋 URL
    """
    # 組合查詢字串（如果沒有地址，就只搜尋店名）
    if address and address != 'unknown' and address.strip():
        query = f"{name} {address}"
    else:
        query = name

    # URL encode
    encoded_query = quote(query)

    # 生成 Google Maps 搜尋連結
    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    return maps_url
