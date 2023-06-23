from pymongo import MongoClient
from flask import Flask, request, jsonify
import json
from bson import ObjectId


# Connect to our local MongoDB
client = MongoClient('mongodb://localhost:27017/')

# Choose DigitalAirlines database
db = client['DigitalAirlines']

# Create needed collections
users_collection = db['users']
flights_collection = db['available_flights']
reservations_collection = db['reservations']

app = Flask(__name__)

logged_in = False
user_email_Global = "" 

#REGISTER
@app.route('/register', methods=['POST'])
def registerUser():
    userData = json.loads(request.data)
    if users_collection.find_one({'$or': [{'email': userData['email']}, {'username': userData['username']}]}) is not None:
        return jsonify({'message': 'Username or Email Already Exists!'}), 409
   
    username = userData.get('username')
    surname = userData.get('surname') 
    email = userData.get('email')
    password = userData.get('password')
    date_of_birth = userData.get('date_of_birth')
    country_of_origin = userData.get('country_of_origin')
    passport_number = userData.get('passport_number')
   
   
    user = {
        'username' : username,
        'surname' : surname,
        'email' : email,
        'password': password,
        'date_of_birth': date_of_birth,
        'country_of_origin': country_of_origin,
        'passport_number': passport_number
    }

    users_collection.insert_one(user)    
    return jsonify({'message': 'User Registration Was Successful!'}), 201


#SIGN IN
@app.route('/signIn', methods=['POST'])
def signIn():
    global logged_in  
    global user_email_Global
    signInData = json.loads(request.data)
    email = signInData.get('email')
    password = signInData.get('password')

    user = users_collection.find_one({'email': email, 'password': password}, {'_id': 0})
    if user is None:
        return jsonify({'message': 'Invalid credentials! Please try again!'}), 401

    logged_in = True  
    user_email_Global = signInData.get('email')
    return jsonify({'message': 'Sign-in successful', 'user': user}), 200


#SIGN OUT
@app.route('/signOut', methods=['POST'])
def signOut():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    logged_in = False  
    return jsonify({'message': 'User has signed out successfully!'}), 200


#SEARCH FLIGHTS
@app.route('/searchFlights', methods=['GET'])
def searchFlights():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    search_query = {}
    if request.data:
        searchFlightsData = json.loads(request.data)
        originAirport = searchFlightsData.get('originAirport')
        destinationAirport = searchFlightsData.get('destinationAirport')
        date = searchFlightsData.get('date')
        if originAirport and destinationAirport and date:
            search_query = {'originAirport': originAirport,
                            'destinationAirport': destinationAirport, 'date': date}
        elif originAirport and destinationAirport:
            search_query = {'originAirport': originAirport,
                            'destinationAirport': destinationAirport}
        elif date:
            search_query = {'date': date}
        elif originAirport or destinationAirport:
            return jsonify({'message': 'Not sufficient information to execute the search!'}), 400 

    flights = flights_collection.find(search_query)
    available_flights = []
    for flight in flights:
        available_flights.append({
            '_id': str(flight['_id']),
            'date': flight['date'],
            'originAirport': flight['originAirport'],
            'destinationAirport': flight['destinationAirport']
        })

    return jsonify({'available_flights': available_flights}), 200


#SHOW FLIGHTS DETAILS
@app.route('/showFlightDetails', methods=['GET'])
def showFlightDetails():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    showFlightDetailsData = json.loads(request.data)
    flight_code = showFlightDetailsData.get('flight_code')

    flight = flights_collection.find_one({'_id': ObjectId(flight_code)})

    if flight is None:
        return jsonify({'message': 'No flight was found.'}), 404

    flightDetails = {
        'date': flight['date'],
        'originAirport': flight['originAirport'],
        'destinationAirport': flight['destinationAirport'],
        'available_tickets': {
            'economy': int(flight['available_tickets']['economy']),
            'business': int(flight['available_tickets']['business'])
        },
        'ticket_cost': {
            'economy': flight['ticket_cost']['economy'], #not int() because it might be "100$" for example
            'business': flight['ticket_cost']['business'] #not int() because it might be "100$" for example
        }
    }

    return jsonify(flightDetails), 200


