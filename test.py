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
        print("总长度:",length-1)
        English_Words.GetWord(self,randint(1,length))
                    
    def Split(self,word):
        ''' 
        word : 被分割的字符串 
        en : 英语词汇
        Phonepic_symbol : 英语音标
        Part_of_speech : 词性
        zh : 汉语含义
        '''
        result = word.split()
        en = result[0]
        Phonepic_symbol = result[1]
        Part_of_speech = result[2]
        zh = result[3]
        word_element = [en,Phonepic_symbol,Part_of_speech,zh]
        for i in word_element:
            print(i)
        
    def GetWord(self,id):
        word = self.words[id]
        print(id,":",word)
        English_Words.Split(self,word)
            
        

if __name__ == "__main__":
    a = English_Words()
    a.ReadText()
    