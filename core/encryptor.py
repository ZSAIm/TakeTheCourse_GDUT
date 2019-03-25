
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES

def aes_cipher(key, aes_str):
    aes = AES.new(key.encode('utf-8'), AES.MODE_ECB)

    pad_pkcs7 = pad(aes_str.encode('utf-8'), AES.block_size, style='pkcs7')
    encrypt_aes = aes.encrypt(pad_pkcs7)

    return encrypt_aes.hex()