#TICKET RESERVATION
@app.route('/ticketReservation', methods=['POST'])
def ticketReservation():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    ticketReservationData = json.loads(request.data)
    flight_code = ticketReservationData.get('flight_code')
    name = ticketReservationData.get('name')
    surname = ticketReservationData.get('surname')
    passport_number = ticketReservationData.get('passport_number')
    date_of_birth = ticketReservationData.get('date_of_birth')
    email = ticketReservationData.get('email')
    ticket_class = ticketReservationData.get('ticket_class')

    flight = flights_collection.find_one({'_id': ObjectId(flight_code)})

    if flight is None:
        return jsonify({'message': 'No flight was found.'}), 404


    if ticket_class == 'economy':
        class_tickets = int(flight['available_tickets']['economy'])
        flights_collection.update_one({'_id': ObjectId(flight_code)}, {'$set': {'available_tickets.economy': class_tickets - 1}})

    elif ticket_class == 'business':    
        class_tickets = int(flight['available_tickets']['business'])
        flights_collection.update_one({'_id': ObjectId(flight_code)}, {'$set': {'available_tickets.business': class_tickets - 1}})

    reservation = {
        'flight': flight['_id'],
        'name': name,
        'surname': surname,
        'passport_number': passport_number,
        'date_of_birth': date_of_birth,
        'email': email,
        'ticket_class': ticket_class
    }

    reservations_collection.insert_one(reservation)
    return jsonify({'message': 'Your ticket has been reserved!.'}), 200


#SHOW RESERVATIONS
@app.route('/showReservations', methods=['GET'])
def showReservations():
    global logged_in  
    global user_email_Global
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    #Find reservations made by the user
    reservations = reservations_collection.find({'email': user_email_Global})

    user_reservations = []
    for reservation in reservations:
        user_reservations.append({
            'flight_code': str(reservation['flight']),
            'name': reservation['name'],
            'surname': reservation['surname'],
            'passport_number': reservation['passport_number'],
            'date_of_birth': reservation['date_of_birth'],
            'email': reservation['email'],
            'ticket_class': reservation['ticket_class']
        })

    return jsonify({'user reservations': user_reservations}), 200


#SHOW RESERVATION DETAILS
@app.route('/showReservationDetails', methods=['GET'])
def showReservationDetails():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    showReservationDetailsData = json.loads(request.data)
    reservation_code = showReservationDetailsData.get('reservation_code')

    reservation = reservations_collection.find_one({'_id': ObjectId(reservation_code)})
    flight = flights_collection.find_one({'_id': ObjectId(reservation['flight'])})
    if reservation is None:
        return jsonify({'message': 'No reservation was found.'}), 404

    reservationDetails = {
        'originAirport': flight['originAirport'],
        'destinationAirport': flight['destinationAirport'],
        'date': flight['date'],
        'name': reservation['name'],
        'surname': reservation['surname'],
        'passport_number': reservation['passport_number'],
        'date_of_birth': reservation['date_of_birth'],
        'email': reservation['email'],
        'ticket_class': reservation['ticket_class']
    }

    return jsonify(reservationDetails), 200

#CANCEL RESERVATION
@app.route('/cancelReservation', methods=['POST'])
def cancelReservation():
    global logged_in
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    cancelReservationData = json.loads(request.data)
    reservation_code = cancelReservationData.get('reservation_code')

    reservation = reservations_collection.find_one({'_id': ObjectId(reservation_code)})
    if reservation is None:
        return jsonify({'message': 'No reservation was found.'}), 404


    #Update the available tickets for the flight based on the ticket class
    flight = reservation['flight']
    ticket_class = reservation['ticket_class']
    if ticket_class == 'economy':
        flights_collection.update_one({'_id': ObjectId(flight)}, {'$inc': {'available_tickets.economy': 1}})
    elif ticket_class == 'business':    
        flights_collection.update_one({'_id': ObjectId(flight)}, {'$inc': {'available_tickets.business': 1}})


    #Delete the reservation
    reservations_collection.delete_one({'_id': ObjectId(reservation_code)})

    return jsonify({'message': 'Reservation canceled successfully.'}), 200


