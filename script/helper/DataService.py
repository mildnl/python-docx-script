import sqlite3
import json
from tqdm import tqdm
from entities.Book import Book
from entities.Chapter import Chapter
from helper.FirebaseHelper import FirebaseHelper

class DataService:
    def __init__(self, dbfile):
        self.connection = sqlite3.connect(dbfile)
        self.cursor = self.connection.cursor()
        self.create_table()
        self.firebase_helper = FirebaseHelper()


    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books
                              (id INTEGER PRIMARY KEY, name TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS chapter 
                              (id INTEGER PRIMARY KEY, book_id INTEGER, number INTEGER, data TEXT)''')
        self.connection.commit()

    def delete_all(self):
        self.cursor.execute("DELETE FROM books")
        self.cursor.execute("DELETE FROM chapter")
        self.connection.commit()

    def store_book(self, book, book_number):
        if book_number is None:
            self.cursor.execute("INSERT INTO books (name) VALUES (?)", (book.name,))
            book_id = self.cursor.lastrowid
        else:
            self.cursor.execute("INSERT INTO books (id, name) VALUES (?, ?)", (book_number, book.name))
            self.connection.commit()
            book_id = self.cursor.lastrowid
        for chapter in book.chapters:
            chapter_data = chapter.default()
            verses = ''
            for i, verse in enumerate(chapter_data[f"{chapter.number}"]):
                verses += f"{i + 1} {verse}\n"
            self.cursor.execute("INSERT INTO chapter (book_id, number, data) VALUES (?, ?, ?)", (book_id, chapter.number, verses))
        

    def get_book(self, book_name):
        self.cursor.execute("SELECT id FROM books WHERE name=?", (book_name,))
        ref = self.cursor.fetchone()
        if ref is not None:
            book_id = ref[0]
            self.cursor.execute("SELECT number, data FROM chapter WHERE book_id=?", (book_id,))
            result = self.cursor.fetchall()
            return self.parse_book_data(result, book_name)
        else:
            if self.firebase_helper.book_exists(book_name):
                document_data = self.firebase_helper.access_collection_document(book_name)
                book = self.parse_document_data(document_data)
                self.store_book(book, None)
                return book
        return None
    
    def get_list_book_ids(self):
        self.cursor.execute("SELECT * FROM books")
        result = self.cursor.fetchall()
        return result
    
    def delete_book(self, book_name):
        self.cursor.execute("SELECT id FROM books WHERE name=?", (book_name,))
        ref = self.cursor.fetchone()
        if ref is not None:
            book_id = ref[0]
            self.cursor.execute("DELETE FROM chapter WHERE book_id=?", (book_id,))
            self.cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
            self.connection.commit()
            return True
        return False
    
    def clean_book(self, book_name):
        self.cursor.execute("SELECT id FROM books WHERE name=?", (book_name,))
        ref = self.cursor.fetchone()
        if ref is not None:
            book_id = ref[0]
            self.cursor.execute("SELECT number, data FROM chapter WHERE book_id=?", (book_id,))
            result = self.cursor.fetchall()
            if len(result) == 0:
                return self.delete_book(book_name)
        return None

    def get_all_books(self):
        self.cursor.execute("SELECT name FROM books")
        result = self.cursor.fetchall()
        books = []
        for book_name in tqdm(result, ncols=100, desc='Retrieving books from database', unit='book', unit_scale=True, ascii=True, bar_format='{l_bar}{bar:100}{r_bar}'):
            book = self.get_book(book_name[0])
            if book is None:
                raise Exception('Book not correctly persisted to database', book)
            if not book.verify():
                raise Exception('Book not correctly persisted to database', book)
            books.append(book)
        return books
    
    def clean_books(self):
        self.cursor.execute("SELECT name FROM books")
        result = self.cursor.fetchall()
        for book_name in tqdm(result, ncols=100, desc='Cleaning books from database', unit='book', unit_scale=True, ascii=True, bar_format='{l_bar}{bar:100}{r_bar}'):
            self.clean_book(book_name[0])
            

    def book_exists(self, book_name):
        self.cursor.execute("SELECT name FROM books WHERE name=?", (book_name,))
        result = self.cursor.fetchone()
        if result is None:
            return self.firebase_helper.book_exists(book_name)
        return True

    def parse_book_data(self, book_data, book_name):
        book = Book(book_name, self)  # Create the book object with the book name
        for row in book_data:
            chapter_number = row[0]
            verses = row[1].split('\n')[:-1]  # Split the verses string into a list
            chapter = Chapter(chapter_number, verses)
            book.addChapter(chapter)
        return book
    
    def parse_document_data(self, document_data):
        book_name = document_data.id
        book_data = document_data.get().to_dict()
        book = Book(book_name, self)
        for chapter_number, chapter_data in book_data.items():
            chapter = Chapter(chapter_number, chapter_data)
            book.addChapter(chapter)
        return book

    def close_connection(self):
        self.cursor.close()
        self.connection.close()
    
    def get_db(self):
        return self.firebase_helper.get_db()
    
    def access_collection_document(self, book_name):
        return self.get_db().collection(u'New World Translation').document(book_name)
