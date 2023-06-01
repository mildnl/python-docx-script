import json
from .Chapter import Chapter


class Book:
    def __init__(self, name, dataservice):
        self.number = None
        self.name = name
        self.chapters = None
        self.datenservice = dataservice

    def addChapter(self, chapter):
        if self.chapters is None:
            self.chapters = []
        if not isinstance(chapter, Chapter):
            raise TypeError("chapter must be of type Chapter")
        self.chapters.append(chapter)

    def addChapterByNumber(self, chapterNumber):
        if self.chapters is None:
            self.chapters = []
        if not isinstance(chapterNumber, int):
            raise TypeError("chapterNumber must be of type int")
        self.chapters.append(Chapter(chapterNumber, []))

    def save(self):
        self.datenservice.store_book(self)

    def getJson(self):
        return json.dumps(self, cls=self.BookEncoder)

    def __len__(self):
        return len(self.chapters)

    def __str__(self):
        res = f"Book:{self.name}\n"
        for c in self.chapters:
            verses = f"Chapter {c.number} : [ \n"
            for i, v in enumerate(c.verses):
                    verses += f"    {i + 1}: {v},\n"
            verses = verses[:-1] + "\n]"
            res += f"{c.number}: {verses}\n"
        return res
    
    def default(self):
        res = {}
        for c in self.chapters:
            res[f"{c.number}"] = c.verses
        # add book number
        res["number"] = self.number
        return res
    
    def verify(self):
        if self.name is None:
            return False
        if self.chapters is None:
            return False
        return True
        
    
    class BookEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Book):
                return obj.default()
            return json.JSONEncoder.default(self, obj)
