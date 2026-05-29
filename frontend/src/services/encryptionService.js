/**
 * Encryption utilities for the frontend
 * Implements hybrid encryption: RSA for key exchange, AES for message encryption
 * Uses Web Crypto API (native browser crypto)
 */

export class FrontendEncryption {
  /**
   * Load public key from PEM string
   * Note: In production, use a proper crypto library like TweetNaCl.js or libsodium.js
   */
  static async loadPublicKey(pem) {
    // Extract the key content
    const pemHeader = '-----BEGIN PUBLIC KEY-----';
    const pemFooter = '-----END PUBLIC KEY-----';
    const pemContents = pem
      .substring(pemHeader.length, pem.length - pemFooter.length)
      .replace(/\s/g, '');
    const binaryString = atob(pemContents);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    return await window.crypto.subtle.importKey(
      'spki',
      bytes.buffer,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256',
      },
      false,
      ['encrypt']
    );
  }

  /**
   * Load private key from PEM string
   */
  static async loadPrivateKey(pem) {
    const pemHeader = '-----BEGIN PRIVATE KEY-----';
    const pemFooter = '-----END PRIVATE KEY-----';
    const pemContents = pem
      .substring(pemHeader.length, pem.length - pemFooter.length)
      .replace(/\s/g, '');
    const binaryString = atob(pemContents);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    return await window.crypto.subtle.importKey(
      'pkcs8',
      bytes.buffer,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256',
      },
      false,
      ['decrypt']
    );
  }

  /**
   * Generate random AES key
   */
  static async generateAESKey() {
    return await window.crypto.subtle.generateKey(
      {
        name: 'AES-GCM',
        length: 256,
      },
      true,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encrypt message with AES key
   */
  static async encryptMessageWithAES(message, aesKey) {
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    const encodedMessage = new TextEncoder().encode(message);

    const encryptedData = await window.crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv,
      },
      aesKey,
      encodedMessage
    );

    return {
      encrypted: this.arrayBufferToBase64(encryptedData),
      iv: this.arrayBufferToBase64(iv),
    };
  }

  /**
   * Decrypt message with AES key
   */
  static async decryptMessageWithAES(encryptedData, aesKey, iv) {
    const decrypted = await window.crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: this.base64ToArrayBuffer(iv),
      },
      aesKey,
      this.base64ToArrayBuffer(encryptedData)
    );

    return new TextDecoder().decode(decrypted);
  }

  /**
   * Encrypt AES key with public key
   */
  static async encryptKeyWithPublicKey(aesKey, publicKey) {
    const exportedKey = await window.crypto.subtle.exportKey('raw', aesKey);
    const encrypted = await window.crypto.subtle.encrypt(
      {
        name: 'RSA-OAEP',
      },
      publicKey,
      exportedKey
    );

    return this.arrayBufferToBase64(encrypted);
  }

  /**
   * Decrypt AES key with private key
   */
  static async decryptKeyWithPrivateKey(encryptedKey, privateKey) {
    const decrypted = await window.crypto.subtle.decrypt(
      {
        name: 'RSA-OAEP',
      },
      privateKey,
      this.base64ToArrayBuffer(encryptedKey)
    );

    return await window.crypto.subtle.importKey(
      'raw',
      decrypted,
      {
        name: 'AES-GCM',
      },
      true,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Full encryption: Generate AES key, encrypt message, encrypt key with public key
   */
  static async encryptMessage(message, recipientPublicKey) {
    // Generate AES key
    const aesKey = await this.generateAESKey();

    // Encrypt message with AES
    const { encrypted, iv } = await this.encryptMessageWithAES(message, aesKey);

    // Encrypt AES key with recipient's public key
    const encryptedKey = await this.encryptKeyWithPublicKey(aesKey, recipientPublicKey);

    return {
      encrypted_message: encrypted,
      encrypted_key: encryptedKey,
      iv: iv,
    };
  }

  /**
   * Full decryption: Decrypt AES key with private key, then decrypt message
   */
  static async decryptMessage(encryptedData, recipientPrivateKey) {
    // Decrypt AES key with private key
    const aesKey = await this.decryptKeyWithPrivateKey(
      encryptedData.encrypted_key,
      recipientPrivateKey
    );

    // Decrypt message with AES key
    const message = await this.decryptMessageWithAES(
      encryptedData.encrypted_message,
      aesKey,
      encryptedData.iv
    );

    return message;
  }

  /**
   * Utility: Convert ArrayBuffer to Base64
   */
  static arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Utility: Convert Base64 to ArrayBuffer
   */
  static base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }
}
