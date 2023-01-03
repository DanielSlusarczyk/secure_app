from Crypto.Protocol.KDF import PBKDF2
from Cryptodome.Cipher import AES
from Crypto.Random import get_random_bytes
from source.dbManager import DBManager
import os, markdown, bleach, json
from base64 import b64encode, b64decode

class NoteManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.allowed_tags = json.loads(os.getenv('ALLOWED_TAGS'))
        self.allowed_protocols = json.loads(os.getenv('ALLOWED_PROTOCOLS'))

    def render(self, author, text):
        note = markdown.markdown(text)

        sanitized_note = bleach.clean(note, tags=self.allowed_tags, protocols=self.allowed_protocols)
        is_safe = (note == sanitized_note)

        self.db_manager.insert('INSERT INTO drafts (author, markdown) VALUES (?, ?)', params = (author, text))

        return sanitized_note, is_safe
    
    def save(self, user, encrypt, public, password):
        saved = False
        try:
            md = self.db_manager.one('SELECT markdown FROM drafts WHERE author = ? ORDER BY addDate DESC LIMIT 1', params = (user,))
        except:
            md = None

        if md is not None:
            md = markdown.markdown(md[0])
            tag, salt, nonce = '', '', ''

            note = bleach.clean(md, tags=self.allowed_tags, protocols=self.allowed_protocols)
            
            if encrypt:
                note, salt, nonce, tag = self.encrypt(note, password)

            isEncrypted = 1 if encrypt else 0
            isPublic = 1 if public else 0

            self.db_manager.insert('INSERT INTO notes (owner, note, isEncrypted, isPublic, tag, salt, nonce) VALUES (?, ?, ?, ?, ?, ?, ?)', params = (user, note, isEncrypted, isPublic, tag, salt, nonce))
            self.db_manager.execute('DELETE FROM drafts WHERE author = ?', params = (user,))
            saved = True

        return saved

    def is_encrypted(self, id):
        try:
            (isEncypted,) = self.db_manager.one('SELECT isEncrypted FROM notes WHERE id = ?', params = (id,))

            if isEncypted == 1:
                return True
            else:
                return False
        except:
            return False

    def is_author(self, id, alleged_author):
        try:
            (author,) = self.db_manager.one('SELECT owner FROM notes WHERE id = ?', params = (id,))
            
            isAuthor = (author == alleged_author)
            return isAuthor
        except:
            return False

    def find_by_id_encrypted(self, id, password):
        try:
            row = self.db_manager.one('SELECT note, salt, tag, nonce FROM notes WHERE id = ?', params = (id,))
            text, salt, tag, nonce = row

            note = self.decrypt(text, password, salt, nonce, tag)

            return note
        except:
            return None

    def find_by_id(self, id):
        try:
            (note,) = self.db_manager.one('SELECT note FROM notes WHERE id = ?', params = (id,))

            return note
        except:
            return None

    def find_by_author(self, author):
        notes = self.db_manager.many('SELECT id, STRFTIME("%d/%m/%Y, %H:%M", addDate) FROM notes WHERE owner = ?', params = (author,))
        return notes

    def encrypt(self, plain_text, password):
        salt = get_random_bytes(32)
        key = PBKDF2(password, salt, dkLen=32)
        cipher = AES.new(key, AES.MODE_EAX)

        text, tag = cipher.encrypt_and_digest(bytes(plain_text, 'utf-8'))

        salt = b64encode(salt).decode('utf-8')
        text = b64encode(text).decode('utf-8')
        nonce = b64encode(cipher.nonce).decode('utf-8')
        tag = b64encode(tag).decode('utf-8')

        return text, salt, nonce, tag

    def decrypt(self, text, password, salt, nonce, tag):

        salt = b64decode(salt)
        cipher_text = b64decode(text)
        nonce = b64decode(nonce)
        tag = b64decode(tag)

        private_key = PBKDF2(password, salt, dkLen=32)
        cipher = AES.new(private_key, AES.MODE_EAX, nonce=nonce)

        decrypted = cipher.decrypt_and_verify(cipher_text, tag)
        return bytes.decode(decrypted)