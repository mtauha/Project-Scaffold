import zipfile
import io
from cryptography.fernet import Fernet, InvalidToken
import getpass


def compress_snapshot(bytes_data, out_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("snapshot", bytes_data)
    compressed = zip_buffer.getvalue()
    if out_path:
        with open(out_path + ".zip", "wb") as f:
            f.write(compressed)
    return compressed


def encrypt_snapshot(bytes_data, out_path):
    passphrase = getpass.getpass("Enter passphrase for encryption: ")
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)
    encrypted = cipher_suite.encrypt(bytes_data)
    if out_path:
        with open(out_path + ".enc", "wb") as f:
            f.write(encrypted)
    print("Encryption key (save it securely!):", key.decode())
    return encrypted
