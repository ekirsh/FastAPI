import requests
import json
import sys


def convert_string(string):
    # Remove spaces from the string
    string = string.replace(" ", "")
    # Convert the string to lowercase
    string = string.lower()
    return string

def extract_team_members(data):
    companies = []
    for company_data in data:
        company_name = company_data['company']['name']
        people = []
        for team in company_data['team']:
            for person in team['people']:
                people.append({'company_name': company_name, 'name': person['name']})
        companies.append({'company_name': company_name, 'people': people})
    return companies

def format_data(data, name):
    output = []
    for item in data:
        if item['people']:
            if item['people'][0]['name'] != item['company_name']:
                output.append(f"{name} is managed by {item['people'][0]['name']} at {item['company_name']}.")
            else:
           	    output.append(f"{name} is managed by {item['people'][0]['name']} at their own company.")
        else:
            output.append(f"{name} is managed by {item['company_name']}.")
    return output

def format_data_pub(data, name):
    output = []
    for item in data:
        if item['people']:
            if item['people'][0]['name'] != item['company_name']:
                output.append(f"{name} is published by {item['people'][0]['name']} at {item['company_name']}.")
            else:
           	    output.append(f"{name} is published by {item['people'][0]['name']} at their own company.")
        else:
            output.append(f"{name} is published by {item['company_name']}.")
    return output



def find_info(cc):
    print('FIND INFO')
    managment_company = cc
    print(managment_company)
    managment_path = convert_string(managment_company)
    managment_path = ''.join(e for e in managment_path if e.isalnum())

    url = f'https://www.rostr.cc/api/v1/entity/{managment_path}'
    url2 = f'https://www.rostr.cc/api/v1/artist/{managment_path}/team/publisher'
    url3 = f'https://www.rostr.cc/api/v1/artist/{managment_path}/team/management'

    headers = {
        "cookie": "rostr-user-cookie=%7B%22userID%22%3A%22ff4sA1GrUbNNADb6tfQYhP%22%2C%22name%22%3A%22Ezra%20Kirsh%22%2C%22email%22%3A%22ezkirsh%40gmail.com%22%7D; rack.session=BAh7CEkiD3Nlc3Npb25faWQGOgZFVG86HVJhY2s6OlNlc3Npb246OlNlc3Npb25JZAY6D0BwdWJsaWNfaWRJIkU2OGE3ODNjZTE1NWRhNzlkZGNlNmE1MzY5OWIxNmQxNzlkYzYxOWE4ZGIxZDE3MTg2MjJiNWNkY2YzYjU2ZDFkBjsARkkiHHdhcmRlbi51c2VyLmRlZmF1bHQua2V5BjsAVEkiG2ZmNHNBMUdyVWJOTkFEYjZ0ZlFZaFAGOwBUSSIKZmxhc2gGOwBGewA%3D--66d2b435e7937a2a26113ccf79539aacc55bb555; mp_b303fbb5-7ceb-4ca5-a6f5-2c8bb777d6d7_perfalytics=%7B%22distinct_id%22%3A%20%22ff4sA1GrUbNNADb6tfQYhP%22%2C%22%24device_id%22%3A%20%221865be3903a1304-0446b3b339203c8-49193201-1fa400-1865be3903b1478%22%2C%22__user_props%22%3A%20%7B%22avatar%22%3A%20%22null%22%2C%22company%20name%22%3A%20%22EJK%22%2C%22email%22%3A%20%22ezkirsh%40gmail.com%22%2C%22name%22%3A%20%22Ezra%20Kirsh%22%2C%22firstName%22%3A%20%22Ezra%22%2C%22lastName%22%3A%20%22Kirsh%22%2C%22Group%20ID%22%3A%20%22gmail.com%22%2C%22signup%20date%22%3A%20%222023-02-16T21%3A34%3A45%2B00%3A00%22%2C%22first%20login%20date%22%3A%20%222023-02-16T21%3A34%3A45%2B00%3A00%22%2C%22pro%20enabled%22%3A%20true%2C%22account%20type%22%3A%20%22rostr%22%2C%22roadie%20enabled%22%3A%20false%7D%2C%22__last_event_time%22%3A%201682975959894%2C%22%24session_id%22%3A%20%22187d90ad732c5c-0f8ba7c94d50df-49193201-1ea000-187d90ad733f7d%22%2C%22__initial_utm_props_set%22%3A%20true%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__group_props%22%3A%20%7B%22name%22%3A%20%22EJK%22%2C%22teamName%22%3A%20%22Invdividual%20Subscription%22%7D%2C%22%24pageview_id%22%3A%20%22187d92e3789508-097be13f4c933f8-49193201-1ea000-187d92e378a169c%22%2C%22Group%20ID%22%3A%20%22gmail.com%22%2C%22%24user_id%22%3A%20%22ff4sA1GrUbNNADb6tfQYhP%22%2C%22__group_id%22%3A%20%22gmail.com%22%2C%22__first_pageview_in_session_has_occurred%22%3A%20true%2C%22__first_pageview_occurred%22%3A%20true%2C%22__last_pageview_time%22%3A%201682975897483%7D"
    }

    response = requests.get(url, headers=headers)
    response_content = response.content
    json_response = json.loads(response_content.decode('utf-8'))
    print(json_response)

    try:
        if json_response['entities'][0]['role'] == "MANAGER":
            managment_path = managment_path + "0"
            url2 = f'https://www.rostr.cc/api/v1/artist/{managment_path}/team/publisher'
            url3 = f'https://www.rostr.cc/api/v1/artist/{managment_path}/team/management'
    except:
        return "NA"

    response = requests.get(url2, headers=headers)
    response_content = response.content

    json_response = json.loads(response_content.decode('utf-8'))
    if json_response == {'msg': 'No objects were returned for this request.'}:
        print("NOT FOUND")
        return "NA"
    else:
        team = extract_team_members(json_response)
        yut = format_data_pub(team, managment_company)

        response = requests.get(url3, headers=headers)
        response_content = response.content

        json_response = json.loads(response_content.decode('utf-8'))
        #print(json_response)
        team = extract_team_members(json_response)
        yup = format_data(team, managment_company)
        return {'pub': yut, 'mgmt': yup}

