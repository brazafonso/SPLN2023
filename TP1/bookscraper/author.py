from typing import Set,List

class Author:
    """Class to represent and save data of an author"""

    def __init__(self,name:str,birthdate:str=None,birthplace:str=None,deathdate:str=None,
                 website:str=None,genres:Set[str]=None,influence:Set[str]=None,
                 description:str=None,averageRating:float=None,nratings:int=None,
                 nreviews:int=None,nUniqueWorks:int=None,works:List[str]=None):
        self.name = name
        self.birthdate = birthdate
        self.birthplace = birthplace
        self.deathdate = deathdate
        self.website = website
        self.genres = genres
        self.influence = influence
        self.description = description
        self.averageRating = averageRating
        self.nratings = nratings
        self.nreviews = nreviews
        self.nUniqueWorks = nUniqueWorks
        self.works = works


    def name(self)->str:
        return self.name
    
    def birthdate(self)->str:
        return self.birthdate
    
    def birthplace(self)->str:
        return self.birthplace
    
    def deathdate(self)->str:
        return self.deathdate
    
    def website(self)->str:
        return self.website
    
    def genres(self)->Set[str]:
        return self.genres
    
    def averageRating(self)->float:
        return self.averageRating

    def nratings(self)->int:
        return self.nratings
    
    def nreviews(self)->int:
        return self.nreviews
    
    def nUniqueWorks(self)->int:
        return self.nUniqueWorks
    
    def works(self)->List[str]:
        return self.works
    
    def set_birthdate(self, date:str):
        self.birthdate = date

    def set_birthplace(self, place:str):
        self.set_birthplace = place

    def set_deathdate(self, date:str):
        self.deathdate = date

    def set_website(self, website:str):
        self.website = website

    def set_genres(self,genres:Set[str]):
        self.genres = genres
    
    def set_influence(self,influence:Set[str]):
        self.influence = influence

    def set_description(self,description:str):
        self.description = description

    def set_averageRating(self,averageRating:float):
        self.averageRating = averageRating

    def set_nratings(self,nratings:int):
        self.nratings = nratings

    def set_nreviews(self,nreviews:int):
        self.nreviews = nreviews

    def set_nUniqueWorks(self,nUniqueWorks:int):
        self.nUniqueWorks = nUniqueWorks

    def set_works(self,works:List[str]):
        self.works = works


    def __str__(self,verbose=False)->str:
        text = f'''
         ___________________________
        /
        | Author: {self.name}
        | Birth Place : {self.birthplace}
        | Birth Date: {self.birthdate}'''
        if self.deathdate: 
            text += f'''
        | Death: {self.deathdate}'''
        text += f'''
        | Website: {self.website}
        | Genres: {self.genres}
        | Influence: {self.influence}
        \__________________________
        | Average Rating : {self.averageRating}
        | N.Ratings : {self.nratings}
        | N.Reviews : {self.nreviews}
        | N.Unique Works : {self.nUniqueWorks}
        \ 
          --------------------------
        '''
        if verbose:
            text += f'''
        Works:'''
            for work in self.works:
                text += f'''
                {work}'''
            text += f''''
        Description:
        {self.description}
        '''
        return text

