from typing import Set,List

class Review:
    """Class to represent and save data of a Review"""

    def __init__(self,reviewerID:str,reviewerName:str=None,score:int=None,review:str=None):
        self.reviewerID = reviewerID
        self.reviewerName = reviewerName
        self.score = score
        self.review = review


    
    def __str__(self,verbose=False):
        text = f'''
          ________________________
        /
        | ID : {self.reviewerID}
        | Name : {self.reviewerName}
        | Score: {self.score}
        \__________________________
        '''
        if verbose:
            text += f'''
        Review:
        {self.review}
            '''
        return text