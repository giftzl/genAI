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
