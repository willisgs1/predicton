from cryptography.fernet import Fernet
import os

class SecurityModule:
    def __init__(self, key_path="secret.key"):
        self.key_path = key_path
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        if os.path.exists(self.key_path):
            with open(self.key_path, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_path, "wb") as f:
                f.write(key)
            print(f"[Security] New Encryption Key generated: {self.key_path}")
            return key

    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self.cipher.encrypt(data)

    def decrypt(self, token):
        return self.cipher.decrypt(token).decode()

    def get_key_str(self):
        return self.key.decode()

if __name__ == "__main__":
    sec = SecurityModule()
    msg = "Quantum Secret"
    enc = sec.encrypt(msg)
    print(f"Encrypted: {enc}")
    print(f"Decrypted: {sec.decrypt(enc)}")
