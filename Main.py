from Extract import Extract
from Preprocessing import Reader
from BucketConnect import connect_aws, upload_folder
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
from PIL import Image
from pdf2image import convert_from_path
from operator import itemgetter
import pdfplumber
import fitz
import json
import pytesseract 
import PyPDF2
import os
import re
import spacy


'''Function to get all element per page (text, images, tables, text within images) and make a nested dictionary. 
Dictionary will look like this = {'page_0' : }'''
def get_elements(paper) :

    extract = Extract()                                                #Object of the class Extract
    pdfFileObj = open(paper, 'rb')
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # Create the dictionary to extract text from each image
    text_per_page = {}
    # Create a boolean variable for image detection
    image_flag = False

    # We extract the pages from the PDF
    for pagenum, page in enumerate(extract_pages(paper)):

        # Initialize the variables needed for the text extraction from the page
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        # Initialize the number of the examined tables
        table_in_page= -1
        # Open the pdf file
        pdf = pdfplumber.open(paper)
        # Find the examined page
        page_tables = pdf.pages[pagenum]
        # Find the number of tables in the page
        tables = page_tables.find_tables()
        if len(tables)!=0:
            table_in_page = 0

        # Extracting the tables of the page
        for table_num in range(len(tables)):
            # Extract the information of the table
            table = extract.extract_table(paper, pagenum, table_num)
            # Convert the table information in structured string format
            table_string = extract.table_converter(table)
            # Append the table string into a list
            text_from_tables.append(table_string)

        # Find all the elements
        page_elements = [(element.y1, element) for element in page._objs]
        # Sort all the element as they appear in the page 
        page_elements.sort(key=lambda a: a[0], reverse=True)


        # Find the elements that composed a page
        for i,component in enumerate(page_elements):
            # Extract the element of the page layout
            element = component[1]

            # Check the elements for tables
            if table_in_page == -1:
                pass
            else:
                if extract.is_element_inside_any_table(element, page ,tables):
                    table_found = extract.find_table_for_element(element,page ,tables)
                    if table_found == table_in_page and table_found != None:    
                        page_content.append(text_from_tables[table_in_page])
                        page_text.append('table')
                        line_format.append('table')
                        table_in_page+=1
                    # Pass this iteration because the content of this element was extracted from the tables
                    continue

            if not extract.is_element_inside_any_table(element,page,tables):

                # Check if the element is text element
                if isinstance(element, LTTextContainer):
                    # Use the function to extract the text and format for each text element
                    (line_text, format_per_line) = extract.text_extraction(element)
                    # Append the text of each line to the page text
                    page_text.append(line_text)
                    # Append the format for each line containing text
                    line_format.append(format_per_line)
                    page_content.append(line_text)


                # Check the elements for images
                if isinstance(element, LTFigure):
                    # Crop the image from PDF
                    extract.crop_image(element, pageObj, pagenum)
                    # Convert the croped pdf to image
                    extract.convert_to_images('cropped_image_'+ str(pagenum)+'.pdf', pagenum)
                    #Extracting Images on each page and putting it in seperate folder
                    image_text = extract.image_to_text('Images/PDF_image' + str(pagenum)+ '.png')      
                    text_from_images.append(image_text)
                    page_content.append(image_text)
                    # Add a placeholder in the text and format lists
                    page_text.append('image')
                    line_format.append('image')
                    # Update the flag for image detection
                    image_flag = True


        # Create the key of the dictionary
        dctkey = 'Page_'+str(pagenum)
        # Add the list of list as value of the page key
        text_per_page[dctkey]= {'page_text' : page_text, 'line_format' : line_format, 'text_from_images' : text_from_images, 'text_from_tables' : text_from_tables, 'page_content': page_content}


    return text_per_page

#Function to get footer will return dictionary with footer information on each page
def get_footer(doc, size_tag):

    header_para = []  # list with headers and paragraphs
    foots = []
    Raw_data = []
    first = True  # boolean operator for first header
    previous_s = {}  # previous span
    abstract = []
    page_attribute = {}

    for pagenum, page in enumerate(doc):
        foots = []
        Raw_data = []
        
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text
                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s

                    # new block started, indicating with a pipe
                        
                    block_string += " "

                if re.match(r'^<s4>', block_string):
                        block_string= re.sub(r'^<s4>', '', block_string, flags=re.MULTILINE)
                        foots.append(block_string)

                elif re.match(r'^<p>', block_string):
                        
                        block_string= re.sub(r'^<p>', '', block_string, flags=re.MULTILINE)
                        Raw_data.append(block_string)

                header_para.append(block_string)

            
        mapkey = 'Page_'+str(pagenum)
        page_attribute[mapkey] = {'footer': foots}

    return page_attribute

