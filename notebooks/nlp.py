import nltk
nltk.download('punkt_tab')      
nltk.download('wordnet')    
nltk.download('omw-1.4') 
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import stopwords   

lemmatizer = WordNetLemmatizer()

stop_words = set(stopwords.words('english'))

units = ["kg", "ml", "mg", "ph", "ng", "cm", "mm", "nm", "min", "cal", "kcal", "ppm", "ppb", "mm2", "mm3"]

def get_wordnet_pos(tag: str)->str:
    if tag.startswith('J'):  
        return 'a'
    elif tag.startswith('V'):  
        return 'v'
    elif tag.startswith('N'):  
        return 'n'
    elif tag.startswith('R'):  
        return 'r'
    else:
        return 'n'  

def lemmatize_text(text: str) -> str:
    lemmatized_text = []

    tokens = word_tokenize(text)
    tagged_tokens = pos_tag(tokens)
    for word, tag in tagged_tokens:
        lemmatized_text.append(lemmatizer.lemmatize(word, get_wordnet_pos(tag)))
    return (' '.join(lemmatized_text))

def preprocess_text(text: str, stop_words) -> str:
    text = lemmatize_text(text)
    text = text.lower()
    tokens = word_tokenize(text)
    filtered_tokens = [word for word in tokens if word.isalpha() and word not in stop_words and len(word) >1 and word not in units]
    return ' '.join(filtered_tokens)

def extract_nouns(sentence: str) -> list[str]:
    tokens = word_tokenize(sentence)
    tagged_tokens = pos_tag(tokens)

    nouns = [
        lemmatizer.lemmatize(word, 'n')
        for word, tag in tagged_tokens
        if tag.startswith('NN')
    ]

    return nouns

if __name__ == "__main__":
    sentence = "The children are running towards a better place."

    lemmatized_sentence = lemmatize_text(sentence)

    print("Original Sentence: ", sentence)
    print("Lemmatized Sentence: ", lemmatized_sentence)

    print("final text :", preprocess_text(sentence, stop_words))