def validate_result(result):
    """
    驗證辨識結果是否有效

    新邏輯：只要有店名就算成功，地址是可選的

    參數:
        result: dict - 包含 name 和 address 的辨識結果

    回傳:
        bool: 是否為有效結果
    """
    # 檢查是否包含必要欄位
    if 'name' not in result:
        return False

    name = result['name']

    # 檢查店名是否為 unknown 或空字串
    if name == 'unknown' or not name or name.strip() == '':
        return False

    # 只要有店名就算成功！
    return True