#function to get AUTHOR,TITLE,ABSTRACT from pdfs
def get_extracontent(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[1]  # Assuming title, authors, and abstract are on the first page
        second_page = pdf.pages[1] 
        text = first_page.extract_text()
        text_1 = second_page.extract_text()

        # This is a simple example and may need to be adjusted based on your specific PDF layout
        title = text.split('\n')[0]  # Assuming the first line is the title
        authors = text.split('\n')[3]  # Assuming the second line contains the authors

        abstract_index = text.lower().find('abstract')
        end_index = text.lower().find('keywords')

        if end_index == -1 :

            end_index = text.lower().find('key words')

        abstract_text = text[abstract_index : end_index].split('\n')[1:]  # Assuming abstract starts after the 'abstract' keyword

        abstract = ' '.join(abstract_text).replace('\n', ' ')

    return {
        'title': title,
        'authors': authors,
        'abstract': abstract   
    }


'''THIS FUNCTION USES MACHINE LEARNING TO EXTRACT AUTHOR NAME WE ARE LOADING NLP MODEL FOR NER . THIS DID NOT GIVE DESIRED RESULTS THUS NOT USED'''
def extract_author_name(pdf_path):
    nlp = spacy.load('/Users/dipit.mahajan/anaconda3/lib/python3.11/site-packages/en_core_web_sm/en_core_web_sm-3.7.1')
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + " "  # Concatenate text from each page

        # Find the position of the keyword 'author' and capture the following text
        pattern = r'Authors[:\s]*([\w\s]+)' 
        match = re.search(pattern, full_text, re.IGNORECASE)  # Search up to 200 characters after 'author'
        if match:
            # Process the captured text with spaCy
            doc = nlp(match.group(1))
            # Extract the first proper name after the keyword
            for ent in doc.ents:
                if ent.label_ in ['PERSON']:
                    return ent.text.strip()
        return "Author not found"
    

def merge_nested_dicts(d1, d2):
    """
    Merge two nested dictionaries. This function will update d1 with values from d2.
    In case of overlapping keys, inner dictionaries are merged recursively.
    
    Parameters:
    d1 (dict): First dictionary with nested structure.
    d2 (dict): Second dictionary with nested structure to merge with the first dictionary.
    
    Returns:
    dict: d1 updated with merged values from d2.
    """
    for key in d2:
        if key in d1:
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                merge_nested_dicts(d1[key], d2[key])
            else:
                # If they are not both dicts, replace the value in d1 with d2's value
                d1[key] = d2[key]
        else:
            # If the key from d2 is not in d1, add it to d1
            d1[key] = d2[key]
    return d1




if __name__ == '__main__':


    pdfs = ['pdfs/paper1.pdf','pdfs/paper2.pdf','pdfs/paper3.pdf','pdfs/paper4.pdf','pdfs/paper5.pdf'] 
    extract = Extract()

    #Processing pdfs one by one 
    for number,paper in enumerate(pdfs) :

        doc = fitz.open(paper)
        font_counts, styles = extract.fonts(doc, granularity=False)
        size_tag = extract.font_tags(font_counts, styles)

        footer_per_page = get_footer(doc, size_tag)
        info_per_page = get_elements(paper)
        extracontent = get_extracontent(paper)

        merge_dict = merge_nested_dicts(footer_per_page, info_per_page)
        extracontent.update(merge_dict)                                            # We have final dictionary with all scraped information from paper

        # writing dictionary into json file 
        img_path = '/Users/dipit.mahajan/Micro-Hive /Images'
        base_path = '/Users/dipit.mahajan/Micro-Hive'
        file_name = 'paper' + str(number) + '.json'
        #file_path = f'{base_path}/{file_name}.json'
        # Open the file in write mode ('w') and write the JSON data
        with open(file_name, 'w') as file:
            json.dump(extracontent, file, indent=4)                                

        #connecting to data lake and storing json file. This will trigger lambda and store all information in DynamoDB
        connect_aws(file_name,file_name) 
        #dumping all the meta data and image files in seprate folder in data lake (s3)
        upload_folder(img_path)






        





















        
