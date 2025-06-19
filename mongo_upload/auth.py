import os
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

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
    with open(PUB_KEY_FILE, "rb") as f:
        pub_key = serialization.load_pem_public_key(f.read())
    encrypted = pub_key.encrypt(
        serialized,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    with open(CRED_FILE, "wb") as f:
        f.write(encrypted)

def load_credentials() -> dict | None:
    if not CRED_FILE.exists() or not PRI_KEY_FILE.exists():
        return None
    with open(PRI_KEY_FILE, "rb") as f:
        pri_key = serialization.load_pem_private_key(f.read(), password=None)
    with open(CRED_FILE, "rb") as f:
        encrypted = f.read()
    decrypted = pri_key.decrypt(
        encrypted,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )
    return json.loads(decrypted.decode("utf-8"))
