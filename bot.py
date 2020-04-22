import string
import re
import json
import Levenshtein as lev
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
import random
import logging

logFormatter = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.NOTSET,
    format=logFormatter, 
    handlers=[logging.StreamHandler()])
logging.root.setLevel(logging.NOTSET)
logger = logging.getLogger(__name__)

nltk.download('stopwords')
sw = stopwords.words('english')  
protection_words = "Regularly and thoroughly clean your hands with an alcohol-based hand rub or wash them with soap and water.\nAvoid touching eyes, nose and mouth.\nStay home if you feel unwell.\nMaintain at least 1 metre (3 feet) distance between yourself and anyone who is coughing or sneezing"

medical_attention_words = "If you develop emergency warning signs for COVID-19 get medical attention immediately. Emergency warning signs include fever, cough, trouble breathing, persistent pain or pressure in the chest, new confusion or inability to arouse, bluish lips or face"

with open("corona-questions.txt", 'r') as f:
    mystring = f.read()
questions = mystring.split("`")

with open("corona-answers.txt", 'r') as f:
    mystring = f.read()
answers = mystring.split("`")

# This is for generating a random question each time your question isn't valid
short_questions = [q for q in questions if len(q) < 65]

def clean_string(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in sw])
    return text

cleaned = list(map(clean_string, questions))
vectoriser = CountVectorizer(cleaned)
question_vectors = vectoriser.fit_transform(cleaned[:]).toarray()

def get_generic_answer():
    return "Sorry, we are unable to answer that question.\n\nTry asking a different question. For example: {0}".format(short_questions[random.randint(0,len(short_questions)-1)])

# https://towardsdatascience.com/calculating-string-similarity-in-python-276e18a7d33a

def cosine_sim_vectors(vec1, vec2):
    vec1 = vec1.reshape(1,-1)
    vec2 = vec2.reshape(1,-1)
    
    return cosine_similarity(vec1, vec2)[0][0]

def get_max_value(input_q):
    ratios = [lev.ratio(input_q, clean_text(q)) for q in questions]

    input_vector = vectoriser.transform([input_q])
    cosine_sim = [cosine_sim_vectors(input_vector[0], q) for q in question_vectors]

    max_value_c = max(cosine_sim)
    max_index_c = cosine_sim.index(max_value_c)
    max_value_r = max(ratios)
    max_index_r = ratios.index(max_value_r)

    logger.debug(f"cosine: val {max_value_c}, index {max_index_c}, question {questions[max_index_c]}")
    logger.debug(f"levenshtein ratio: val {max_value_r}, index {max_index_r}, question {questions[max_index_r]}")

    if max_value_c > max_value_r:
        return (max_value_c, max_index_c)
    else:
        return (max_value_r, max_index_r)

def clean_text(txt):
    return ''.join(txt.lower().strip().replace(".","").replace(",",""))


def handle_query(input_q):
    logger.info(f"Question asked: {input_q}")

    # Take care of these first
    if any([w in input_q for w in ["handwash", "wash my hands", "washing my hands", "wash hands", "washing hands", "handwashing", "wash hand", "hand wash"]]):
        logger.debug("Returning answer for question related to handwashing")
        return(answers[69])
    elif any([w in input_q for w in ["get testing", "get tested", "get test", "get a test" ]]):
        logger.debug("Returning answer for question related to testing")
        return('.'.join(answers[79].split('.')[:2]))
    elif any([w in input_q for w in ["symptom", "symptoms"]]):
        logger.debug("Returning answer for question related to symptoms")
        return('.'.join(answers[2].split('.')[:4]))
    elif any([w in input_q for w in ["medical attention", "doctor"]]):
        logger.debug("Returning answer for question related to medical attention")
        return(medical_attention_words)

    input_q = input_q.replace("covid 19", "covid-19")

    max_value, max_index = get_max_value(input_q)

    logger.debug(f"Closest question: {questions[max_index]}")
    ans = answers[max_index]

    # bad protection answer
    if max_index == 46 or max_index==114:
        return(protection_words)

    if max_value < 0.7:
        logger.debug(f"Similarity index {max_value} is less than 0.7. Doing manual checking")

        if any([w in input_q for w in ["protection", "protect", "precaution", "precautionary", "prevent", "prevention"]]):
            ans = protection_words
        elif any([w in input_q for w in ["mask", "masks"]]):
            if ("children" in input_q): ans = answers[56]
            else: ans = answers[12]
        elif ("quarantine" in input_q):
            ans = answers[37]
        elif any([w in input_q for w in ["vaccine", "treatment"]]):
            ans = answers[10]
        elif any([w in input_q for w in ["pet", "pets"]]):
            ans = '.'.join(answers[16].split(';')[:1]) + '. ' + '.'.join(answers[99].split('.')[:1])
        elif any([w in input_q for w in ["animal", "animals"]]):
            ans = answers[15]        
        elif "vodka" in input_q:
            ans = answers[203]
        elif "antibiotics" in input_q:
            ans = answers[8]
        elif "essential worker" in input_q:
            ans = answers[122]
        elif "diagnose" in input_q:
            ans = answers[81]
        elif "hand sanitizer" in input_q:
            ans = answers[71]
        elif "donate blood" in input_q:
            ans = answers[50]
        elif any([w in input_q for w in ["occur", "start", "begin"]]):
            ans = answers[21]
        else:
            logger.warning(f"BOT: No good question match for question {input_q}")
            ans = get_generic_answer()
    # Truncate to under 320 character (1 SMS is 160 characters)

    num_sentences = ans.count('.')
    while len(ans) > 320:
        # print(len(ans), num_sentences)
        ans = '.'.join(ans.split('.')[:num_sentences])
        num_sentences -= 1

    if not ans or len(ans) < 1:
        ans = get_generic_answer()

    return(ans)


