import re     #Intial basic preprocessing -- To remove whitespaces and special characters
import spacy  # NLP machine learning library for Named Entity Relationship


class Reader :

    @staticmethod
    def clean_text(text):

        # Remove special characters and multiple whitespaces
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        text = re.sub(r'\s+', ' ', text)

        return text
    

    @staticmethod
    def clean_and_tokenize(text):
        #To tokenize and clean the data

        nlp = spacy.load('/Users/dipit.mahajan/anaconda3/lib/python3.11/site-packages/en_core_web_sm/en_core_web_sm-3.7.1')
        
        doc = nlp(text)
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)


