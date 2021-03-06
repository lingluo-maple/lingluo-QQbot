import os
import sys
import time
from random import randint

class English_Words():
    def __init__(self):
        self.file_path = sys.path[0]
        self.words = []

    def ReadText(self):
        with open(self.file_path + "/words.txt") as f:
            while True:
                txt = f.readline()[:-1]
                self.words.append(txt)
                if txt == "":
                    English_Words.function(self)
                    break
                    
    def function(self):
        length = len(self.words)
        English_Words.GetWord(self,randint(1,length))
                    
    def Split(self):
         for i in self.words:
             print(i)
             time.sleep(1)
             print(i.split())
             time.sleep(1)

    def GetWord(self,id):
        print(self.words[id])
            
        

if __name__ == "__main__":
    a = English_Words()
    a.ReadText()
    