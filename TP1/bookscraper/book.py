from typing import Set

class Book:
    """Class to represent and save data of a book"""
    def __init__(self,name:str,isbn:str,author:str=None,
                 description:str=None,publishing_date:str=None,
                 score:float=None,nratings:int=None,nreviews:int=None,
                 npages:int=None,language:str=None,genres:Set[str]=None):
        self.name = name
        self.isbn = isbn
        self.author = author
        self.description = description  
        self.publishing_date = publishing_date
        self.score = score
        self.nratings = nratings
        self.nreviews = nreviews
        self.npages = npages
        self.language = language
        self.genres = genres

    def name(self)->str:
        return self.name
    
    def isbn(self)->str:
        return self.isbn
    
    def author(self)->str:
        return self.author
    
    def description(self)->str:
        return self.description
    
    def score(self)->float:
        return self.score
    
    def nratings(self)->int:
        return self.nratings
    
    def nreviews(self)->int:
        return self.nreviews
    
    def npages(self)->int:
        return self.npages
    
    def language(self)->str:
        return self.language
    
    def genres(self)->Set[str]:
        return self.genres
    
    def publishing_date(self)->str:
        return self.publishing_date
    

    def set_author(self,author:str):
        self.author = author
    
    def set_description(self,description:str):
        self.description=description
    
    def set_score(self,score:float):
        self.score=score
    
    def set_nratings(self,nratings:int):
        self.nratings=nratings
    
    def set_nreviews(self,nreviews:int):
        self.nreviews=nreviews
    
    def set_npages(self,npages:int):
        self.npages=npages
    
    def set_language(self,language:str):
        self.language=language
    
    def set_genres(self,genres:Set[str]):
        self.genres=genres
    
    def set_publishing_date(self,publishing_date:str):
        self.publishing_date=publishing_date


    def __str__(self,verbose=False)->str:
        text = f'''
          ________________________
        /
        | Book: {self.name}
        | ISBN: {self.isbn}
        | Author: {self.author}
        | Language: {self.language}
        | Published : {self.publishing_date}
        \__________________________
        | Score : {self.score}
        | N.Ratings : {self.nratings}
        | N.Reviews : {self.nreviews}
        | N.Pages : {self.npages}
        | Genres : {self.genres}
        \ 
          --------------------------
        '''
        if verbose:
            text += f'''
        Description:
        {self.description}
            '''
        return text