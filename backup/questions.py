import time
from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import requests
import string
import re
import json
import entity_names as en
from bs4 import BeautifulSoup
from requests import get
import Levenshtein as lev
import string
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
nltk.download('stopwords')
sw = stopwords.words('english')  

# # https://towardsdatascience.com/calculating-string-similarity-in-python-276e18a7d33a

def clean_string(text):
    text = ''.join([word for word in text if word not in string.punctuation])
    text = text.lower()
    text = ' '.join([word for word in text.split() if word not in sw])
    return text

def cosine_sim_vectors(vec1, vec2):
    vec1 = vec1.reshape(1,-1)
    vec2 = vec2.reshape(1,-1)
    
    return cosine_similarity(vec1, vec2)[0][0]

def get_questions():
    who_q, who_a = get_who_questions()
    cdc_q, cdc_a = get_cdc_questions()
    fda_q, fda_a = get_fda_questions()
    jhm_q, jhm_a = get_jhm_questions()
    cnn_q, cnn_a = get_cnn_questions()
    questions = who_q + cdc_q + fda_q + jhm_q + cnn_q
    answers = who_a + cdc_a + fda_a + jhm_a + cnn_a
    print(len(answers), len(questions))
    return (questions, answers)

def get_cnn_questions():
    # Scraping from CNN FAQ
    url = 'https://www.cnn.com/interactive/2020/health/coronavirus-questions-answers/'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    questions = html_soup.find_all('div', class_='question-q')
    questions = [q.text.strip().replace('\x99','').replace('\x80','').replace('â',"'") for q in questions]

    answers = html_soup.find_all('div', class_='question-a')
    answers = [a.text.strip().replace('\x99','').replace('\x80','').replace('\x93','').replace('\x94','').replace('â',"'").replace('\x9c','').replace('\x9d','') for a in answers]

    return (questions, answers)


def get_jhm_questions():
    # Scraping from Johns Hopkins Medicine
    url = 'https://www.hopkinsmedicine.org/health/conditions-and-diseases/coronavirus/coronavirus-frequently-asked-questions'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    questions = []
    answers = []

    for header in html_soup.find_all('h3'):
        para = header.find_next_sibling('p')
        questions.append(header.text.strip())
        if para:
            answers.append(para.text.strip().replace('\n',' ').replace('\xa0',''))
            
    questions = questions[:-3]

    return (questions, answers)

def get_fda_questions():
    # Scraping from FDA
    url = 'https://www.fda.gov/emergency-preparedness-and-response/coronavirus-disease-2019-covid-19/coronavirus-disease-2019-covid-19-frequently-asked-questions'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    questions = html_soup.find_all('div', class_ = 'panel-heading')
    questions = [q.text.strip().replace('Q: ','').replace('Q. ','') for q in questions]

    answers = html_soup.find_all('div', class_ = 'panel-body')
    answers = [a.text.strip().replace('A: ','').replace('A. ','').replace('\xa0', '').replace('A:','') for a in answers]

    return (questions, answers)


def get_cdc_questions():
    # Scraping from CDC
    url = 'https://www.cdc.gov/coronavirus/2019-ncov/faq.html'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    questions = html_soup.find_all('button', class_ = 'card-title btn btn-link')
    questions = [q.text for q in questions]

    answers = html_soup.find_all('div', class_ = 'collapse')
    answers = [a.text for a in answers]
    answers.pop(0)

    return (questions, answers)

def get_who_questions():
    # Scraping from WHO
    url = 'https://www.who.int/news-room/q-a-detail/q-a-coronaviruses'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')

    questions = html_soup.find_all('a', class_ = 'sf-accordion__link')
    questions = [' '.join(q.text.split()) for q in questions]

    answers = html_soup.find_all('p', class_ = 'sf-accordion__summary')
    answers = [' '.join(q.text.split()) for q in answers]

    return (questions, answers)

def clean_text(txt):
    return ''.join(txt.lower().strip().replace(".","").replace(",",""))


# questions, answers = get_questions()

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """ Get the incoming message the user sent our Twilio number """
    resp = MessagingResponse()

    with open("corona-questions.txt", 'r') as f:
        mystring = f.read()
    questions = mystring.split("`")

    with open("corona-answers.txt", 'r') as f:
        mystring = f.read()
    answers = mystring.split("`")

    # questions, answers = get_questions()

    body = request.values.get('Body', None)
    input_q = clean_text(body)


    if "cases in" in input_q:
        regexp = re.compile("cases in(.*)$")
        case_search = regexp.search(input_q).group(1)
        print (len(case_search) )
        print("You wanted cases in", case_search)



    cleaned = list(map(clean_string, questions))
    vectoriser = CountVectorizer(cleaned)
    question_vectors = vectoriser.fit_transform(cleaned[:]).toarray()
    question_vectors.shape
    #  vectoriser.vocabulary_

    print("Question asked", input_q)
    ratios = [lev.ratio(input_q, q) for q in questions]
    input_vector = vectoriser.transform([input_q])
    cosine_sim = [cosine_sim_vectors(input_vector[0], q) for q in question_vectors]

    max_value_c = max(cosine_sim)
    max_index_c = cosine_sim.index(max_value_c)
    max_value_r = max(ratios)
    max_index_r = ratios.index(max_value_r)

    print("cosine", max_value_c, max_index_c, questions[max_index_c])
    print("\nratio", max_value_r, max_index_r, questions[max_index_r])
    

    if max_value_c > max_value_r:
        max_value = max_value_c
        max_index = max_index_c
    else:
        max_value = max_value_r
        max_index = max_index_r

    print("Max value and index", max_value, max_index)
    print("Closest question:", questions[max_index])
    ans = answers[max_index]


    if max_value < 0.7:
        if ("symptoms" in input_q):
            ans = answers[2]
        elif any([w in input_q for w in ["mask", "masks", "protection"]]):
            if ("children" in input_q): ans = answers[56]
            else: ans = answers[12]
        elif ("quarantine" in input_q):
            ans = answers[37]
        elif any([w in input_q for w in ["vaccine", "treatment"]]):
            ans = answers[10]
        elif any([w in input_q for w in ["pet", "pets"]]):
            ans = answers[16]
        elif any([w in input_q for w in ["animal", "animals"]]):
            ans = answers[15]        
        elif "vodka" in input_q:
            ans = answers[203]
        elif "antibiotics" in input_q:
            ans = answers[8]
        elif "prevent" in input_q:
            ans = answers[114]
        elif "essential worker" in input_q:
            ans = answers[122]
        elif "diagnose" in input_q:
            ans = answers[81]
        elif "hand sanitizer" in input_q:
            ans = answers[71]
        elif "donate blood" in input_q:
            ans = answers[50]
        elif any([w in input_q for w in ["handwash", "wash my hands", "wash hands", "washing hands", "handwashing", "wash hand", "hand wash"]]):
            print(answers[69])
        else:
            ans = "Sorry, we are unable to answer that question yet. \nTry asking a different question. For example: 'What is a coronavirus?'"

    # Truncate to under 320 character (1 SMS is 160 characters)
    num_sentences = ans.count('.')
    while len(ans) > 320:
        # print(len(ans), num_sentences)
        ans = '.'.join(ans.split('.')[:num_sentences])
        num_sentences -= 1

    print("Answer:", ans)
    print(len(ans), num_sentences)

    resp.message(ans)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)




