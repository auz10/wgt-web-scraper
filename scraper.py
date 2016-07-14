# -*- coding: utf-8 -*-
import requests
import json
import itertools
from bs4 import BeautifulSoup

target_url = 'http://www.wegottickets.com/searchresults/page/'
page = 9

# Full page of HTML
def get_full_page(url, page):
    response = requests.get(target_url + str(page) + '/all')
    if response.status_code is 200:
        print "Response from page: "+str(page)
        return response.text
    else:
        print "Error: No response from page: "+str(page)

# Array of each events block of HTML
def get_each_event(markup):
    markup = BeautifulSoup(markup, 'lxml')
    all_events = markup.findAll('div',
                        attrs={'class':'content block-group chatterbox-margin'})

    return all_events

# Get the relevent information out of each events URL and return as object
def parse_each_event(each_event):
    event_url = each_event.find('a', {'class': 'event_link'})['href']
    event_title = each_event.find('a', {'class': 'event_link'}).contents[0]
    venue_details = each_event.find('div', {'class': 'venue-details'})
    venue_name = venue_details.findAll('h4')[0].contents[0]
    event_date = venue_details.findAll('h4')[1].contents[0]
    # TODO Parse Date

    try:
        venue_city = venue_name.split(':')[0]
        venue_name = venue_name.split(':')[1].strip()
    except:
        venue_name = None

    price_data = each_event.find('div', {'class': 'searchResultsPrice'})
    if price_data is None:
        total_price = 0
        ticket_price = 0
        booking_fee = 0
    else:
        split_price = price_data.contents[0]
        each_price = split_price.split(' + ')
        ticket_price = each_price[0][1:]
        booking_fee = each_price[1].split(' ')[0][1:]
        total_price = price_data.find('strong').contents[0][1:]

    available = each_event.find('form', {'class': 'buyboxform'})
    if available is None:
        is_available = False
        tickets = None
    else:
        is_available = True
        tickets = available.find('div', {'class': 'buy-stock'})
        tickets = tickets.find('div').contents[0]

    return {'event_name': event_title,
            'venue_name': venue_name,
            'venue_city': venue_city,
            'event_date': event_date,
            'event_url': event_url,
            'price': {
                'total_price': total_price,
                'ticket_price': ticket_price,
                'booking_fee': booking_fee
                },
            'is_available': is_available
            }

def start_scraper(target_url, page):
    everything = []
    for i in range(1, page):
        html_page = get_full_page(target_url, i)
        all_events = get_each_event(html_page)
        events = []
        for each_event in all_events:
            events.append(parse_each_event(each_event))

        everything.append(events)
    return everything

def write_file(data):
    f = open('output_1-'+str(page-1)+'.json', 'w')
    f.write(json.dumps(list(itertools.chain(*data)),
                        sort_keys=True, indent=4, separators=(',', ': ')))
    print 'FILE: output_1-'+str(page-1)+'.json'

output_data = start_scraper(target_url, page)
write_file(output_data)
