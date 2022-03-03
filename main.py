import xml.dom.minidom as md
from datetime import datetime
from pprint import pprint

from currency import convert_to_ruble


def get_flights(xml_doc):
    flights_nodes = xml_doc.getElementsByTagName('PricedItineraries')[0]
    flights_nodes = flights_nodes.childNodes
    flights = []
    for flight_node in flights_nodes:
        if flight_node.nodeType == 1:
            flight = {}
            for child in flight_node.childNodes:
                if child.nodeType == 1:
                    flight[child.tagName] = child
            flights.append(flight)
    return flights


def get_airport(flight, source_or_destination):
    source = flight.getElementsByTagName(source_or_destination)
    return source[0].firstChild.data


def get_dxb_bkk_flights(flights):
    dxb_bkk_flights = []
    for flight in flights:
        parts_of_itinerary = flight['OnwardPricedItinerary']
        parts_of_itinerary = parts_of_itinerary.getElementsByTagName('Flight')
        source = get_airport(parts_of_itinerary[0], 'Source')
        destination = get_airport(parts_of_itinerary[-1], 'Destination')
        if source == 'DXB' and destination == 'BKK':
            dxb_bkk_flights.append(flight)
    return dxb_bkk_flights


def get_flight_info(flight_node):
    parts_of_itinerary = flight_node.getElementsByTagName('Flight')
    flights = []
    i = 0
    for flight in parts_of_itinerary:
        flight_info = {}
        for child in flight.childNodes:
            if child.nodeType == 1:
                if child.firstChild:
                    flight_info[child.tagName] = child.firstChild.data.strip()
                else:
                    flight_info[child.tagName] = 'None'
        flights.append(flight_info)
    return flights


def get_pricing(pricing_node):
    currency = pricing_node.attributes['currency'].value
    pricing_node = [
        node for node in pricing_node.childNodes if node.nodeType == 1
    ]
    full_pricing = {'currency': currency}
    for pricing in pricing_node:
        full_pricing[pricing.attributes['ChargeType'].value] = pricing.firstChild.data
    return full_pricing


def get_all_flights_info(dxb_bkk_flights):
    flights = []
    for flight in dxb_bkk_flights:
        itinerary = {}
        onward = get_flight_info(flight['OnwardPricedItinerary'])
        pricing = get_pricing(flight['Pricing'])
        itinerary['onward'] = onward
        itinerary['pricing'] = pricing
        flights.append(itinerary)
    return flights


def get_max_min_price(dxb_bkk_flights):
    flight = dxb_bkk_flights[0]
    price = flight['pricing']['TotalAmount']
    currency = flight['pricing']['currency']
    price = convert_to_ruble(price, currency)
    max_price = price
    max_flight = flight
    min_price = price
    min_flight = flight
    for flight in dxb_bkk_flights:
        price = flight['pricing']['TotalAmount']
        currency = flight['pricing']['currency']
        price = convert_to_ruble(price, currency)
        if price > max_price:
            max_price = price
            max_flight = flight
        elif price < min_price:
            min_price = price
            min_flight = flight
    return max_flight, min_flight


def get_duration(arrival, departure):
    departure = datetime.strptime(departure, '%Y-%m-%dT%H%M')
    arrival = datetime.strptime(arrival, '%Y-%m-%dT%H%M')
    return arrival - departure


def get_max_min_duration(dxb_bkk_flights):
    flight = dxb_bkk_flights[0]
    departure = flight['onward'][0]['DepartureTimeStamp']
    arrival = flight['onward'][-1]['ArrivalTimeStamp']
    duration = get_duration(arrival, departure)

    max_duration = duration
    max_flight = flight
    min_duration = duration
    min_flight = flight

    for flight in dxb_bkk_flights:
        departure = flight['onward'][0]['DepartureTimeStamp']
        arrival = flight['onward'][-1]['ArrivalTimeStamp']
        duration = get_duration(arrival, departure)
        if duration > max_duration:
            max_duration = duration
            max_flight = flight
        elif duration < min_duration:
            min_duration = duration
            min_flight = flight
    return max_flight, min_flight, max_duration, min_duration


if __name__ == '__main__':
    xml_doc = md.parse('RS_Via-3.xml')
    xml_doc.normalize()
    flights = get_flights(xml_doc)
    dxb_bkk_flights = get_dxb_bkk_flights(flights)
    dxb_bkk_flights = get_all_flights_info(dxb_bkk_flights)

    while True:
        print('Enter -1 to exit')
        print('Enter 0 to get all flights from DXB to BKK')
        print('Enter 1 to get flight with the max and min cost')
        print('Enter 2 to get flight with the max and min duration')

        user_input = input()
        if user_input == '-1':
            break
        elif user_input == '0':
            pprint(dxb_bkk_flights)
        elif user_input == '1':
            flight_max_price, flight_min_price = get_max_min_price(
                dxb_bkk_flights
            )
            pprint(flight_min_price)
            pprint(flight_max_price)
        elif user_input == '2':
            (
                flight_max_duration,
                flight_min_duration,
                max_duration,
                min_duration
            ) = get_max_min_duration(
                dxb_bkk_flights
            )
            pprint(flight_min_duration)
            pprint(flight_max_duration)
            print(f'max duration {max_duration}\nmin duration {min_duration}')
        else:
            print('Wrong input')
