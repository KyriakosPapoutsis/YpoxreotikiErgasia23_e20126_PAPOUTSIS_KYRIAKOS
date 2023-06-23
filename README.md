# YpoxreotikiErgasia23_e20126_PAPOUTSIS_KYRIAKOS

## ΛΕΠΤΟΜΕΡΗΣ ΕΠΕΞΗΓΗΣΗ ΤΟΥ ΚΩΔΙΚΑ ΚΑΙ ΠΑΡΑΔΕΙΓΜΑΤΑ ΕΚΤΕΛΕΣΗΣ

Κάνουμε τα απαραίτητα imports, συνδεόμαστε στη βάση δεδομένων DigitalAirlines και δημιουργούμε τα collections της.
~~~python
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
~~~

### ΤΑ ENDPOINTS ΑΠΛΟΥ ΧΡΗΣΤΗ

Για όλες τις λειτουργίες(endpoints) του απλού χρήστη, δημιουργούμε τις μεταβλητές logged_in και user_email_Global ώστε να ελέγχουμε ότι είναι συνδεδεμένος πρωτού εκτελέσει κάποια λειτουργία.

~~~python
logged_in = False
user_email_Global = "" 
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */register*
Αρχικά γίνεται έλεγχος για το αν υπάρχει άλλος χρήστης στο users_collection με το ίδιο email ή username και αν ναι εμφανίζεται αντίστοιχο μήνυμα με http code 409(Conflict).
~~~python
 userData = json.loads(request.data)
    if users_collection.find_one({'$or': [{'email': userData['email']}, {'username': userData['username']}]}) is not None:
        return jsonify({'message': 'Username or Email Already Exists!'}), 409
~~~
Αν δεν τίθεται θέμα ύπαρξης χρήστη με όμοιο email ή username, παίρνει τα στοιχεία που δίνει ο χρήστης, δημιουργεί τον user, τον εισάγει στο users_collection και εμφανίζει το αντίστοιχο μήνυμα με http code 201(Created).
~~~python
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
~~~
Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "username":"johnathan",
    "surname":"lucky",
    "email":"john@gmail.com",
    "password":"444",
    "date_of_birth":"1998-01-02",
    "country_of_origin":"Russia",
    "passport_number":"a99872"
}
~~~
και λαμβάνουμε ως απάντηση:
~~~json
{
    "message": "User Registration Was Successful!"
}
~~~
με status code 201 CREATED.

Αν ξαναπροσπαθήσουμε να εισάγουμε χρήστη με όμοιο email μέσω Postman για παράδειγμα:
~~~json
{
    "username":"mike",
    "surname":"dean",
    "email":"john@gmail.com",
    "password":"222",
    "date_of_birth":"1999-12-12",
    "country_of_origin":"Greece",
    "passport_number":"a69676"
}
~~~
λαμβάνουμε ως απάντηση:
~~~json
{
    "message": "Username or Email Already Exists!"
}
~~~
με status code 409 CONFLICT.

+ #### ΛΕΙΤΟΥΡΓΙΑ */signIn*
Στη συγκεκριμένη λειτουργία, ελέγχονται τα στοιχεία που δίνει ο χρήστης (email και password) και αν δεν υπάρχει τέτοιος user στο users_collection εμφανίζεται μήνυμα πως τα διαπιστευτήρια είναι εσφαλμένα και ο χρήστης προτρέπεται να δοκιμάσει την εισαγωγή στοιχείων ξανά με http code 401(Unauthorized), διαφορετικά αν είναι επιτυχής το sign in εμφανίζεται ανάλογο μήνυμα μαζι με τα στοιχεία του user και http code 200(OK) και ταυτόχρονα ενημερώνονται οι μεταβλητές logged_in και user_email_Global. 

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "email":"john@gmail.com",
    "password":"444"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Sign-in successful",
    "user": {
        "country_of_origin": "Russia",
        "date_of_birth": "1998-01-02",
        "email": "john@gmail.com",
        "passport_number": "a99872",
        "password": "444",
        "surname": "lucky",
        "username": "johnathan"
    }
}
~~~
με status code 200 OK.

