import requests
import pandas as pd
import json
from core import settings_confidential as confidentials

API_SESSION_ENDPOINT = "https://kraken.picasso-utc.fr/api/auth/badge?full=true"
API_BLOCK_ENDPOINT = "https://kraken.picasso-utc.fr/api/blocked/users/"
BADGE_ID = ''

# A MODIFIER AVEC VOS VALEURS !!!!
PATH_TO_EXCEL_FILE = ''
LOGIN = ''
PIN = ''
GINGER_KEY = confidentials.GINGER_KEY
REASON = "Campagne d'integration P20"


def get_info_from_login(r, login):
    get_uid_user_response = r.request(method="GET",
                                      url='https://assos.utc.fr/ginger/v1/' + login + "?key=" + GINGER_KEY)

    if get_uid_user_response.status_code == 200:
        return get_uid_user_response.json()
    else:
        print(get_uid_user_response.reason)
        return None


# creer la session pour avoir l'acces a l'api
def create_session():
    r = requests.session()
    infos = get_info_from_login(r, LOGIN)
    BADGE_ID = infos['badge_uid']
    credentials = {'badge_id': BADGE_ID, 'pin': PIN}
    api_response = r.request(method="POST", url=API_SESSION_ENDPOINT, data=credentials)
    response = {
        'data': api_response.reason,
        'status': api_response.status_code
    }
    print(response)
    return r


# on met sous forme de liste la colonne login et on enleve les duplicates
def read_logins():
    X = pd.read_excel(PATH_TO_EXCEL_FILE)
    return list(dict.fromkeys(X['login'].to_list()))


def block_users(r, list_of_logins_to_block):
    for login in list_of_logins_to_block:
        api_response2 = r.request(method="POST", url=API_BLOCK_ENDPOINT, data={'login': login, 'justification': REASON})
        response2 = {
            'data': api_response2.reason,
            'status': api_response2.status_code
        }
        print("response pour le login: " + login, response2)


def unblock_users(r, list_of_logins_to_unblock):
    get_blocked_users_response = r.request(method="GET", url=API_BLOCK_ENDPOINT)
    blocked_users = get_blocked_users_response.json()['blocked_users']

    for login in list_of_logins_to_unblock:
        get_uid_user_response = r.request(method="GET",
                                          url='https://assos.utc.fr/ginger/v1/' + login + "?key=" + GINGER_KEY)

        user_response = get_uid_user_response.json()
        if user_response['badge_uid']:
            uid_user = user_response['badge_uid']
        else:
            uid_user = ''

        user_to_block = [d for d in blocked_users if d['badge_uid'] == uid_user]
        if len(user_to_block) > 0:
            id = user_to_block[0]['id']
            delete_user_response = r.request(method="DELETE", url=API_BLOCK_ENDPOINT + str(id) + "/", )
            response_delete = {
                'data': delete_user_response.reason,
                'status': delete_user_response.status_code
            }
            print("response pour le login: " + login, response_delete)
        else:
            print("cet utilisateur n'etait pas bloque : " + login)


def main():
    session = create_session()
    list_of_logins = read_logins()
    block_users(session, list_of_logins)
    # unblock_users(session, list_of_logins)


main()
