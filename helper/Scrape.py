from bs4 import BeautifulSoup
import requests, re
from entities.Book import Book
from entities.Chapter import Chapter
from helper.DataService import DataService
from tqdm import tqdm, trange
import traceback

class Scrape:
    def __init__(self):
        self.data_service = DataService('data/database.db')
        self.books = set()
        self.baseUrl = "https://wol.jw.org/de/wol/binav/r10/lp-x/nwtsty/"
    
    def book_exists(self, book_name, book_number):
        # check if book exists in local database
        for book in self.books:
            if book.name == book_name:
                book.number = book_number
                return True
        # check if book exists in DataService
        if self.data_service.book_exists(book_name):
            return True
        return False
    
    def get_chapter_url(self, book_number, chapter_number):
        return f"https://wol.jw.org/de/wol/b/r10/lp-x/nwtsty/{book_number}/{chapter_number}#study=discover"
    
    def add_book(self, book):
        # check if book is of instance Book
        if not isinstance(book, Book):
            raise Exception("Object is not of type Book")
        self.books.add(book)

    def append_book(self, book):
        # check if book is of instance Book
        if not isinstance(book, Book):
            raise Exception("Object is not of type Book")
        self.books.append(book)

    def add_new_book(self, name, book_number):
        book = Book(name, self.data_service)
        book.number = book_number
        self.append_book(book)
        return book
    
    def add_book_from_DataService(self, name, book_number):
        # check if book exists in memory
        for book in self.books:
            if book.name == name:
                book.number = book_number
                return
        
        book = self.data_service.get_book(name)
        book.number = book_number
        if book is None:
            raise Exception("Book does not exist in DataService")
        self.append_book(book)
    
    def get_last_book(self):
        if len(self.books) == 0:
            raise Exception("No book added")
        # return last book in set
        return self.books[-1]

    def add_chapters_list_to_last_book(self, chapters):
        for chapter in chapters:
            self.get_last_book().addChapter(chapter)
        self.data_service.store_book(self.get_last_book(), self.get_last_book().number)

    def cast_string_to_int(self, string):
        return int(string.replace(".", ""))

    def parse_html_scrape_to_text(self, verses_html):
        parsedTextResult = ['']
            
        for i, htmlVers in enumerate(verses_html):
            verseText = htmlVers.text
            # remove all special characters
            verseText = verseText.replace("+", "")
            verseText = verseText.replace("*","")
            verseText = verseText.replace("  "," ")
            pattern = r"\xa0"
            verseText = re.sub(pattern, "", verseText)
            # remove all verse numbers
            pattern = r"^\d{1,3}"
            match = re.match(pattern, verseText)
            if match:
                # if match is found, remove the match from the string
                number = match.group(0)
                remaining_text = verseText[len(number):].strip()
                parsedTextResult.append(remaining_text)
            else:
                # if match is not found, append the text to the last element in the list
                parsedTextResult[-1] += verseText
                    
        return parsedTextResult

    def get_chapters_by_soup(self, soup):
        chapter_elements = soup.find_all('li', class_='chapter')
        chapters = []
        for element in chapter_elements:
            chapters.append(element.a.text)
        return chapters
        
    
    def scrape_request_with_url(self, url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        return soup

    def parse_soup_html_verses(self, soup):
        article = soup.find('article', class_='article')
        verses_html = soup.find_all('span', class_='v')
        if len(verses_html) == 0:
            verses_html = soup.find_all('p', class_='sb')
        if len(verses_html) == 0:
            raise Exception("No verses found")
        
        verses = self.parse_html_scrape_to_text(verses_html)
        return verses
    
    def check_book_number(self, book_number):
        for book in self.books:
            if book.number == book_number:
                return True
        return False

    def scrape(self):
        self.data_service.clean_books()
        self.look_up_books()
        if len(self.books) == 66:
            return
        for num_book in trange(1, 67, ncols=100, desc='Scraping Bible Book'):
            if self.check_book_number(num_book):
                continue
            
            # get the soup for the book number and parse the html to get the book name and chapter numbers
            # then add the book to the list of books and add the chapters to the last book in the list of book
            soup = self.scrape_request_with_url(f"{self.baseUrl}{num_book}")

            header = soup.find('header').find('h1')
            
            if self.book_exists(header.text, num_book):
                self.add_book_from_DataService(header.text, num_book)
            else:
                self.add_new_book(header.text, num_book)
                chapters = []
                for chapter_number in tqdm(self.get_chapters_by_soup(soup), ncols=100, desc='Scraping Bible Chapter'):
                    cpNum = self.cast_string_to_int(chapter_number)

                    soup = self.scrape_request_with_url(self.get_chapter_url(num_book, chapter_number))

                    verses = self.parse_soup_html_verses(soup)
                    chapter = Chapter(cpNum, verses)
                    chapters.append(chapter)
                self.add_chapters_list_to_last_book(chapters)
    
    def look_up_books(self):
        all_books = self.data_service.get_all_books()
        # Create a set to store unique book names
        unique_names = set()

        # Iterate over the list and check for duplicates
        for book in tqdm(all_books, ncols=100, desc='Looking up Books'):
            if book.name not in unique_names:
                unique_names.add(book.name)
                self.add_book(book)
        self.books = list(self.books)
        
    def access_firestore_book_collection_document(self, book_name):
        return self.data_service.access_collection_document(book_name)
            
    def persistAllBooks(self):
        for book in tqdm(self.books, ncols=100, desc='Persisting Books'):
            doc_ref = self.access_firestore_book_collection_document(book.name)
            doc_ref.set(book.default(), merge=True)
        
    
    def start(self):
        try:
            self.scrape()
            self.persistAllBooks()
            print("Scrape has completed succesfully")
        except Exception as e:
                print(e)
                print("Scrape has failed")
                print(traceback.format_exc())
                return -1
        finally:
            self.data_service.close_connection()
        