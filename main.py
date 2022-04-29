import requests
import os
from flask import Response

class Zendesk:
    subdomain = os.environ.get('ZENDESK_INSTANCE','')
    user_data = {'username': os.environ.get('ZENDESK_USERNAME',''), 'id': os.environ.get('ZENDESK_USERID','')}
    user = user_data['username'] + '/token'
    env_variable = 'ZENDESK_ACCESS_TOKEN'
    headers = {"Content-Type": "application/json"}

    def __init__(self, ticket_id):
        self.ticket_id = ticket_id
        self.api_url = self.subdomain + '/api/v2/tickets/' + ticket_id + '.json'
        self.auth = (self.user, self.__access_token())

    '''
    helper function for calling Zendesk api
    '''
    def __response_caller(self, method: str, type: str, *args, **kwargs) -> dict:
        try:
            response = requests[method](*args,**kwargs)
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {"error": f'There was an error fetching zendesk info for function {type}'}
        except:
            return {"error": "There was an error reaching zendesk api."}
    
    def __access_token(self) -> str:
        return os.environ.get(self.env_variable, 'Specified environment variable is not set.')
    
    def __get_ticket(self) -> dict:
        data = self.__response_caller('GET',"get_ticket",self.api_url, headers=self.headers,auth=self.auth)
        return data

    '''
    method to update a ticket with an internal or public note directly from a LookML action
    '''
    def add_comment(self, comment: str, public: bool) -> dict:
        json = {"ticket": {"comment":{"body":comment,"public": True if public == "public" else False}}}
        data = self.__response_caller('PUT', 'add_comment', self.api_url,headers=self.headers,json=json,auth=self.auth)
        return data
    
    '''
    method to update a ticket's status and optionally add an internal note directly from a LookML action
    '''
    def reopen_ticket(self, comment: str, status: str) -> dict:
        json = {"ticket": { "comment": {"body": comment,"public": False}, "status":status.lower()}}
        data = self.__response_caller('PUT', 'reopen_ticket', self.api_url,headers=self.headers,json=json,auth=self.auth)
        return data
    
    '''
    method to update a ticket's priority and based off of priority set any required tags and leave internal comment
    '''
    def set_priority(self, comment: str, priority: str, tags: str) -> dict:
        current_tags = self.__get_ticket()["ticket"]["tags"]
        new_tags = current_tags + tags.split(',')
        new_tags = [tag.strip() for tag in new_tags]
        json = {"ticket": { "comment": {"body": comment,"public": False}, "priority":priority.lower(), "tags":new_tags}} if priority.lower() == "high" else {"ticket": { "comment": {"body": comment,"public": False}, "priority":priority.lower()}}
        data = self.__response_caller('PUT', 'set_priority', self.api_url,headers=self.headers,json=json,auth=self.auth)
        return data
    
    '''
    method to update a ticket and set new tags, indicate that tags should be comma deliminated
    '''
    def set_tags(self,tags: str) -> dict:
        current_tags = self.get_ticket()["tags"]
        new_tags = current_tags + tags.split(',')
        json = {"ticket": {"tags":new_tags}}
        data = self.__response_caller('PUT', 'set_tags', self.api_url,headers=self.headers,json=json,auth=self.auth)
        return data
    
def run_ticket_update(request):
    """
    Zendesk
    """
    request_json = request.get_json()
    ticket_id = request_json["data"]["ticket_id"]
    zendesk_data = Zendesk(ticket_id)
    function_mapping = {
        "Add Comment": zendesk_data.add_comment,
        "Reopen Ticket": zendesk_data.reopen_ticket,
        "Set Priority": zendesk_data.set_priority
    }
    res = {}
    if request_json["form_params"]["function"] == "Add Comment":
        res = function_mapping["Add Comment"](request_json["form_params"]["comment"],request_json["form_params"]["public"])
    elif request_json["form_params"]["function"] == "Reopen Ticekt":
        res = function_mapping["Reopen Ticket"](request_json["form_params"]["comment"],request_json["form_params"]["status"])
    else:
        res = function_mapping["Set Priority"](request_json["form_params"]["comment"],request_json["form_params"]["priority"],request_json["form_params"]["tags"])
    print(res)
    return Response(res, status=200, mimetype='application/json')
