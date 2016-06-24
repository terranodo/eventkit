import requests


def register_service(base_url=None,
                     username='admin',
                     password="admin",
                     service_url=None,
                     service_name=None,
                     service_type="AUTO",
                     verify=True):

    base_url = base_url.rstrip('/')
    client = requests.session()
    URL = '{}/account/login'.format(base_url)
    client.get(URL, verify=False)
    csrftoken = client.cookies['csrftoken']
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/services/')
    response = client.post(URL, data=login_data, headers=dict(Referer=URL), verify=verify)

    url = '{}/services/register/'.format(base_url)
    client.get(url, verify=False)
    csrftoken = client.cookies['csrftoken']
    params = {"url": service_url,
            "name": service_name,
            "type": service_type,
            "csrfmiddlewaretoken":csrftoken}
    headers = {"X-CSRFToken": csrftoken, "Referer": url}
    response = client.post(url, data=params, headers=headers, verify=verify)
