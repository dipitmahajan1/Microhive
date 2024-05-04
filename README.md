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
or you can just run playground.ipynb. The file locations are not relative, change it to according to your local setup.
Screenshot of S3 :
<img width="1158" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/9d4c15b9-8b96-4122-af5c-2dd50d76a6bf">

Screenshot of DynamoDB :
<img width="1409" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/4b73ea4a-738c-47dc-a129-94e2e261441b">

Screenshot of Lambda Function hosted on cloud :
<img width="977" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/702f0040-3765-4491-ae15-b6c8045837b8">

2. Data Pipeline Diagram :
<img width="797" alt="image" src="https://github.com/dipitmahajan1/Microhive/assets/60647539/de7611e7-7941-4318-a600-ea89360aa250">

3. What improvement I would make with more time (includes limitations):
   >I would host my local Pyhton script to EC2 (Any cloud based processing service) and migrate everything to cloud. Right now my ETL script is local while S3 and Dynamodb are hosted on cloud.
   
   >I would make own Machine Learning model to extract Author, Title , Footer, Images from PDF. There is no ML model with good accuracy as of now. I have used NLP model 'SPACY' which uses Name 
    entity relationship to extract keyword. I used that model to extract author but accuracy wasn't good enough. Thus I would atleast give time to fine tune 'SPACY' to extract information.
   
5. What I did to meet each evaluation criteria :
   
   **Disclaimer** :  THE SCRIPT TO 100 % EXTRACT INFORMATION FROM EVERY PDF IS NOT POSSIBLE WITHOUT USING IN-HOUSE ML MODEL OR WITHOUT FINE TUNING NER MODEL. IN THE GIVEN TIME CONSTRUCTING AN 
   ETL SCRIPT WITH BEST ACCURACY WAS THE PRIORITY.THIS SCRIPT CAN BE USED TO EXTRACT INFORMATION FROM ALL PDF PAPERS BUT HAS BEEN WRITTEN TO GIVE HIGHEST ACCURACY WITH PAPER-1 BECAUSE IT TAKES 
   FEW ASSUMPTION WITH RESPECT TO WHERE AUTHOR,TITLE WOULD RESIDE IN THE PDF.THUS ALL IMAGES AND JSON FORMED SHOW PAPER1 AND IT IS THE ONE BEING STORED IN DYNAMO DB.HAVING SAID THAT YOU CAN STILL RUN THE CODE TO EXTRACT INFORMATION FROM ALL PDF AND SEE THE RESULTS.
   
   1.	Correctness: ETL script uses all the relevant libraries. Specific libraries to extract table, images have been used making it highly accurate. Seprate data analysis and novel 'footer' 
   and'header' identification model has been built to extract elements correctly.

   2.	Efficiency: The Data pipeline is highly effiecient. As soon as file lands in S3, data is stored in dynamo db. Images and raw data are stored in data lake (Used to store huge vol. of data)
      
   3.	Code quality: Code follows PEP-8. The naming uses snake case , comments have been written where ever possible to make it extremely readable.
      
   4.	Extensibility: Extensive use of classes and different files insure extensibility. This code can be extended to add any number of functions. It does not include one single file for ETL.
      
   5.	Cloud integration: DATA LAKE has been used to store large raw data. Dynamo DB has been used to store Json file. DynamoDB was selected because of the following reason :
      1)The data wasn't that large and thus dynamodb provides quick retrieval of not so large JSON data. It offers less latency and costs less.
     	2)If your data storage is focused on key-value access, quick lookups, and moderate querying, DynamoDB is likely more suitable. It's also better suited for applications that require 
        straightforward data storage with occasional access.

   7.	Documentation: Clear and concise documentation made.
      
   ![image](https://github.com/dipitmahajan1/Microhive/assets/60647539/452e5cc8-45fa-4781-8ef8-1ad3341a768a)




