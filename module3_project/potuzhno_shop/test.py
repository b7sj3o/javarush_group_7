import base64, json

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoi.aswaswasw"
header, payload, signature = token.split('.')

def decode(part):
    return base64.urlsafe_b64decode(part + '=' * (-len(part) % 4))

print(decode(header))
print(decode(payload))