Σε ανεπιτυχής προσπάθεια:
~~~json
{
    "message": "Invalid credentials! Please try again!"
}
~~~
με status code 401 UNAUTHORIZED.

+ #### ΛΕΙΤΟΥΡΓΙΑ */signOut*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, αλλάζει η τιμή της μεταβλητής logged_in σε False και εμφανίζεται αντίστοιχο μήνυμα με http code 200(OK).

Στο Postman, αφού έχει προηγηθεί το sign in στην προηγούμενη λειτουργία:
~~~json
{
    "message": "User has signed out successfully!"
}
~~~
με status code 200 OK.

+ #### ΛΕΙΤΟΥΡΓΙΑ */searchFlights*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, δημιουργείται ένα search_query με βάση τα στοιχεία που επιλέγει να δώσει ο χρήστης κάθε φορά:
1. Αεροδρόμιο προέλευσης και αεροδρόμιο τελικού προορισμού
2. Αεροδρόμιο προέλευσης, αεροδρόμιο τελικού προορισμού και ημερομηνία
διεξαγωγής
3. Ημερομηνία
4. Κανένα στοιχείο (εμφανίζονται όλες οι πτήσεις)

Με αυτό το search_query που δημιουργείται γίνεται η αναζήτηση στην flights_collection και εμφανίζεται η λίστα με τις ανάλογες πτήσεις(με στοιχεία _id, date, originAirport, destinationAirport) με http code 200(OK). Στην περίπτωση που δεν τηρηθεί η εισαγωγή στοιχείων με έναν από τους 4 προαναφερθέντες τρόπους, εμφανίζεται μήνυμα για μη ικανοποιητικές πληροφορίες με http code 400(Bad Request).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "date": "2023-08-13"
}
~~~
και λαμβάνουμε:
~~~json
{
    "available_flights": [
        {
            "_id": "6494d47bbaa68bd557b2fdf4",
            "date": "2023-08-13",
            "destinationAirport": "thailand",
            "originAirport": "portugal"
        },
        {
            "_id": "6494d4b1baa68bd557b2fdf5",
            "date": "2023-08-13",
            "destinationAirport": "france",
            "originAirport": "italy"
        }
    ]
}
~~~
με status code 200 OK.

Σε ανεπιτυχής προσπάθεια (π.χ. με εισαγωγή μόνο του originAirport):
~~~json
{
    "message": "Not sufficient information to execute the search!"
}
~~~
με status code 400 BAD REQUEST.

+ #### ΛΕΙΤΟΥΡΓΙΑ */showFlightDetails*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, μέσω του flight_code που θα εισάγει πραγματοποιείται η αναζήτηση στην flights_collection και εμφανίζονται όλες οι λεπτομέρειες της πτήσης(date, originAirport, destinationAirport, available_tickets[economy και business], ticket_cost [economy και business]) με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "flight_code":"6494d47bbaa68bd557b2fdf4"
}
~~~
και λαμβάνουμε:
~~~json
{
    "available_tickets": {
        "business": 45,
        "economy": 55
    },
    "date": "2023-08-13",
    "destinationAirport": "thailand",
    "originAirport": "portugal",
    "ticket_cost": {
        "business": "111$",
        "economy": "222$"
    }
}
~~~
με status code 200 OK.

