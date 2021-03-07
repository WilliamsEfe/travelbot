""" ChatBot
"""
from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.comparisons import levenshtein_distance
from chatterbot.trainers import ListTrainer
import nltk
import requests
import json

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
APP = Flask(__name__)

ENGLISH_BOT = ChatBot("Chatterbot",
                      storage_adapter='chatterbot.storage.MongoDatabaseAdapter',

                      database_uri='mongodb+srv://root:tcore@cluster0-otnor.mongodb.net/test?retryWrites=true&w=majority',
                      statement_comparison_function=levenshtein_distance,
                      filters=[
                          'chatterbot.filters.RepetitiveResponseFilter'],
                      preprocessors=[
                          'chatterbot.preprocessors.clean_whitespace'],
                      logic_adapters=[
                          {
                              'import_path': 'chatterbot.logic.BestMatch',
                              'threshold': 0.85,
                              'default_response': 'I am sorry, but I do not understand.'
                          }
                      ]
                      )

TRAINER = ChatterBotCorpusTrainer(ENGLISH_BOT)

# For training Custom corpus data
# TRAINER.train("./data/my_corpus/")

# For training English corpus data
# TRAINER.train('chatterbot.corpus.english')

# For training list of conversations
# TRAINER_LIST = ListTrainer(ENGLISH_BOT)
# TRAINER_LIST.train([
#     "How are you?",
#     "I am good.",
#     "That is good to hear.",
#     "Thank you",
#     "You are welcome.",
# ])


@APP.route("/")
def home():
    """
    Home
    """
    return render_template("index.html")


@APP.route("/get")
def get_bot_response():
    """
    Get reply from Bot
    """
    user_text = request.args.get('msg')
    if user_text == "yes":
        return "enter destination"
    # if user_text == "yes":
    #     return "enter your preferred destination"
    #     destination_city = request.args.get('msg')
    #     print("destination city is"+destination_city)
    #     if(1 == 1):

    #         return "enter your departure city"
    #     if(1 == 1):
    #         departure_city = request.args.get('msg')
    #         return "enter your preferred departure date"
    #     departure_date = request.args.get('msg')
    #     return "enter your preferred arrival date"
    #     arrival_date = request.args.get('msg')
    #     return "enter your preferred departure date"

    if user_text == "ttt":
        return comedy()
    #user_text = request.args.get('msg')
    # return user_text
    return str(ENGLISH_BOT.get_response(user_text))


def comedy():
    url = "http://www.ije-api.travelpro.com.ng/v1/flight/search-flight"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'cookie': 'J8JBNpPEVEjx3QA4zTpn'
    }
    myobj = {
        "header": {
            "cookie": ""
        },
        "body": {
            "origin_destinations": [{
                "departure_city": "LOS",
                "destination_city": "CAI",
                "departure_date": "02/23/2020",
                "return_date": "02/24/2020"
            }],
            "search_param": {
                "no_of_adult": 1,
                "no_of_child": 1,
                "no_of_infant": 0,
                "cabin": "All",
                "preferred_airline_code": "EK",
                "calendar": True
            }
        }
    }
    x = requests.post(url, data=json.dumps(myobj), headers=headers)

    # print(x.json())
    if x.status_code != 200:
        return "status=400"
    results = x.json()['body']['data']['itineraries']
    new_results = []
    for result in results:
        new_result = {}
        last_segment_arrival = result['origin_destinations'][0]['segments'][-1]['arrival']
        new_result['arrival_date'] = last_segment_arrival['date']
        new_result['arrival_time'] = last_segment_arrival['time']
        new_result['destination'] = last_segment_arrival['airport']['name']

        first_segment_departure = result['origin_destinations'][0]['segments'][0]['departure']
        new_result['departure_date'] = first_segment_departure['date']
        new_result['departure_time'] = first_segment_departure['time']
        new_result['departure_airport'] = first_segment_departure['airport']['name']

        new_result['airline'] = result['origin_destinations'][0]['segments'][0]['operating_airline']['name']

        new_result['price'] = str(result['pricing']['portal_fare']['total_fare']) + \
            result['pricing']['portal_fare']['currency']['code']
        new_result['cabin'] = result['cabin']['name']
        new_result['no_of_stops'] = len(
            result['origin_destinations'][0]['segments'])
        new_results.append(new_result)
        #print (new_results.length())
    return str(new_results[0:1])


if __name__ == "__main__":
    # APP.run()
    APP.run(debug=True)
