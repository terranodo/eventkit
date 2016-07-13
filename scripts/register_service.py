import requests
import json


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


# def register_mapproxy_service(base_url=None,
#                               username='admin',
#                               password="admin",
#                               location=None,
#                               type=None,
#                               name=None,
#                               verify=True):
#     base_url = base_url.rstrip('/')
#     client = requests.session()
#     URL = '{}/account/login'.format(base_url)
#     client.get(URL, verify=False)
#     csrftoken = client.cookies['csrftoken']
#     login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/services/')
#     client.post(URL, data=login_data, headers=dict(Referer=URL), verify=verify)
#
#     url = '{}/eventkit/register'.format(base_url)
#     client.get(url, verify=verify)
#     csrftoken = client.cookies['csrftoken']
#     params = {"location": json.dumps(location),
#               "name": name,
#               "type": type,
#               "csrfmiddlewaretoken": csrftoken}
#     headers = {"X-CSRFToken": csrftoken, "Referer": url}
#     response = client.post(url, data=params, headers=headers, verify=verify)
#     # print(response.text)


def register_wms_service(base_url=None,
                     username='admin',
                     password="admin",
                     service_url=None,
                     service_name=None,
                     service_type="wms",
                     verify=True):
    base_url = base_url.rstrip('/')
    client = requests.session()
    URL = '{}/account/login'.format(base_url)
    client.get(URL, verify=verify)
    csrftoken = client.cookies['csrftoken']
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/eventkit/')
    client.post(URL, data=login_data, headers=dict(Referer=URL), verify=verify)

    url = '{}/eventkit/register'.format(base_url)
    client.get(url, verify=verify)
    csrftoken = client.cookies['csrftoken']
    params = {"service_url": service_url,
              "service_name": service_name,
              "service_type": service_type,
              "csrfmiddlewaretoken": csrftoken}
    headers = {"X-CSRFToken": csrftoken, "Referer": url}
    print("Registering: {}, {}, {}".format(service_url, service_name, service_type))
    response = client.post(url, data=params, headers=headers, verify=verify)


def register_voyager_services(base_url=None,
                         username='admin',
                         password="admin",
                         service_file=None,
                         voyager_base_url=None,
                         verify=True):

    base_url = base_url.rstrip('/')
    client = requests.session()
    URL = '{}/account/login'.format(base_url)
    client.get(URL, verify=verify)
    csrftoken = client.cookies['csrftoken']
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next='/eventkit/')
    client.post(URL, data=login_data, headers=dict(Referer=URL), verify=verify)

    url = '{}/eventkit/voyager'.format(base_url)
    client.get(url, verify=verify)
    csrftoken = client.cookies['csrftoken']
    params = {"service_file": service_file,
              "voyager_base_url": voyager_base_url,
              "csrfmiddlewaretoken": csrftoken}
    headers = {"X-CSRFToken": csrftoken, "Referer": url}
    response = client.post(url, data=params, headers=headers, verify=verify)