#DELETE ACCOUNT
@app.route('/deleteAccount', methods=['POST'])
def deleteAccount():
    global logged_in  
    if not logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    #Delete the user account
    users_collection.delete_one({'email': user_email_Global})

    #Reset global variable and log out the user
    logged_in = False

    return jsonify({'message': 'Account has been deleted successfully!'}), 200

#-------------------------------------------------------------------------------------------------------------
#ADMINISTRATOR ENDPOINTS
admin_logged_in = False
admin_email_Global = "k@gmail.com"

admin = {   #Create the admin
    'username' : 'admin',
    'email' : admin_email_Global,
    'password': '123',
    'isAdmin' : True
}

existing_admin = users_collection.find_one({'isAdmin': True})  
if existing_admin is None:  #Check if admin already exists and if not, insert him in the users_collection
    users_collection.insert_one(admin)

#ADMIN SIGN IN
@app.route('/adminSignIn', methods=['POST'])
def adminLogin():
    global admin_logged_in, admin_email_Global
    adminSignInData = json.loads(request.data)
    email = adminSignInData.get('email')
    password = adminSignInData.get('password')

    #Check if the user is an administrator
    admin = users_collection.find_one({'email': email, 'password': password})

    if admin is None:
        return jsonify({'message': 'Invalid credentials! Please try again!'}), 401

    admin_logged_in = True
    admin_email_Global = email

    return jsonify({'message': 'Admin sign-in successful!'}), 200


#ADMIN SIGN OUT
@app.route('/adminSignOut', methods=['POST'])
def adminSignOut():
    global admin_logged_in, admin_email_Global
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in as admin!'}), 401

    admin_logged_in = False
    admin_email_Global = ""
    return jsonify({'message': 'Admin has signed out successfully!'}), 200


#CREATE FLIGHT
@app.route('/createFlight', methods=['POST'])
def createFlight():
    global admin_logged_in
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in as an admin!'}), 401

    createFlightData = json.loads(request.data)
    originAirport = createFlightData.get('originAirport')
    destinationAirport = createFlightData.get('destinationAirport')
    date = createFlightData.get('date')
    businessTickets = createFlightData.get('businessTickets')
    economyTickets = createFlightData.get('economyTickets')
    businessCost = createFlightData.get('businessCost')
    economyCost = createFlightData.get('economyCost')

    flight = {
        'originAirport': originAirport,
        'destinationAirport': destinationAirport,
        'date': date,
        'available_tickets': {
            'business': int(businessTickets),
            'economy': int(economyTickets)
        },
        'ticket_cost': {
            'business': businessCost,
            'economy': economyCost
        }
    }

    flights_collection.insert_one(flight)
    return jsonify({'message': 'Flight created successfully!'}), 201


#UPDATE TICKET COST
@app.route('/updateTicketCost', methods=['POST'])
def updateTicketCost():
    global admin_logged_in
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in as an admin!'}), 401

    updateTicketCostData = json.loads(request.data)
    flight_code = updateTicketCostData.get('flight_code')
    economy_price = updateTicketCostData.get('economy_price')
    business_price = updateTicketCostData.get('business_price')

    flight = flights_collection.find_one({'_id': ObjectId(flight_code)})

    if flight is None:
        return jsonify({'message': 'No flight was found.'}), 404

    #Update the ticket prices
    flights_collection.update_one({'_id': ObjectId(flight_code)}, {'$set': {'ticket_cost.economy': economy_price, 'ticket_cost.business': business_price}})

    return jsonify({'message': 'Ticket prices have been updated successfully!'}), 200


#DELETE FLIGHT
@app.route('/deleteFlight', methods=['POST'])
def deleteFlight():
    global admin_logged_in
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in as an administrator!'}), 401

    deleteFlightData = json.loads(request.data)
    flight_code = deleteFlightData.get('flight_code')

    flight = flights_collection.find_one({'_id': ObjectId(flight_code)})

    if flight is None:
        return jsonify({'message': 'No flight was found.'}), 404

    #Check if there are any reservations for the flight
    if reservations_collection.find_one(): #check if collection is completely empty - if not,check for reservations for a specific flight
        reservations = reservations_collection.find({'flight': ObjectId(flight_code)})
        reservationsList = list(reservations)
        if len(reservationsList) > 0:
            return jsonify({'message': 'Not able to delete the flight. There are reservations associated with it.'}), 409
    
    #Delete the flight
    flights_collection.delete_one({'_id': ObjectId(flight_code)})

    return jsonify({'message': 'Flight has been deleted successfully!'}), 200


