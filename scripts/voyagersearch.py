import requests
import csv
import getopt
import sys


def get_record(data_id, base_url):
    request_url = base_url.rstrip('/') + '/api/rest/index/record/{}'.format(data_id)
    req = requests.get(request_url)
    if req.status_code == 200:
        return req.json()
    else:
        return None


def read_voyager_cart(cart_file):
    id_list = []
    with open(cart_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            id_list.append(row['id'])
    return id_list


def export_voyager_data(file_path, base_url):
    ids = read_voyager_cart(file_path)
    if not ids:
        print("No ID values found in file")
        quit()
    for data_id in ids:
        record = get_record(data_id, base_url)
        if record:
            format = record.get('format')
            title = record.get('title')
            # if record.get('rest_endpoint'):
            #     endpoint = record.get('rest_endpoint')
            # else:
            endpoint = record.get('path')
            print('ID: {}\n'.format(data_id)
                  + 'Title: {}\n'.format(title)
                  + 'Format: {}\n'.format(format)
                  + 'Endpoint: {}\n'.format(endpoint))
        else:
            print("Could not find record for ID: {}".format(data_id))


def usage():
    print('--file or -f: (required) The path of the voyager export csv file')

try:
    options, remainder = getopt.getopt(
        sys.argv[1:], 'f:u:h', ['file=', 'baseurl=', 'help'])
except getopt.GetoptError as err:
    print (err)
    quit()

file_path = None
baseurl = None

for opt, arg in options:
    if opt in ('-f', '--file'):
        file_path = arg
    elif opt in ('-u', '--baseurl'):
        baseurl = arg
    elif opt in ('-h', '--help'):
        usage()
        quit()

if baseurl and file_path:
    export_voyager_data(file_path)
