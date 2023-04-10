# GoodReadsScraper

This package aims to provide a program to scrape from the book repository goodreads, authors,books and their reviews information.  
It allows for single or multiple requests at a time, with the aim of creating review datasets.  
As goodreads is a highly dinamyc website, simple requests are not realiable enough to gather information, as such, a webdriver is necessary, provided by the selenium package. It is recommended to have firefox with geckodriver installed

## Book Scraping
Scraping a book's information, such as title, publication date, author, number of pages, average score, etc.  
This can be done by multiple means.
### Options:
- isbn :  
Search a book by it's **ISBN** reference.
- id :  
Search a book by it's goodreads id.
- btitle :  
Search a book by a given term (e.g. 'Harry Potter'), using similitaryti algorithms to find the best match.  
As there can be multiple books with the same title, this can be partened with the author option for further matching.

### Usage:
- grs -id 61215351  
Result:
---
         ________________________
        /
        | Book: The Fellowship of the Ring
        | ISBN: None
        | Author: J.R.R. Tolkien
        | Language: English
        | Published : 1954-07-29
        \__________________________
        | Score : 4.38
        | N.Ratings : 2679377
        | N.Reviews : 33909
        | N.Pages : 432
        | Genres : ['Fantasy', 'Classics', 'Fiction', 'Adventure', 'High Fantasy', 'Science Fiction Fantasy', 'Epic Fantasy', 'Audiobook', 'Young Adult', 'Novels']
        \
          --------------------------
---
- grs -btitle "Whose body"  
Result:
---
         ________________________
        /
        | Book: Whose Body
        | ISBN: 9780865346093
        | Author: Donald Levering
        | Language: English
        | Published : 2007-10-15
        \__________________________
        | Score : 4.75
        | N.Ratings : 4
        | N.Reviews : 1
        | N.Pages : 108
        | Genres : []
        \
          --------------------------
---
-  grs -btitle "Whose body" -a 'Dorothy l. Sayer'  
Result:
---
         ________________________
        /
        | Book: Whose Body?
        | ISBN: 9780061043574
        | Author: Dorothy L. Sayers
        | Language: English
        | Published : 1923-01-01
        \__________________________
        | Score : 3.85
        | N.Ratings : 52959
        | N.Reviews : 3559
        | N.Pages : 212
        | Genres : ['Mystery', 'Fiction', 'Classics', 'Crime', 'Mystery Thriller', 'Audiobook', 'Detective', 'Historical Fiction', 'British Literature', 'Historical']
        \
          --------------------------

## Author Scraping
Scraping an author's information, such as name, bithdate and place, death, works, average score, etc.

### Options:
- a :  
Search using the author's title with similitarity algorithms.
- mw:  
Maximum number of works to gather.

### Usage:

- grs -a 'Dorothy l. Sayer' -ve  
*ve is an extra option to show more of the scraped information  

Result: 
--- 
         ___________________________
        /
        | Author: Dorothy L. Sayers
        | Birth Place : in Oxford, England
        | Birth Date: June 13, 1893
        | Death: December 17, 1957
        | Website: http://www.sayers.org.uk/
        | Genres: ['Mystery', 'Poetry', 'Christian']
        | Influence: []
        \__________________________
        | Average Rating : 4.03
        | N.Ratings : 377,263
        | N.Reviews : 23,235
        | N.Unique Works : 475 distinct works
        \
          --------------------------

        Works:
                Whose Body?  (Lord Peter Wimsey, #1)
                Strong Poison (Lord Peter Wimsey, #5)
                Gaudy Night (Lord Peter Wimsey, #10)
                Unnatural Death (Lord Peter Wimsey, #3)
                Murder Must Advertise  (Lord Peter Wimsey, #8)
                Clouds of Witness (Lord Peter Wimsey, #2)
                Busman's Honeymoon (Lord Peter Wimsey, #11)
                The Nine Tailors (Lord Peter Wimsey, #9)
                ...
        Description:
         Dorothy Leigh Sayers was a renowned British author, translator, student of classical and modern languages, and Christian humanist.


          Dorothy L. Sayers is best known for her mysteries, a series of novels and short stories set between World War I and World War II that feature English aristocrat and amateur sleuth Lord Peter Wimsey. However, Sayers herself considered her translation of Dante's

           Divina Commedia

          to be her best work. She is also known for her plays and essays.

## Review Scraping
Scraping a book's reviews, single or multiple reviews at a time, gathering information such as the score given, the reviewer, the review,etc.  
Needs to be used paired with a book option described above.  
Can gather only the firts reviews of the review page, or make use of the dynamic options of the page to show more reviews and gather them.  

### Options:
- rs :  
Reviews simple, gather only the first reviews available in the book's review page (max 30).

- r :  
Reviews, gather all the reviews available in the book's review page (if there are many reviews this will be very slow and resource heavy as the single web page is being updated with more information).

- rg :  
Reviews range, gather reviews only in a certain range. E.g. [0,100], gathers review 0 to 100 if possible.

- rl :  
Reviews language, uses the language given to filter reviews on the page if such an option is found, otherwise no reviews are gathered.

- ro :  
Reviews output, defines an output file for the reviews to be written. If using the json option and there is a book with no review output defined, the global review output will be used, allowing for appending reviews from multiple books in a single file. If no output is given, reviews will be written to stdout.

### Usage:

- grs -btitle 'Watership Down' -a 'Richard Adams' -r -rg 0 100 -rl en  
 *Searching for the first 100 english reviews of *Watership Down*  
Result:  
---
      "Book";"Id";"Name";"Score";"Review"
      "Watership Down";"27788046";"Sean Barrs";"5";"I don’t give a ...
      ...  
          ________________________
        /
        | Book: Watership Down
        | ISBN: 9780380395866
        | Author: Richard  Adams
        | Language: English
        | Published : 1972-11-01
        \__________________________
        | Score : 4.08
        | N.Ratings : 466779
        | N.Reviews : 16296
        | N.Pages : 478
        | Genres : ['Classics', 'Fiction', 'Fantasy', 'Young Adult', 'Animals', 'Childrens', 'Adventure', 'Literature', 'Novels', 'Audiobook']
        \
          --------------------------


## Extras

 - o:  
 Output file for both author and book information.

 - l:  
 Logging option. Logs about the proceding of the program, written on stdout, recommended as the tasks can be lengthy and this gives information about their progress and helps notice if it is stuck.

 - j:  
 Json file that allows for giving multiple iterations of the program to be given at once. This follows the format:  
---

    {
        "books": [
            {
                "name" : "Coraline",
                "author" : "Neil Gaiman", 
                "output" : "coraline.txt",
                "reviews" : true,
                "reviews_output" : "caroline_reviews.csv",
                "reviews_range" : [40,60],
                "reviews_language" : "pt"

            }
        ],
        "authors" : [
            {
                "name" : "abel ferreira",
                "output" : "abel.txt"
            }
        ]
}

Where the first key *books* represents all the books that are meant to be scraped. Each book can have its task costumized to only search for the basic info, its output, gather reviews in a range and so on. The flags explained before are also available here in the same contexts, whereas in this case their full name has to be given, as exemplefied, for ease of legibility (special case for 'btitle' and 'a' which both are recognized as 'name').  
As mentioned before, if a book does not have a review output defined, they will either go to the default output or, if a global review output is given with the flag **-ro**, they will be appended there.

- e:  
Error output file

- ve:  
Verbose option. Writes full information for a given author or book, this is, their description or works list.

- V:  
Shows the program version.