Σε περίπτωση που δεν υπάρχει πτήση με τέτοιο flight_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No flight was found."
}
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */ticketReservation*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, αναζητείται η πτήση που επιθυμεί με βάση το flight_code και αν υπάρχει ελέγχεται το ticket_class που επέλεξε και ανάλογα (economy ή business) ανανεώνονται τα διαθέσιμα εισητήρια (available_tickets). Έπειτα δημιουργείται η κράτηση (reservation) με τα στοιχεία που έδωσε και προστίθεται στην reservations_collection. Τέλος, εμφανίζεται μήνυμα επιτυχίας με http code 200(Ok).  

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "flight_code":"6494d4b1baa68bd557b2fdf5",
    "name":"johnathan",
    "surname":"lucky",
    "passport_number":"a99872",
    "date_of_birth":"1998-01-02",
    "email":"john@gmail.com",
    "ticket_class":"business"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Your ticket has been reserved!."
}
~~~
με status code 200 OK.

Σε περίπτωση που δεν υπάρχει πτήση με τέτοιο flight_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No flight was found."
}
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */showReservations* 
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, πραγματοποιείται μία αναζήτηση στην reservations_collection με βάση το user_email_Global και εμφανίζεται μία λίστα με όλες τις κρατήσεις του συγκεκριμένου χρήστη με http code 200(Ok).

Στο Postman, αφού έχει προηγηθεί το sign in σε προηγούμενη λειτουργία:
~~~json
{
    "user reservations": [
        {
            "date_of_birth": "1998-01-02",
            "email": "john@gmail.com",
            "flight_code": "6494d4b1baa68bd557b2fdf5",
            "name": "johnathan",
            "passport_number": "a99872",
            "surname": "lucky",
            "ticket_class": "business"
        }
    ]
}
~~~
με status code 200 OK.

+ #### ΛΕΙΤΟΥΡΓΙΑ */showReservationDetails*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, αναζητείται η κράτηση που επιθυμεί με βάση το reservation_code και αν υπάρχει και εμφανίζονται όλες οι λεπτομέρειες της κράτησης (date της πτήσης την οποία αφορά, originAirport της πτήσης την οποία αφορά, destinationAirport της πτήσης την οποία αφορά, name, surname, passport_number, date_of_birth, email, ticket_class) με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "reservation_code":"6494d96cbaa68bd557b2fdf6"
}
~~~
και λαμβάνουμε:
~~~json
{
    "date": "2023-08-13",
    "date_of_birth": "1998-01-02",
    "destinationAirport": "france",
    "email": "john@gmail.com",
    "name": "johnathan",
    "originAirport": "italy",
    "passport_number": "a99872",
    "surname": "lucky",
    "ticket_class": "business"
}
~~~
με status code 200 OK.

Σε περίπτωση που δεν υπάρχει κράτηση με τέτοιο reservation_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No reservation was found."
}
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */cancelReservation*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, αναζητείται η κράτηση που επιθυμεί να ακυρώσει με βάση το reservation_code, ενημερώνονται ανάλογα το ticket_class (economy ή business) τα διαθέσιμα εισητήρια (available_tickets) και διαγράφεται η κράτηση από την reservations_collection. Εμφανίζεται κατάλληλο μήνυμα με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "reservation_code":"6494d96cbaa68bd557b2fdf6"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Reservation canceled successfully."
}
~~~
με status code 200 OK.

Σε περίπτωση που δεν υπάρχει κράτηση με τέτοιο reservation_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No reservation was found."
}
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */deleteAccount*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο χρήστης και αν ναι, διαγράφεται ο user από την users_collection μέσω του user_email_Global, αλλάζει η τιμή της μεταβλητής logged_in σε False και εμφανίζεται κατάλληλο μήνυμα με http code 200(Ok).

Στο Postman, αφού έχει προηγηθεί το sign in σε προηγούμενη λειτουργία:
~~~json
{
    "message": "Account has been deleted successfully!"
}
~~~
με status code 200 OK.

### ΤΑ ENDPOINTS ΔΙΑΧΕΙΡΙΣΤΗ
Ο διαχειρηστής (admin) υπάρχει ήδη στο σύστημα επομένως εισάγεται μία φορά στην users_collection εξαρχής.

