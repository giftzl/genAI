import re

def is_valid_email(email_string):
    """
    验证给定的字符串是否为有效的电子邮件地址
    
    参数:
        email_string (str): 要验证的电子邮件地址字符串
        
    返回:
        bool: True表示有效，False表示无效
        
    异常:
        TypeError: 如果输入不是字符串类型
        
    正则表达式说明:
        这个正则表达式基于RFC 5322标准简化版本，覆盖大多数常见电子邮件格式：
        - 用户名部分允许: 字母、数字、. _ % + -
        - 域名部分允许: 字母、数字、. -
        - 必须包含@符号
        - 顶级域名至少2个字符
        - 不支持国际化域名(IDN)中的非ASCII字符
        参考: https://emailregex.com/
    """
    if not isinstance(email_string, str):
        raise TypeError("输入必须是字符串类型，但收到 {}".format(type(email_string).__name__))
    
    # 健壮的电子邮件正则表达式
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # 使用fullmatch确保整个字符串匹配
    return bool(re.fullmatch(pattern, email_string))

if __name__ == "__main__":
    # 简单命令行测试
    import sys
    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"'{email}' is {'valid' if is_valid_email(email) else 'invalid'}")
    else:
        print("Usage: python email_validator.py <email>")
