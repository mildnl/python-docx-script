import unittest
from entities.Book import Book
from entities.Chapter import Chapter
from helper.DataService import DataService

class DataServiceTest(unittest.TestCase):

    def setUp(self):
       self.data_service = DataService('data/test.db') 

    def tearDown(self):
        self.data_service.delete_all()
        pass

    def test_store_book(self):

        book = Book("Test Book", self.data_service)
        chapter1 = Chapter(1, ["Verse 1.1", "Verse 1.2"])
        chapter2 = Chapter(2, ["Verse 2.1", "Verse 2.2"])
        book.addChapter(chapter1)
        book.addChapter(chapter2)

        self.data_service.store_book(book)
        self.assertEqual(self.data_service.book_exists("Test Book"), True)

    def test_get_book(self):

        book = Book("Test Book", self.data_service)
        chapter1 = Chapter(1, ["Verse 1.1", "Verse 1.2"])
        chapter2 = Chapter(2, ["Verse 2.1", "Verse 2.2"])
        book.addChapter(chapter1)
        book.addChapter(chapter2)

        self.data_service.store_book(book)

        retrieved_book = self.data_service.get_book("Test Book")
        self.assertEqual(retrieved_book.name, "Test Book")
        self.assertEqual(len(retrieved_book.chapters), 2)
        self.assertEquals(retrieved_book.chapters[0].verses[0], "1 Verse 1.1")
        self.assertEquals(retrieved_book.chapters[1].verses[1], "2 Verse 2.2")

    def test_book_exists(self):

        self.assertEqual(self.data_service.book_exists("Test Book"), False)

        book = Book("Test Book", self.data_service)
        chapter1 = Chapter(1, ["Verse 1", "Verse 2"])
        book.addChapter(chapter1)

        self.data_service.store_book(book)
        self.assertEqual(self.data_service.book_exists("Test Book"), True)

if __name__ == '__main__':
    unittest.main()
