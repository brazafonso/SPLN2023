class Book:
    """Class to represent and save data of a book"""
    def __init__(self,name,isbn,author=None,description=None,publishing_date=None,score=None,nratings=None,nreviews=None,npages=None,language=None,genres=None):
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

    def name(self):
        return self.name
    
    def isbn(self):
        return self.isbn
    
    def author(self):
        return self.author
    
    def description(self):
        return self.description
    
    def score(self):
        return self.score
    
    def nratings(self):
        return self.nratings
    
    def nreviews(self):
        return self.nreviews
    
    def npages(self):
        return self.npages
    
    def language(self):
        return self.language
    
    def genres(self):
        return self.genres
    
    def publishing_date(self):
        return self.publishing_date
    

    def set_author(self,author):
        self.author = author
    
    def set_description(self,description):
        self.description=description
    
    def set_score(self,score):
        self.score=score
    
    def set_nratings(self,nratings):
        self.nratings=nratings
    
    def set_nreviews(self,nreviews):
        self.nreviews=nreviews
    
    def set_npages(self,npages):
        self.npages=npages
    
    def set_language(self,language):
        self.language=language
    
    def set_genres(self,genres):
        self.genres=genres
    
    def set_publishing_date(self,publishing_date):
        self.publishing_date=publishing_date


    def __str__(self,verbose=False):
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