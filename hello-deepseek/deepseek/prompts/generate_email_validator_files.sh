#!/bin/bash

# 创建 email_validator.py 文件，包含 is_valid_email 函数
cat > email_validator.py << 'EOF'
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
EOF

# 创建 test_email_validator.py 文件，包含 TestIsValidEmail 测试类
cat > test_email_validator.py << 'EOF'
import unittest
from email_validator import is_valid_email

class TestIsValidEmail(unittest.TestCase):
    def test_valid_emails(self):
        """测试各种有效的电子邮件格式"""
        valid_emails = [
            "simple@example.com",               # 标准格式
            "firstname.lastname@example.com",   # 带点的用户名
            "user+tag@example.org",             # 带+号的别名
            "user@sub.domain.co.uk",            # 多级域名
            "user-name@domain-name.com",        # 带连字符的域名
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(is_valid_email(email), f"应该有效: {email}")

    def test_invalid_emails_format(self):
        """测试格式错误的电子邮件"""
        invalid_emails = [
            "plainaddress",                     # 缺少@和域名
            "@missingusername.com",             # 只有域名部分
            "user@.com",                       # @后直接是点
            "user@domain..com",                 # 连续的点
            "user@domain_com",                 # 域名中有下划线(非法字符)
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(is_valid_email(email), f"应该无效: {email}")

    def test_invalid_input_type(self):
        """测试非字符串输入是否抛出TypeError"""
        invalid_inputs = [
            123,                               # 整数
            ["test@example.com"],               # 列表
            None,                               # None
            {"email": "test@example.com"},      # 字典
            True                                # 布尔值
        ]
        
        for inp in invalid_inputs:
            with self.subTest(input=inp):
                with self.assertRaises(TypeError):
                    is_valid_email(inp)

    def test_empty_string(self):
        """测试空字符串"""
        self.assertFalse(is_valid_email(""))
    
    def test_emails_with_spaces(self):
        """测试包含空格的电子邮件地址"""
        emails_with_spaces = [
            " user@example.com",               # 前导空格
            "user@example.com ",               # 尾部空格
            "user name@example.com",            # 中间空格
            "user@example .com",                # 域名中空格
            " user @ example.com ",             # 多处空格
        ]
        
        for email in emails_with_spaces:
            with self.subTest(email=email):
                self.assertFalse(is_valid_email(email), f"应该无效(含空格): {email}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
EOF

# 设置文件可执行权限
chmod +x email_validator.py
chmod +x test_email_validator.py

echo "已创建以下文件:"
echo "- email_validator.py (包含 is_valid_email 函数)"
echo "- test_email_validator.py (包含 TestIsValidEmail 测试类)"