#SEARCH FLIGHTS (ADMIN)
@app.route('/searchFlightsAdmin', methods=['GET'])
def searchFlightsAdmin():
    global admin_logged_in  
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    search_query = {}
    if request.data:
        searchFlightsData = json.loads(request.data)
        originAirport = searchFlightsData.get('originAirport')
        destinationAirport = searchFlightsData.get('destinationAirport')
        date = searchFlightsData.get('date')

        if originAirport and destinationAirport and date:
            search_query = {'originAirport': originAirport,
                            'destinationAirport': destinationAirport, 'date': date}
        elif originAirport and destinationAirport:
            search_query = {'originAirport': originAirport,
                            'destinationAirport': destinationAirport}
        elif date:
            search_query = {'date': date}
        elif originAirport or destinationAirport:
            return jsonify({'message': 'Not sufficient information to execute the search!'}), 400


    flights = flights_collection.find(search_query)
    available_flights = []
    for flight in flights:
        available_flights.append({
            '_id': str(flight['_id']),
            'date': flight['date'],
            'originAirport': flight['originAirport'],
            'destinationAirport': flight['destinationAirport']
        })

    return jsonify({'available_flights': available_flights}), 200


#SHOW FLIGHTS DETAILS (ADMIN)
@app.route('/showFlightDetailsAdmin', methods=['GET'])
def showFlightDetailsAdmin():
    global admin_logged_in  
    if not admin_logged_in:
        return jsonify({'message': 'Access has been denied! You are not signed in!'}), 401

    showFlightDetailsData = json.loads(request.data)
    flight_code = showFlightDetailsData.get('flight_code')

    flight = flights_collection.find_one({'_id': ObjectId(flight_code)})

    if flight is None:
        return jsonify({'message': 'No flight was found.'}), 404

    economy_tickets = flight['available_tickets']['economy'] #avail
    business_tickets = flight['available_tickets']['business'] #avail 
    total_tickets = int(flight['available_tickets']['economy']) + int(flight['available_tickets']['business']) #total
    
    if reservations_collection.find_one(): #check if collection is completely empty - if not,check for reservations for a specific flight
        reservationsE = reservations_collection.find({'flight': ObjectId(flight_code),'ticket_class': 'economy'})
        reservationsListE = list(reservationsE)

        reservationsB = reservations_collection.find({'flight': ObjectId(flight_code),'ticket_class': 'business'})
        reservationsListB = list(reservationsB)

        economy_tickets = int(flight['available_tickets']['economy']) + len(reservationsListE) #avail + reserv
        business_tickets = int(flight['available_tickets']['business']) + len(reservationsListB) #avail + reserv
        total_tickets = economy_tickets + business_tickets


    available_tickets = int(flight['available_tickets']['economy']) + int(flight['available_tickets']['business'])

    flightDetails = {
        'originAirport': flight['originAirport'],
        'destinationAirport': flight['destinationAirport'],
        'total_tickets' : total_tickets,
        'total_tickets_per_class': {
            'economy': int(economy_tickets),
            'business': int(business_tickets)
        },
        'ticket_cost': {
            'economy': flight['ticket_cost']['economy'], #not int() because it might be "100$"
            'business': flight['ticket_cost']['business'] #not int() because it might be "100$"
        },
        'available_tickets': available_tickets,
        'available_tickets_per_class': {
            'economy': int(flight['available_tickets']['economy']),
            'business': int(flight['available_tickets']['business'])
        },
        'reservations': []
    }
    
    if reservations_collection.find_one(): #check if collection is completely empty - if not,check for reservations for a specific flight
        reservations = reservations_collection.find({'flight': ObjectId(flight_code)})
        for reservation in reservations:
            flightDetails['reservations'].append({
                'name': reservation['name'],
                'surname': reservation['surname'],
                'ticket_class': reservation['ticket_class'] 
            })

    return jsonify(flightDetails), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
