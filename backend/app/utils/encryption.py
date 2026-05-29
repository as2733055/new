"""
End-to-end encryption utilities for messages
Implements hybrid encryption: RSA for key exchange, AES for message encryption
"""

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import json
from datetime import datetime


class EncryptionManager:
    """Manages encryption and decryption of messages"""
    
    def __init__(self):
        self.backend = default_backend()
    
    @staticmethod
    def generate_key_pair():
        """Generate RSA key pair for user"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        # Serialize keys to PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')
    
    @staticmethod
    def encrypt_message(message: str, recipient_public_key: str) -> dict:
        """
        Encrypt message for recipient
        1. Generate random AES key
        2. Encrypt message with AES
        3. Encrypt AES key with recipient's public key
        4. Return both encrypted message and key
        """
        # Generate random AES key and IV
        aes_key = os.urandom(32)  # 256-bit key
        iv = os.urandom(16)  # 128-bit IV
        
        # Encrypt message with AES-256-CBC
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        padded_message = EncryptionManager._add_padding(message.encode())
        encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
        
        # Encrypt AES key with recipient's public key
        public_key = serialization.load_pem_public_key(
            recipient_public_key.encode(),
            backend=default_backend()
        )
        
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return {
            "encrypted_message": base64.b64encode(encrypted_message).decode(),
            "encrypted_key": base64.b64encode(encrypted_key).decode(),
            "iv": base64.b64encode(iv).decode()
        }
    
    @staticmethod
    def decrypt_message(encrypted_data: dict, private_key: str) -> str:
        """
        Decrypt message using private key
        1. Decrypt AES key with private key
        2. Decrypt message with AES key
        3. Return decrypted message
        """
        try:
            # Load private key
            priv_key = serialization.load_pem_private_key(
                private_key.encode(),
                password=None,
                backend=default_backend()
            )
            
            # Decode from base64
            encrypted_key = base64.b64decode(encrypted_data["encrypted_key"])
            encrypted_message = base64.b64decode(encrypted_data["encrypted_message"])
            iv = base64.b64decode(encrypted_data["iv"])
            
            # Decrypt AES key with private key
            aes_key = priv_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt message with AES key
            cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
            
            # Remove PKCS7 padding
            message = EncryptionManager._remove_padding(padded_message)
            return message.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    @staticmethod
    def _add_padding(data: bytes) -> bytes:
        """Add PKCS7 padding to data"""
        padding_length = 16 - (len(data) % 16)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    @staticmethod
    def _remove_padding(data: bytes) -> bytes:
        """Remove PKCS7 padding from data"""
        padding_length = data[-1]
        return data[:-padding_length]


class MessageEncryption:
    """High-level message encryption API"""
    
    @staticmethod
    def encrypt_for_user(message: str, recipient_public_key: str) -> str:
        """Encrypt message and return JSON string"""
        encrypted_data = EncryptionManager.encrypt_message(message, recipient_public_key)
        return json.dumps(encrypted_data)
    
    @staticmethod
    def decrypt_user_message(encrypted_json: str, recipient_private_key: str) -> str:
        """Decrypt message from JSON string"""
        encrypted_data = json.loads(encrypted_json)
        return EncryptionManager.decrypt_message(encrypted_data, recipient_private_key)
