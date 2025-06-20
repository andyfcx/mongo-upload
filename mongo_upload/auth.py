import os
import json
import secrets
from pathlib import Path
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

KEY_DIR = Path.home() / ".mongo_upload"
PUB_KEY_FILE = KEY_DIR / "public.pem"
PRI_KEY_FILE = KEY_DIR / "private.pem"
CRED_FILE = KEY_DIR / "credentials.enc"

def generate_keys():
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(PRI_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    with open(PUB_KEY_FILE, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def encrypt_and_store_credentials(data: dict):
    serialized = json.dumps(data).encode("utf-8")

    # Generate AES key and IV
    aes_key = secrets.token_bytes(32)  # 256-bit AES key
    iv = secrets.token_bytes(16)

    # Encrypt data using AES
    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(serialized) + encryptor.finalize()

    # Encrypt AES key using RSA public key
    with open(PUB_KEY_FILE, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())
    encrypted_key = pub_key.encrypt(
        aes_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    # Save to disk (Base64-encoded JSON)
    payload = {
        "encrypted_key": b64encode(encrypted_key).decode(),
        "iv": b64encode(iv).decode(),
        "ciphertext": b64encode(ciphertext).decode()
    }
    with open(CRED_FILE, "w") as f:
        json.dump(payload, f)

def load_credentials() -> dict | None:
    if not CRED_FILE.exists() or not PRI_KEY_FILE.exists():
        return None

    with open(CRED_FILE, "r") as f:
        payload = json.load(f)

    encrypted_key = b64decode(payload["encrypted_key"])
    iv = b64decode(payload["iv"])
    ciphertext = b64decode(payload["ciphertext"])

    with open(PRI_KEY_FILE, "rb") as f:
        pri_key = serialization.load_pem_private_key(f.read(), password=None)
    aes_key = pri_key.decrypt(
        encrypted_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )

    cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(ciphertext) + decryptor.finalize()

    return json.loads(decrypted.decode("utf-8"))
