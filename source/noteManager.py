from source.dbManager import DBManager
import os, markdown, bleach, json

class NoteManager:
    def __init__(self):
        self.db_manager = DBManager()
        self.allowed_tags = json.loads(os.getenv('ALLOWED_TAGS'))
        self.allowed_protocols = json.loads(os.getenv('ALLOWED_PROTOCOLS'))

    def add(self, author, text):
        note = markdown.markdown(text)

        sanitized_note = bleach.clean(note, tags=self.allowed_tags, protocols=self.allowed_protocols)
        requiredSanitization = (note != sanitized_note)

        self.db_manager.insert('INSERT INTO notes (owner, note) VALUES (?, ?)', params = (author, sanitized_note))

        return sanitized_note, requiredSanitization
    
    def find_by_id(self, id):
        try:
            row = self.db_manager.one('SELECT owner, note FROM notes WHERE id = ?', params = (id,))
            author, note = row
            return author, note
        except:
            return None, None

    def find_by_author(self, author):
        notes = self.db_manager.many('SELECT id FROM notes WHERE owner = ?', params = (author,))
        return notes