Για όλες τις λειτουργίες(endpoints) του admin, δημιουργούμε τις μεταβλητές admin_logged_in και admin_email_Global ώστε να ελέγχουμε ότι είναι συνδεδεμένος πρωτού εκτελέσει κάποια λειτουργία.

~~~python
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
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */adminSignIn*
Στη συγκεκριμένη λειτουργία, ελέγχονται τα στοιχεία που δίνει ο admin (email και password) και αν δεν υπάρχει τέτοιος user στο users_collection εμφανίζεται μήνυμα πως τα διαπιστευτήρια είναι εσφαλμένα και ο χρήστης προτρέπεται να δοκιμάσει την εισαγωγή στοιχείων ξανά με http code 401(Unauthorized), διαφορετικά αν είναι επιτυχής το sign in εμφανίζεται ανάλογο μήνυμα μαζι με τα στοιχεία του user και http code 200(OK) και ταυτόχρονα ενημερώνονται οι μεταβλητές admin_logged_in και admin_email_Global.

Στέλνουμε μέσω Postman το εξής:
~~~json
{
    "email": "k@gmail.com",
    "password": "123"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Admin sign-in successful!"
}
~~~
με status code 200 OK.

+ #### ΛΕΙΤΟΥΡΓΙΑ */adminSignOut*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, αλλάζει η τιμή της μεταβλητής admin_logged_in σε False και εμφανίζεται αντίστοιχο μήνυμα με http code 200(OK).

Στο Postman, αφού έχει προηγηθεί το sign in στην προηγούμενη λειτουργία:
~~~json
{
    "message": "Admin has signed out successfully!"
}
~~~
με status code 200 OK.

+ #### ΛΕΙΤΟΥΡΓΙΑ */createFlight*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, χρησιμοποιούνται όλες οι πληροφορίες που εισάγει σχετικά με την πτήση που επιθυμεί να δημιουργήσει, φτιάχνεται το flight και πραγματοποιείται η εισαγωγή του στην flights_collection. Εμφανίζεται κατάλληλο μήνυμα με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "originAirport" : "italy",
    "destinationAirport" : "france",
    "date" : "2023-08-13",
    "businessTickets" : "34",
    "economyTickets" : "69",
    "businessCost" : "90$",
    "economyCost" : "55$"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Flight created successfully!"
}
~~~
με status code 200 OK.

+ #### ΛΕΙΤΟΥΡΓΙΑ */updateTicketCost*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, αναζητείται η πτήση που θέλει να τροποποιήσει μέσω του flight_code και ανανεώνονται τα κόστη των εισητηρίων με βάση τα εισαχθέντα economy_price και business_price. Τέλος, εμφανίζεται κατάλληλο μήνυμα με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "flight_code" : "6494d47bbaa68bd557b2fdf4",
    "economy_price" : "300$",
    "business_price" : "500$"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Ticket prices have been updated successfully!"
}
~~~
με status code 200 OK.

Σε περίπτωση που δεν υπάρχει πτήση με τέτοιο flight_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No flight was found."
}
~~~

+ #### ΛΕΙΤΟΥΡΓΙΑ */deleteFlight*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, αναζητείται η πτήση που θέλει να διαγράψει μέσω του flight_code, πραγματοποιείται έλεγχος για το αν υπάρχουν κρατήσεις για τη συγκεκριμένη πτήση και αν όχι, την διαγράφει από την flights_collection και εμφανίζει κατάλληλο μήνυμα με http code 200(Ok). 

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "flight_code" : "6494d47bbaa68bd557b2fdf4"
}
~~~
και λαμβάνουμε:
~~~json
{
    "message": "Flight has been deleted successfully!"
}
~~~
με status code 200 OK.

Στην περίπτωση όπου υπάρχουν κρατήσεις για τη συγκεκριμένη πτήση εμφανίζεται αντίστοιχο μήνυμα με http code 409(Conflict) και η πτήση δεν διαγράφεται.
~~~json
{
  "message": "Not able to delete the flight. There are reservations associated with it."
}
~~~
με status code 409 CONFLICT.

