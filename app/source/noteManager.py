from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from source.dbManager import DBManager
import os, markdown, bleach, json, re
from base64 import b64encode, b64decode

class NoteManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.allowed_tags = json.loads(os.getenv('ALLOWED_TAGS'))
        self.allowed_attr = json.loads(os.getenv('ALLOWED_ATTR'))
        self.allowed_protocols = json.loads(os.getenv('ALLOWED_PROTOCOLS'))
        self.allowed_user_html = True if os.getenv('ALLOWED_USER_HTML') == "True" else False

    def render(self, author, text):

        sanitized_note, is_safe = self.sanitized_markdown(text)

        self.db_manager.insert('INSERT INTO drafts (author, markdown) VALUES (?, ?)', params = (author, text))

        return sanitized_note, is_safe
    
    def save(self, user, public):
        saved = False

        md = self.db_manager.one('SELECT markdown FROM drafts WHERE author = ? ORDER BY addDate DESC LIMIT 1', params = (user,))

        if md is not None:

            note = self.sanitized_markdown(md[0])
            
            isPublic = 1 if public else 0

            self.db_manager.insert('INSERT INTO notes (owner, note, isEncrypted, isPublic) VALUES (?, ?, ?, ?)', params = (user, note, 0, isPublic))
            self.db_manager.execute('DELETE FROM drafts WHERE author = ?', params = (user,))
            saved = True

        return saved

    def lock(self, user, password):
        saved = False

        md = self.db_manager.one('SELECT markdown FROM drafts WHERE author = ? ORDER BY addDate DESC LIMIT 1', params = (user,))

        if md is not None:
            tag, salt, nonce = '', '', ''
            note = self.sanitized_markdown(md[0])
            
            note, salt, nonce, tag = self.encrypt(note, password)

            self.db_manager.insert('INSERT INTO notes (owner, note, isEncrypted, isPublic, tag, salt, nonce) VALUES (?, ?, ?, ?, ?, ?, ?)', params = (user, note, 1, 0, tag, salt, nonce))
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
    
    def is_public(self, id):
        try:
            (state,) = self.db_manager.one('SELECT isPublic FROM notes WHERE id = ?', params = (id,))

            is_public = (state == 1)
            return is_public
        except:
            return False


    def find_by_id_encrypted(self, id, password):
        try:
            text, salt, tag, nonce = self.db_manager.one('SELECT note, salt, tag, nonce FROM notes WHERE id = ?', params = (id,))

            note = self.decrypt(text, password, salt, nonce, tag)

            return note
        except:
            return None

    def find_by_id(self, id):
        try: 
            (note,) = self.db_manager.one('SELECT note FROM notes WHERE id = ?', params = (id,))
        except:
            return None

        return note

    def find_by_author(self, author):
        notes = self.db_manager.many('SELECT owner, id, STRFTIME("%d/%m/%Y, %H:%M", DATETIME(addDate, "localtime")), isEncrypted, isPublic FROM notes WHERE owner = ? ORDER BY addDate DESC', params = (author,))
        return notes

    def find_public(self, username):
        notes = self.db_manager.many('SELECT owner, id, STRFTIME("%d/%m/%Y, %H:%M", DATETIME(addDate, "localtime")), isPublic FROM notes WHERE isPublic = 1 AND isEncrypted != 1 AND owner != ? ORDER BY addDate DESC', params = (username,))
        return notes

    def find_draft(self, username):
        try:
            (draft,) = self.db_manager.one('SELECT markdown FROM drafts WHERE author = ? ORDER BY addDate DESC LIMIT 1', params = (username,))
        except:
            return None

        return draft

    def sanitized_markdown(self, user_text):
        is_save = True

        # Remove html added by user
        if(not self.allowed_user_html):
            text = self.remove_html(user_text)
            is_save = is_save and (text == user_text)
            user_text = text

        # Render markdown
        md = markdown.markdown(user_text)

        # Only allowed tags, attributes and protocols
        sanitized_md = bleach.clean(md, tags=self.allowed_tags, protocols=self.allowed_protocols, attributes=self.allowed_attr)
        
        # Only secure url in img tag
        src_attrs = re.findall('<img[^>]*src="([^"]+)"[^>]*>', sanitized_md)
        for src_attr in src_attrs:
            if not self.validate_url(src_attr):
                sanitized_md = sanitized_md.replace(src_attr, "")

        is_save = is_save and (sanitized_md == md)
        return sanitized_md, is_save

    def remove_html(self, text):
        return bleach.clean(text, tags=[], attributes={}, strip=True)

    def validate_url(self, url):
        # Only https protocol at the beginning
        if(not re.search('^https:\/\/', url)):
            return False

        # Forbidden localhost and 127.0.0.1
        if(re.search('localhost|127.0.0.1', url)):
            return False

        # Only jpg|png|gif extension at the end
        if(not re.search('\.(jpg|png|gif)$', url)):
            return False

        return True

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