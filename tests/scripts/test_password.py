from passlib.context import CryptContext

# 创建密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 从数据库获取的哈希密码
hashed_password = "$2b$12$QekM/moaa64d/fxOU0kH.eU4VbRLizeW/1lOQh/5hLj3QciCSnJpi"

# 测试一些常见的密码
passwords_to_test = [
    "testpassword123",
    "password",
    "123456",
    "test123",
    "test_user",
    "admin",
    "administrator"
]

print("测试密码验证:")
for password in passwords_to_test:
    if pwd_context.verify(password, hashed_password):
        print(f"密码 '{password}' 验证成功!")
        break
    else:
        print(f"密码 '{password}' 验证失败")