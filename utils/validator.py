def validate_result(result):
    """
    驗證辨識結果是否有效

    支援新舊兩種格式：
    - 舊格式: {name: str, address: str}
    - 新格式: {restaurants: [...], count: int}

    參數:
        result: dict - 辨識結果

    回傳:
        bool: 是否為有效結果
    """
    # 新格式：檢查是否有店家
    if 'restaurants' in result:
        return result.get('count', 0) > 0

    # 舊格式（向後相容）
    if 'name' not in result:
        return False

    name = result['name']

    # 檢查店名是否為 unknown 或空字串
    if name == 'unknown' or not name or name.strip() == '':
        return False

    # 只要有店名就算成功！
    return True