+ #### ΛΕΙΤΟΥΡΓΙΑ */searchFlightsAdmin*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, δημιουργείται ένα search_query με βάση τα στοιχεία που επιλέγει να δώσει ο admin κάθε φορά:
1. Αεροδρόμιο προέλευσης και αεροδρόμιο τελικού προορισμού
2. Αεροδρόμιο προέλευσης, αεροδρόμιο τελικού προορισμού και ημερομηνία
διεξαγωγής
3. Ημερομηνία
4. Κανένα στοιχείο (εμφανίζονται όλες οι πτήσεις)

Με αυτό το search_query που δημιουργείται γίνεται η αναζήτηση στην flights_collection και εμφανίζεται η λίστα με τις ανάλογες πτήσεις(με στοιχεία _id, date, originAirport, destinationAirport) με http code 200(OK). Στην περίπτωση που δεν τηρηθεί η εισαγωγή στοιχείων με έναν από τους 4 προαναφερθέντες τρόπους, εμφανίζεται μήνυμα για μη ικανοποιητικές πληροφορίες με http code 400(Bad Request).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "originAirport":"italy",
    "destinationAirport":"france",
    "date":"2023-08-13"
}
~~~
και λαμβάνουμε:
~~~json
{
    "available_flights": [
        {
            "_id": "6494d4b1baa68bd557b2fdf5",
            "date": "2023-08-13",
            "destinationAirport": "france",
            "originAirport": "italy"
        }
    ]
}
~~~
Σε ανεπιτυχής προσπάθεια (π.χ. με εισαγωγή μόνο του destinationAirport):
~~~json
{
    "message": "Not sufficient information to execute the search!"
}
~~~
με status code 400 BAD REQUEST.

+ #### ΛΕΙΤΟΥΡΓΙΑ */showFlightDetailsAdmin*
Σε αυτή τη λειτουργία ελέγχεται αν είναι συνδεδεμένος ο admin και αν ναι, μέσω του flight_code που θα εισάγει πραγματοποιείται η αναζήτηση στην flights_collection και εμφανίζονται όλες οι λεπτομέρειες της πτήσης(date, originAirport, destinationAirport, total_tickets, total_tickets_per_class[economy και business], available_tickets, available_tickets_per_class[economy και business], ticket_cost[economy και business] και λίστα με όλες τις κρατήσεις[reservations] για την συγκεκριμένη πτήση) με http code 200(Ok).

Για παράδειγμα, στέλνουμε μέσω Postman το εξής:
~~~json
{
    "flight_code" : "6494d4b1baa68bd557b2fdf5"
}
~~~
και λαμβάνουμε:
~~~json
{
    "available_tickets": 102,
    "available_tickets_per_class": {
        "business": 34,
        "economy": 68
    },
    "destinationAirport": "france",
    "originAirport": "italy",
    "reservations": [
        {
            "name": "mike",
            "surname": "dean",
            "ticket_class": "economy"
        }
    ],
    "ticket_cost": {
        "business": "90$",
        "economy": "55$"
    },
    "total_tickets": 103,
    "total_tickets_per_class": {
        "business": 34,
        "economy": 69
    }
}
~~~
με status code 200 OK.

*Παρατήρηση: Στο /createFlight δημιουργήσαμε την συγκεκριμένη πτήση με 69 economy tickets, όμως αφού η μία κράτηση εισητηρίου σχετικά με αυτή είναι για θέση economy, στα available_tickets_per_class στη κατηγορία economy βλέπουμε 68 εισητήρια.*

Σε περίπτωση που δεν υπάρχει πτήση με τέτοιο flight_code εμφανίζεται αντίστοιχο μήνυμα με http code 404(Not Found).
~~~json
{
    "message": "No flight was found."
}
~~~
