"""
This is a skill that uses various API's to supply film data for a location and date specified.
"""
# pylint: disable=C0103
# pylint: disable=R0201

import datetime as dt
import requests
from fuzzywuzzy import process

# change this from mykeys to keys

# --------------- Helper class that builds all of the responses ----------------------


class HelperClass(object):
    """ Helper class for building json responses """

    request_film = {}
    request_films = {}
    request_location = {}
    films = []
    showtimes = []
    session_attributes = {}

    def __init__(self):
        self.venue_id = ""
        self.imdb_rating = ""
        self.venue_name = ""
        self.film = ""

    def build_response(self, session_attributes, speechlet_response):
        """ builds json response """
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': speechlet_response
        }

    def build_speechlet_response(self, title, output, reprompt_text, should_end_session):
        """ builds speechlet response """
        return {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output
            },
            'card': {
                'type': 'Simple',
                'title': title,
                'content': output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_text
                }
            },
            'shouldEndSession': should_end_session
        }

    def get_venue_id(self, location):
        """" get venue id from api using location """
        self.request_location = requests.get(
            'http://moviesapi.herokuapp.com/cinemas/find/' + location).json()
        if self.request_location == []:
            self.venue_id = "10539"
        else:
            self.venue_id = self.request_location[0]['venue_id']

        return self.venue_id

    def get_films(self, venue_id, from_date):
        """ get venue id from api using location """
        self.request_films = requests.get(
            'http://findanyfilm.com/api/screenings/by_venue_id/venue_id/'
            + venue_id + "date_from/" + from_date).json()
        for movie_id in self.request_films[venue_id]['films']:
            self.films.append(self.request_films[venue_id]['films'][
                movie_id]['film_data']['film_title'])

        return self.films

    def get_imdb_rating(self, film):
        """ get venue imdb rating from api using name """
        self.request_film = requests.get('http://www.omdbapi.com/?t=' +
                                         film + '&y=&plot=short&r=json').json()
        try:
            self.imdb_rating = self.request_film['imdbRating']
        except:
            self.imdb_rating = "not availaible"

        return self.imdb_rating

    def get_showtimes(self, film, session):
        """ get showtimes api using name """
        films_json = session['attributes']['request_films'].values()[0]['films']

        for item in films_json:
            if film == films_json[item]['film_data']['film_title']:
                film_id = item
        for item in films_json[film_id]['showings']:
            self.showtimes.append(item['display_showtime'])

        return self.showtimes

# --------------- Class that control the skill's behavior ------------------


class IntentsClass(HelperClass):
    """ intents class """

    def __init__(self):
        super(IntentsClass, self).__init__()

    def whats_playing_intent(self, intent, session):
        """ Gets the values from the session and prepares the speech to reply to the
        user.
        """

        should_end_session = False

        if 'value' in intent['slots']['location']:
            location = intent['slots']['location']['value']
            if 'value' in intent['slots']['date']:
                from_date = intent['slots']['date']['value']
            else:
                from_date = dt.datetime.today().strftime("%Y-%m-%d")
            self.venue_id = Helper.get_venue_id(location)
            self.films = Helper.get_films(self.venue_id, from_date)
            self.venue_name = Helper.request_films[self.venue_id]['name']
            card_title = self.venue_name
            speech_output = "Films showing at %s on the %s are: %s. Which movie would you like to know more about?" % (
                self.venue_name, from_date, ', '.join(self.films))
            reprompt_text = "Which movie would you like to know more about?"
        else:
            speech_output = "I'm not sure what you would like to do. " \
                            "Please try again."
            reprompt_text = "I'm not sure what you would like to do."

        self.session_attributes.update(
            {"films": self.films, "request_films": Helper.request_films})
        speechlet_response = Helper.build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session)
        return Helper.build_response(self.session_attributes, speechlet_response)

    def more_information_intent(self, intent, session):
        """ Gets the values from the session and prepares the speech to reply to the
        user.
        """

        should_end_session = True

        if 'value' in intent['slots']['film']:
            try:
                self.film = process.extractOne(intent['slots']['film']['value'], session[
                    'attributes']['films'])[0]
                self.showtimes = ', '.join(Helper.get_showtimes(self.film, session))
            except:
                self.film = intent['slots']['film']['value']
                self.showtimes = "not available"

            self.imdb_rating = Helper.get_imdb_rating(self.film)
            card_title = self.film
            speech_output = "%s has an I.M.D.B rating of %s. The show times for this movie are %s " % (
                self.film, self.imdb_rating, self.showtimes)
            reprompt_text = "Would you like to book this film?"
        else:
            speech_output = "I'm not sure what you would like to do. " \
                            "Please try again."
            reprompt_text = "I'm not sure what you would like to do."

        speechlet_response = Helper.build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session)
        return Helper.build_response(self.session_attributes, speechlet_response)

    def welcome_response(self):
        """ If we wanted to initialize the session to have some attributes we could
        add those here
        """

        card_title = "Welcome"
        speech_output = "Welcome to film finder. " \
                        "To get cinema listings please ask: whats playing in , location , on the , date. " \
                        "Alternativley, to get a movie rating please state the name of a movie."
        # If the user either does not reply to the welcome message or says something
        # that is not understood, they will be prompted again with this text.
        reprompt_text = "To get cinema listings please ask: whats playing in , location , on the , date. " \
                        "Alternativley, to get a movie rating please state the name of a movie."
        should_end_session = False
        speechlet_response = Helper.build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session)
        return Helper.build_response(self.session_attributes, speechlet_response)

    def help_response(self):
        """ If we wanted to initialize the session to have some attributes we could
        add those here
        """
        card_title = "Help"
        speech_output = "Welcome to film finder. " \
                        "To get cinema listings please ask: whats playing in , location , on the , date. " \
                        "Alternativley, to get a movie rating please state the name of a movie."
        # If the user either does not reply to the welcome message or says something
        # that is not understood, they will be prompted again with this text.
        reprompt_text = "To get cinema listings please ask: whats playing in , location , on the , date. " \
                        "Alternativley, to get a movie rating please state the name of a movie."
        should_end_session = False
        speechlet_response = Helper.build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session)
        return Helper.build_response(self.session_attributes, speechlet_response)

    # def amazon_yes_intent():

    # def amazon_no_intent():

    def handle_session_end_request(self):
        """ Called when session end request recieved """
        card_title = "Session Ended"
        speech_output = "Thank you for trying find any film..." \
                        "Have a nice day!"
        # Setting this to true ends the session and exits the skill.
        should_end_session = True
        speechlet_response = Helper.build_speechlet_response(
            card_title, speech_output, None, should_end_session)
        return Helper.build_response({}, speechlet_response)

# --------------- Secondary handlers ------------------

Helper = HelperClass()
Intents = IntentsClass()


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return Intents.welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "whatsPlayingIntent":
        return Intents.whats_playing_intent(intent, session)
    elif intent_name == "moreInformationIntent":
        return Intents.more_information_intent(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return Intents.help_response()
    # elif intent_name == "AMAZON.YesIntent":
    #     return amazon_yes_intent()
    # elif intent_name == "AMAZON.NoIntent":
    #     return amazon_no_intent()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return Intents.handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
#    from mykeys import alexa_skill_id
#
#    if event['session']['application']['applicationId'] != \
#            alexa_skill_id:
#        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
