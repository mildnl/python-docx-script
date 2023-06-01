class Chapter:
    def __init__(self, number, verses):
        self.number = number
        self.verses = verses
    
    def verses_json(self):
        for verse in self.verses:
            yield verse.default()
    
    def __len__(self):
        return len(self.verses)

    def __str__(self):
        return f"Chapter {self.number}: [\n    {self.verses}\n]"
        
    def default(self):
        return {
            f"{self.number}": self.verses
        }