"""
Encryption utilities for sensitive data (AES-256)
"""
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.conf import settings


class AESEncryption:
    """AES-256 encryption/decryption utility"""
    
    def __init__(self):
        # Get encryption key from settings or generate one
        self.key = self._get_or_generate_key()
        self.backend = default_backend()
    
    def _get_or_generate_key(self):
        """Get encryption key from settings or generate a new one"""
        if hasattr(settings, 'ENCRYPTION_KEY'):
            key = settings.ENCRYPTION_KEY
            if isinstance(key, str):
                return key.encode('utf-8')
            return key
        
        # Generate a new key (32 bytes for AES-256)
        # In production, this should be stored securely in environment variables
        key = os.urandom(32)
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-CBC
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64 encoded encrypted string (IV + ciphertext)
        """
        if not plaintext:
            return None
        
        # Generate a random IV (Initialization Vector)
        iv = os.urandom(16)
        
        # Pad the plaintext to block size
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Return IV + ciphertext as base64
        return base64.b64encode(iv + ciphertext).decode('utf-8')
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt ciphertext using AES-256-CBC
        
        Args:
            encrypted_text: Base64 encoded encrypted string (IV + ciphertext)
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return None
        
        try:
            # Decode base64
            data = base64.b64decode(encrypted_text.encode('utf-8'))
            
            # Extract IV and ciphertext
            iv = data[:16]
            ciphertext = data[16:]
            
            # Decrypt
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=self.backend
            )
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


# Singleton instance
aes_encryption = AESEncryption()


def encrypt_biometric_hash(fingerprint_template: str) -> str:
    """
    Encrypt biometric hash using AES-256
    
    Args:
        fingerprint_template: Fingerprint template string
        
    Returns:
        Encrypted base64 string
    """
    return aes_encryption.encrypt(fingerprint_template)


def decrypt_biometric_hash(encrypted_hash: str) -> str:
    """
    Decrypt biometric hash using AES-256
    
    Args:
        encrypted_hash: Encrypted base64 string
        
    Returns:
        Decrypted fingerprint template string
    """
    return aes_encryption.decrypt(encrypted_hash)
