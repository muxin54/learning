"""
第21课 演示 —— JWT 原理彻底拆解
"""
import jwt
import base64
import json

SECRET_KEY = "my-secret"
ALGORITHM = "HS256"

# ============================================================
# 第一步：生成 JWT
# ============================================================
payload = {"sub": "1", "username": "zhangsan"}

token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
print("生成的 JWT 令牌：")
print(token)
print()

# ============================================================
# 第二步：拆开看三部分
# ============================================================
parts = token.split(".")
header_b64, payload_b64, signature_b64 = parts

print("三部分：")
print(f"  头部 (Header):   {header_b64}")
print(f"  数据 (Payload):  {payload_b64}")
print(f"  签名 (Signature): {signature_b64}")
print()

# 解码 Base64 看里面的内容（这部分任何人都能解码！）
def decode_base64(b64_str):
    # JWT 的 Base64 需要补齐位数
    padding = 4 - len(b64_str) % 4
    if padding != 4:
        b64_str += "=" * padding
    return json.loads(base64.urlsafe_b64decode(b64_str))

print("解码后的内容：")
print(f"  Header:  {decode_base64(header_b64)}")
print(f"  Payload: {decode_base64(payload_b64)}")
print()

# ============================================================
# 第三步：验证
# ============================================================
print("验证过程：")
print(f"  ① 拿到 token")
print(f"  ② 把 Header + Payload 用同一个密钥重新算签名")
print(f"  ③ 比对两个签名是否一样")
print(f"  ④ 一样 → 通过；不一样 → 伪造的，拒绝")

# 验证通过
decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
print(f"  验证结果: ✅ 通过 → {decoded}")

# 验证失败（密钥不对）
try:
    jwt.decode(token, "wrong-secret", algorithms=[ALGORITHM])
except jwt.InvalidSignatureError:
    print(f"  篡改测试: ✅ 检测到伪造 → 拒绝！")

print()
print("=" * 60)
print("🔑 核心理解：")
print("  Payload 里的数据任何人都能看到（Base64 不是加密！）")
print("  所以绝对不能放密码、身份证号等敏感信息")
print("  签名保证的是：数据没被篡改过，不是"数据加密了"")
print("=" * 60)
