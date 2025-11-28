from urllib.parse import quote

def generate_maps_url(name, address):
    """
    生成 Google Maps 搜尋連結

    參數:
        name: str - 店家名稱
        address: str - 店家地址

    回傳:
        str: Google Maps 搜尋 URL
    """
    # 組合查詢字串
    query = f"{name} {address}"

    # URL encode
    encoded_query = quote(query)

    # 生成 Google Maps 搜尋連結
    maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    return maps_url
