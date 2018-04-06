from mailchimp3 import MailChimp
import requests
from urllib3.exceptions import HTTPError

class MailchimpException(Exception):
    pass

class MailchimpClient():
    client = None
    unregistered_list_id = None
    registered_list_id = None


    def set_credentials(self, username: str, key: str):
        self.client = MailChimp(username, key)


    def set_unregistered_list_id(self, list_id: str):
        self.unregistered_list_id = list_id


    def set_registered_list_id(self, list_id: str):
        self.registered_list_id = list_id


    def add_or_update_user(self, 
            email: str, 
            is_registered: bool = False,
            status: str = 'subscribed',
            first_name: str = '', 
            last_name: str = ''):
        '''
        add a new subscriber to mailchimp
        if subscriber already exists, do not throw error.
        '''

        list_id = self.registered_list_id \
            if is_registered == True \
            else self.unregistered_list_id
        
        try:
            self.client.lists.members.create_or_update(list_id, email, {
                'email_address': email,
                'status_if_new': 'subscribed',
                'status': status,
                'merge_fields': {
                    'FNAME': first_name,
                    'LNAME': last_name
                },
            })

        except KeyError as e:
            raise e

        except Exception as e:
            if e.response.status_code == 400:
                json = e.response.json()
                raise MailchimpException( \
                        json.get('errors') \
                        or json.get('title') \
                        or json.get('detail') \
                        or json)
            else:
                raise     


mc = MailchimpClient()
