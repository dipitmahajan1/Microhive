MICRO HIVE DATA ENGENEERING TASK 


Table of contents :

1) Introduction and Purpose of each file (Includes how to run them).
2) Data Pipeline Diagram.
3) What improvement I would make with more time (includes limitations).
4) What I did to meet each evaluation criteria.



1. Introduction and Purpose of each file :
   
This a data engineering task done for Microhive. The purpose of this task was to extract important information from PDFs , Transform it and Load it in cloud database of choice.

> Main.py : Main.py is the main file that contains Main() function. 
It has all the functions to extract information from PDFs. It has three main functions 
1) get_elements: This function extracts all the information from PDF and puts it in a dictionary. All the information includes : Text on each page (page_text), Format of each line ('line_format'), Text extracted from each images('text_from_tables'),Text extracted from each table ('text_from_tables'), Content of each page('page_content'). It also extracts images stored on each page and stores it in Images folder.
2) get_footer : This function extracts footer present on each page and puts it in dictionary.
3) get_extracontent : This function gets 'Title', 'Author', 'Abstract' from each paper.

Then main() function converts the dictionary to JSON and stores the JSON in AWS Data Lake(S3).

> Extract.py : Extract function has specific function to extract text, images , tables from pdf. It also has very important function fonts and font_tags to get information on fonts and font styles used in the whole pdf.

It played a very important role to find footer. It showed footer font size and style was different to whole pdf and thus we were able to extract that.

>Preprocessing.py : It has all functions to preprocess pdf.
>BucketConnect.py : It has function to connect to AWS and load file and image folders in bucket.
>Lambda.py : Lambda function to trigger file transfer as soon as file lands in S3. The lambda function stores the JSON into Dynamodb.
>DataAnalysis.ipynb :   THIS IS THE PYTHON NOTEBOOK WHERE ANALYSIS WAS DONE ON THE FOLLOWING :
1) Structure of PDFs. To find what is skeleton of each pdf. Is there anything common between them?
2) To find what fonts, tags and font size has been used.
Following contains my analysis on 'paper1.pdf'
RESULT : THIS ANALYSIS PLAYED A VERY IMPORTANT ROLE IN CORRECTLY IDENTIFYING HEADERS AND FOOTERS. HELPED US IN ISOLATING THEM.
>Playground.ipynb : Ipynb file where i played around to find best possible way to get data.


HOW TO RUN : Download all the libraries and dependency and Run Main.py 
or you can just run playground.ipynb.
Screenshot of S3 :
<img width="1158" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/9d4c15b9-8b96-4122-af5c-2dd50d76a6bf">
Screenshot of DynamoDB :
<img width="1409" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/4b73ea4a-738c-47dc-a129-94e2e261441b">
Screenshot of Lambda Function hosted on cloud :
<img width="977" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/702f0040-3765-4491-ae15-b6c8045837b8">

2. Data Pipeline Diagram :

<img width="797" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/de7611e7-7941-4318-a600-ea89360aa250">

3. What improvement I would make with more time (includes limitations):
4. What I did to meet each evaluation criteria :




