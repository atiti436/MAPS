def validate_result(result):
    """
    驗證辨識結果是否有效

    參數:
        result: dict - 包含 name 和 address 的辨識結果

    回傳:
        bool: 是否為有效結果
    """
    # 檢查是否包含必要欄位
    if 'name' not in result or 'address' not in result:
        return False

    name = result['name']
    address = result['address']

    # 檢查是否為 unknown
    if name == 'unknown' or address == 'unknown':
        return False

    # 檢查是否為空字串
    if not name or not address or name.strip() == '' or address.strip() == '':
        return False

    # 台灣地址關鍵字
    taiwan_keywords = ['市', '區', '路', '街', '巷', '號', '台北', '新北', '台中', '台南', '高雄']

    # 檢查地址是否包含台灣地址關鍵字
    has_taiwan_keyword = any(keyword in address for keyword in taiwan_keywords)

    return has_taiwan_keyword
