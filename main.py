import itertools
import json
import requests
from datetime import datetime
import argparse


def main():
    parser = argparse.ArgumentParser(description='Process  API call parameters ')
    parser.add_argument('-l', '--location', action='store_true', default=False,
                        help='Display current location of the ISS')
    parser.add_argument('-p', '--people', action='store_true', default=False,
                        help='Display current members of the crew on board the ISS')
    parser.add_argument('-pt', '--passtime', nargs=2, type=float, metavar=('LAT', 'LONG'),
                        help='Display pass time for a given latitude and longitude of the ISS')

    args = parser.parse_args()

    if args.location:
        get_current_location()

    if args.people:
        get_crew_members()

    if args.passtime:
        get_pass_time(args.passtime[0], args.passtime[1])


def get_current_location():
    obj = try_fetch_data("http://api.open-notify.org/iss-now.json")

    time = datetime.utcfromtimestamp(obj['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    lat = obj['iss_position']['latitude']
    long = obj['iss_position']['longitude']

    print("The ISS current location at %s UTC is %s lat, %s long" % (time, lat, long))


def get_crew_members():
    obj = try_fetch_data("http://api.open-notify.org/astros.json")

    if obj:
        people = obj['people']

        print("People in the ISS:")

        for key, group in itertools.groupby(people, key=lambda x: x['craft']):
            print('CRAFT: %s' % key)
            for person in list(group):
                print("- %s " % person['name'])


def get_pass_time(lat, long):
    obj = try_fetch_data("http://api.open-notify.org/iss-pass.json?lat=%s&lon=%s" % (lat, long))

    if obj:
        times = obj['response']

        print("ISS will be seen on %s lat, %s long during this times: " % (lat, long))
        for time in times:
            date = datetime.utcfromtimestamp(time['risetime']).strftime('%Y-%m-%d %H:%M:%S')
            print("time: %s - duration: %s seconds" % (date, time['duration']))


def try_fetch_data(url):
    response = requests.get(url)

    obj = json.loads(response.content)

    if response.status_code != 200:
        print('%s: %s' % (obj['message'], obj['reason']))
        return None

    return obj


if __name__ == "__main__":
    main()


