from source.dbManager import DBManager
import markdown

class NoteManager:
    def __init__(self):
        self.db_manager = DBManager()

    def add(self, author, text):
        note = markdown.markdown(text)
        self.db_manager.insert('INSERT INTO notes (owner, note) VALUES (?, ?)', params = (author, note))

        return note
    
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