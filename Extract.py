import PyPDF2                                               # To read the PDF
from pdfminer.high_level import extract_pages, extract_text # To analyze the PDF layout and extract text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import pdfplumber                                           # To extract text from tables in PDF
from PIL import Image                                       # To extract the images from the PDFs
from pdf2image import convert_from_path
import pytesseract                                          # To perform OCR to extract text from images 
import os                                                   # To remove the additional created files
from operator import itemgetter
import fitz
import json

import re


class Extract :
    
    # Create function to extract text
    def text_extraction(self,element):                                               # New commit put old file that didn't have self keyword                                           
        # Extracting the text from the in line text element
        line_text = element.get_text()
        
        # Find the formats of the text
        # Initialize the list with all the formats appeared in the line of text
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Iterating through each character in the line of text
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Append the font name of the character
                        line_formats.append(character.fontname)
                        # Append the font size of the character
                        line_formats.append(character.size)
        # Find the unique font sizes and names in the line
        format_per_line = list(set(line_formats))
        
        # Return a tuple with the text in each line along with its format
        return (line_text, format_per_line)



    # Extracting tables from the page
    
    def extract_table(self, pdf_path, page_num, table_num):
        # Open the pdf file
        pdf = pdfplumber.open(pdf_path)
        # Find the examined page
        table_page = pdf.pages[page_num]
        # Extract the appropriate table
        table = table_page.extract_tables()[table_num]
        
        return table

    # Convert table into appropriate fromat
    
    def table_converter(self, table):
        table_string = ''
        # Iterate through each row of the table
        for row_num in range(len(table)):
            row = table[row_num]
            # Remove the line breaker from the wrapted texts
            cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
            # Convert the table into a string 
            table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
        # Removing the last line break
        table_string = table_string[:-1]
        return table_string

    # Create a function to check if the element is in any tables present in the page
    
    def is_element_inside_any_table(self, element, page ,tables):
        x0, y0up, x1, y1up = element.bbox
        # Change the cordinates because the pdfminer counts from the botton to top of the page
        y0 = page.bbox[3] - y1up
        y1 = page.bbox[3] - y0up
        for table in tables:
            tx0, ty0, tx1, ty1 = table.bbox
            if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
                return True
        return False

    # Function to find the table for a given element
    
    def find_table_for_element(self, element, page ,tables):
        x0, y0up, x1, y1up = element.bbox
        # Change the cordinates because the pdfminer counts from the botton to top of the page
        y0 = page.bbox[3] - y1up
        y1 = page.bbox[3] - y0up
        for i, table in enumerate(tables):
            tx0, ty0, tx1, ty1 = table.bbox
            if tx0 <= x0 <= x1 <= tx1 and ty0 <= y0 <= y1 <= ty1:
                return i  # Return the index of the table
        return None  


    # Create a function to crop the image elements from PDFs
    
    def crop_image(self, element, pageObj, pagenum):
        # Get the coordinates to crop the image from PDF
        [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
        # Crop the page using coordinates (left, bottom, right, top)
        pageObj.mediabox.lower_left = (image_left, image_bottom)
        pageObj.mediabox.upper_right = (image_right, image_top)
        # Save the cropped page to a new PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(pageObj)
        # Save the cropped PDF to a new file
        with open('cropped_image_'+ str(pagenum)+'.pdf', 'wb') as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

    # Create a function to convert the PDF to images
    def convert_to_images(self, input_file,pagenum):
        images = convert_from_path(input_file)
        image = images[0]
        output_file = 'PDF_image' + str(pagenum)+ '.png'
        image.save('/Users/dipit.mahajan/Micro-Hive /Images/' + str(output_file), 'PNG')

    # Create a function to read text from images
    def image_to_text(self, image_path):
        # Read the image
        img = Image.open(image_path)
        # Extract the text from the image
        text = pytesseract.image_to_string(img)
        return text
    

    def fonts(self, doc, granularity=False):
        """Extracts fonts and their usage in PDF documents."""
        styles = {}
        font_counts = {}

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b['type'] == 0:  # block contains text
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if granularity:
                                identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                                styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                    'color': s['color']}
                            else:
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {'size': s['size'], 'font': s['font']}

                            font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

        font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

        if len(font_counts) < 1:
            raise ValueError("Zero discriminating fonts found!")

        return font_counts, styles


    def font_tags(self, font_counts, styles):
        """Returns dictionary with font sizes as keys and tags as value."""
        p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
        p_size = p_style['size']  # get the paragraph's size

        # sorting the font sizes high to low, so that we can append the right integer to each tag
        font_sizes = []
        for (font_size, count) in font_counts:
            font_sizes.append(float(font_size))
        font_sizes.sort(reverse=True)

        # aggregating the tags for each font size
        idx = 0
        size_tag = {}
        for size in font_sizes:
            idx += 1
            if size == p_size:
                idx = 0
                size_tag[size] = '<p>'
            if size > p_size:
                size_tag[size] = '<h{0}>'.format(idx)
            elif size < p_size:
                size_tag[size] = '<s{0}>'.format(idx)

        return size_tag








