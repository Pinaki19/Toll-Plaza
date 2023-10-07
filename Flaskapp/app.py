from flask import Flask, jsonify, request, render_template, redirect, url_for, session, abort, send_file
from flask_pymongo import PyMongo
from pytz import timezone
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_session import Session
import gridfs
from bson import ObjectId
import json
import io
import pymongo
import requests
import pyrebase

firebase_config = {
    'apiKey': "AIzaSyAAJ4Cv2d6cSSbRmnWQPll4kG4TvjdF-W8",
    'authDomain': "smooth-sailing-ad0d5.firebaseapp.com",
    'projectId': "smooth-sailing-ad0d5",
    'storageBucket': "smooth-sailing-ad0d5.appspot.com",
    'messagingSenderId': "62968749843",
    'appId': "1:62968749843:web:3bbe8560b1e73c0a3244e6",
    'measurementId': "G-E6EFBYWRML",
    'databaseURL':'None'

}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


IST = timezone('Asia/Kolkata')

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017"

database_name = "Users"

# Initialize the PyMongo extension with your Flask app
mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/{database_name}")
db = mongo.db
app.config['SECRET_KEY'] = 'ea5691dc5cddf9f9c4cc457e135e8b44066641c940cc5b6278e20afb2b1b'

# Use MongoDB for session storage
app.config["SESSION_TYPE"] = "mongodb"
# Set the MongoDB connection details for sessions
app.config["SESSION_MONGODB"] = pymongo.MongoClient(
    host="localhost", port=27017)

app.config["SESSION_MONGODB_DB"] = "UserSessions"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"

Session(app)

CORS(app)


mongo_for_gridfs = PyMongo(
    app, uri=f"{app.config['MONGO_URI']}/{database_name}")
fs = gridfs.GridFS(mongo_for_gridfs.db)

#----------------------- utility functions ----------------------------------------------------------------------

def turn_into_num(str):
    s = 0
    for i in str:
        s += ord(i)
    return s


def get_cupon_discount_rate(val):
    mongo3 = PyMongo(
        app, uri=f"{app.config['MONGO_URI']}/Global_Discounts")
    db = mongo3.db
    obj = db.Cupons.find()
    for item in obj:
        if val in item:
            return item[val]
    return 0


def get_gst_rate():
    mongo2 = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Toll_Rate")
    db = mongo2.db
    object_id = ObjectId("6511be0f6cae5e50b4f30e34")
    return db.GST.find_one({"_id": object_id}, {"_id": False})['rate']


def calculate_gst(Amount):
    rate = get_gst_rate()
    return (Amount/100)*rate


def calculate_cupon(Amount, val):
    rate = get_cupon_discount_rate(val)
    return (Amount/100)*rate


def find_Global_discount_amount(Amount):
    rate = find_global_discount_rate()
    if (rate <= 0):
        return 0
    return (Amount/100)*rate



def allowed_file(filename):
    # Define the allowed file extensions (e.g., for images)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def insert_payment_id(email, id):
    # Find the user by email
    user = db.UserData.find_one({'Email': email})
    if user:
        # Check if the 'transactions' field exists
        if 'transactions' not in user:
            # Create 'transactions' field as a list with the first ID
            user['transactions'] = [id]
        else:
            # Append the ID to the existing list
            user['transactions'].append(id)
        # Update the user document in the database
        db.UserData.update_one({'Email': email}, {
            '$set': {'transactions': user['transactions']}})
    else:
        return


def get_toll_amount(vehicle, journey):
    mongo2 = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Toll_Rate")
    db = mongo2.db
    object_id = ObjectId("6510916ca24f1f9870537d5f")
    Rate_chart = db.Rate.find_one({"_id": object_id}, {"_id": False})
    if vehicle in Rate_chart:
        if journey in Rate_chart[vehicle]:
            return Rate_chart[vehicle][journey]
    return 0


def find_global_discount_rate():
    mongo3 = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Global_Discounts")
    db = mongo3.db
    object_Id = ObjectId("6510a31f5c761cfa640a15f0")
    obj = db.Discount.find_one({"_id": object_Id}, {"_id": False})
    return obj['discountRate']


def Register_user(name, email, gender, mobile):
  Recieved = {'Email': email.lower(), 'Name': name,
              'Gender': gender, 'Mobile': mobile}
  if (len(name) < 4 or len(name) > 30):
    abort(404)
  if gender == 'male':
    Recieved.update(
        {"Defualt_Profile": True, 'Profile_Url': 'https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg'})
  elif gender == 'female':
    Recieved.update({"Defualt_Profile": True,
                    'Profile_Url': 'https://img.freepik.com/free-psd/3d-illustration-person-with-glasses_23-2149436185.jpg'})
  else:
    Recieved.update({"Defualt_Profile": False,
                    'Profile_Url': '651808ba72d9dd5d64c4ebd1'})

  Recieved.update(
      {'IsAdmin': False, "IsSuperAdmin": False, 'RegistrationDate': datetime.now(), 'Address': ' '})
  db.UserData.insert_one(Recieved)
  wallet = {'Name': name, 'Email': Recieved['Email'], 'Default': True, 'PIN': 1234 ^ (
      turn_into_num(email)), 'Balance': 0.00, 'Added': 0.00, 'Spent': 0.00, 'Transactions': []}
  db.UserWallets.insert_one(wallet)
  return jsonify("Sucesss")

# ----------------------------------------------------------------------------------------------------------------



#-------------------------------------------- User Account -------------------------------------------------------
@app.get('/get_recent_transactions')
def get_recent_transactions():
    email = session.get('email')
    mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/{database_name}")
    db = mongo.db
    # Query the UserWallets collection to get the list of transaction IDs
    user_wallet = db.UserWallets.find_one({'Email': email})

    if user_wallet:
        transaction_ids = user_wallet.get('Transactions', [])

        # Query the CompletedPayments collection to get transaction details
        recent_transactions = []
        mongo = PyMongo(
            app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
        db = mongo.db
        for transaction_id in transaction_ids:
            payment_doc = db.CompletedPayments.find_one(
                {'_id': ObjectId(transaction_id)})
            if payment_doc:
                transaction_data = payment_doc.get('data', {})
                transaction_type = transaction_data.get('Type', 'Unknown')
                transaction_date = payment_doc.get('DateTime', '')
                formatted_date = transaction_date.strftime('%H:%M %d-%m')
                transaction_amount = transaction_data.get('Amount', 0)
                gst = transaction_data.get('Gst', 0)
                cupon = transaction_data.get('Cupon', 0)
                disc = transaction_data.get('GlobalDiscount', 0)
                transaction_amount=round(transaction_amount+gst-cupon-disc,2)
                transaction_color = 'green' if transaction_type == 'Add Money' else 'red'
                transaction_sign = '+' if transaction_type == 'Add Money' else '-'

                recent_transactions.append({
                    'type': transaction_type,
                    'date': formatted_date,
                    'amount': transaction_amount,
                    'color': transaction_color,
                    'sign': transaction_sign,
                })

        return render_template('recent_transactions.html', recent_transactions=recent_transactions[::-1])
    else:
        return render_template('recent_transactions.html', recent_transactions=[])


@app.route('/get_image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Retrieve the image data from GridFS using the provided image_id
        image_data = fs.get(ObjectId(image_id))

        response = send_file(io.BytesIO(image_data.read()),mimetype='image/jpeg')
        return response
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})




@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Get the uploaded file from the request
        uploaded_file = request.files['image']
        # Check if the file exists and is an allowed file type (e.g., image)
        if uploaded_file and allowed_file(uploaded_file.filename):
            # Store the file in GridFS
            file_id = fs.put(uploaded_file.read(),filename=uploaded_file.filename)
            email = session.get('email')
            db.UserData.update_one(
                {"Email": email}, {"$set": {"image_id": file_id}})
            
            db.UserData.update_one(
                {"Email": email}, {"$set": {"Defualt_Profile": False}})
            

            return jsonify({"success": True, "message": "File uploaded successfully."})
        else:
          return jsonify({"success": False, "message": "Invalid file type or no file provided."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/get_profile_image', methods=['GET'])
def get_profile_image():
    try:
        # Get the user's email from the session
        email = session.get('email')
        # Retrieve the user's profile image URL from the database
        user = db.UserData.find_one({"Email": email})

        if user and 'Profile_Url' in user:
            # Check if the user has a custom profile picture
            if user['Defualt_Profile']:
                # If the user has a default profile picture, use the 'Profile_Url' from the database
                return jsonify({"success": True, 'Default': True, "profile_url": user['Profile_Url']})
            elif 'image_id' not in user:
                return jsonify({"success": True, 'Default': False, "profile_url": user['Profile_Url']})

            else:
                # If the user has a custom profile picture, use their profile image URL as before
                # Convert ObjectId to string
                profile_url = str(user["image_id"])
                return jsonify({"success": True, 'Default': False, "profile_url": profile_url})

        return jsonify({"success": False, "message": "Profile image not found for this user."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/remove_profile_image', methods=['POST'])
def remove_profile_image():
    try:
        # Get the user's email from the session or request
        email = session.get('email')
        # Check if the user has a profile picture in the database
        user_data = db.UserData.find_one({"Email": email})
        if user_data and "image_id" in user_data:
            # Delete the profile picture from database (MongoDB GridFS, for example)
            file_id = user_data["image_id"]
            fs.delete(file_id)

            # Update the user's data to remove the reference to the profile picture
            db.UserData.update_one(
                {"Email": email},
                {"$unset": {"image_id": ""}}
            )
            if user_data['Gender'] != 'others':
                db.UserData.update_one(
                    {"Email": email}, {"$set": {"Defualt_Profile": True}})
            return jsonify({"success": True, "message": "Profile picture removed successfully."})
        else:
            return jsonify({"success": False, "message": "No profile picture found for the user."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


  
@app.post('/Forgot_wallet_pass')
def change_wallet_pass():
    recieved=request.get_json()
    new_PIN=recieved['New'].strip()
    if len(new_PIN)!=4:
        abort(404)
    try:
        new_PIN=int(new_PIN)
        email = session.get('email')
    except:
        abort(404)
    db.UserWallets.update_one({'Email':email},{'$set':{'PIN':new_PIN^(turn_into_num(email)),'Default':False}})
    return jsonify({'success':True})
    
    
@app.route('/Edit_account',methods=['POST'])
def Edit_account():
    received = request.get_json()
    email = received.get('email','').lower()
    collection=db.UserData
    if not 'email' in session:
      abort(404)
    # Search for the user based on email
    user = collection.find_one({'Email': email})

    if user:
        # Update user data
        new_name = received.get('name')
        new_mobile = received.get('mobile')
        new_address = received.get('address')
        if (len(new_name) < 4 or len(new_name) > 40 or len(new_address)>100 or len(new_mobile)>=15):
            abort(404)
        
        update_data = {}
        if new_name:
            update_data['Name'] = new_name
        if new_mobile:
            update_data['Mobile'] = new_mobile
        
        update_data['Address'] = new_address

        # Update the user's data
        collection.update_one({'Email': email}, {'$set': update_data})

        return jsonify({'success':True}),200
      
    else:
        abort(404)

#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
  
@app.route('/Find_user',methods=['POST'])
def find_user():
  Recieved = request.get_json()
  User=db.UserData.find_one(Recieved)
  if User:
    return jsonify({'success': True}), 200
  abort(404)
  
@app.route('/Get_user_details',methods=['POST'])
def get_data():
  return find_user()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('Password', '')  # Get the password from the request

    # Simplified authentication (replace with your authentication logic)
    user = db.UserData.find_one({"Email": email})
   
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        # Get user info and check if email is verified
        user_info = auth.get_account_info(user['idToken'])
        email_verified = user_info["users"][0]["emailVerified"]
        if email_verified:
            session['email']=email
            return jsonify({'code': 200, 'message': 'Login Success'}), 200
        else:
            print("Email is not verified. Requesting a new ID token...")
            #new_id_token = user['idToken']
            return jsonify({'code': 405, 'message':'User Email not verified!'}), 405

    except Exception as e:
        error_message = str(e)
        # Find the start and end positions of the 'error' object
        start_idx = error_message.find('{')
        error_object = error_message[start_idx:]
        error = json.loads(error_object)
        error=error['error']
        error_message = ' '.join(error.get('message', 'Undefined').split('_'))
        return jsonify({'code': error.get('code', '400'), 'message':error_message}),  error.get('code', 400)


@app.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    username = data.get('name')
    mobile= data.get('mobile','')
    gender =data.get('gender',)
    if not (email and password and username and gender):
        return jsonify({'message':'Provide all the Fields!'}), 404
    try:
        # Create a new user in Firebase Authentication
        user = auth.create_user_with_email_and_password(email, password)
        # Send email verification
        auth.send_email_verification(user['idToken'])
        response_data = {
            'message': 'User registration successful. Email verification sent.',
        }
        Register_user(username, email, gender,mobile)
        return jsonify(response_data), 200

    except Exception as e:
       error_message = str(e)
       # Find the start and end positions of the 'error' object
       start_idx = error_message.find('{')
       error_object = error_message[start_idx:]
       error = json.loads(error_object)
       error = error['error']
       print(error)
       error_message = ' '.join(error.get('message', 'Undefined').split('_'))
       return jsonify({'code': error.get('code', '400'), 'message': error_message}),  error.get('code', 400)


@app.route("/reset_password", methods=["POST"])
def reset_password():
    try:
        data = request.get_json()
        email = data.get("Email")

        if not email:
            return jsonify({"message": "Email is required"}), 400

        auth = firebase.auth()
        user = auth.send_password_reset_email(email)

        return jsonify({"message": "Password reset email sent successfully"}), 200
    except Exception as e:
       error_message = str(e)
       # Find the start and end positions of the 'error' object
       start_idx = error_message.find('{')
       error_object = error_message[start_idx:]
       error = json.loads(error_object)
       error = error['error']
       print(error)
       error_message = ' '.join(error.get('message', 'Undefined').split('_'))
       return jsonify({'code': error.get('code', '400'), 'message': error_message}),  error.get('code', 400)



@app.route('/Log_out')
def Logout():
  session.pop('email',default=None)
  return redirect(url_for('index'))


@app.route('/profile', methods=['GET'])
def profile():
    if 'email' in session:
        # Retrieve the user's email from the session
        email = session.get('email')
        user = db.UserData.find_one({"Email": email})
        wallet = db.UserWallets.find_one(
        {'Email': session.get('email')}, {'_id': False})
        if not user or not wallet:
            session.pop('email','')
            abort(404)
        if user:
            # Render the profile template with user data
            return render_template('Account.html', user=user,wallet=wallet)
        else:
            return jsonify("User not found")
    else:
        print("session empty")
        return redirect(url_for('index'))



@app.route('/Check_login', methods=['GET'])
def check_login():
    if 'email' in session:
        return "ok",200
    else:
        abort(404)

@app.route('/get_toll_rate')
def get_rate():
    mongo2= PyMongo(app, uri=f"{app.config['MONGO_URI']}/Toll_Rate")
    db=mongo2.db
    object_id = ObjectId("6510916ca24f1f9870537d5f")
    return jsonify(db.Rate.find_one({"_id": object_id},{"_id":False}))


@app.route('/discounts')
def get_discounts():
    rate = find_global_discount_rate()
    if(rate>0):
        return jsonify({'rate':rate})
    else:
        abort(404)
      
      
@app.post('/Apply_coupon')
def apply_cupon():
    data=request.get_json()
    print(data)
    cupon=data['cupon'].strip().lower()
    if(len(cupon)>=10 or cupon==''):
        abort(404)
    else:
        # Check if payment is requested
        payment_requested = session.get('PaymentRequested')
        if not payment_requested:
            # Handle the case where payment is not requested (e.g., redirect to a different page)
            session.pop('PaymentID', '')
            return abort(404)

        # Retrieve the payment ID from the session
        payment_id = session.get('PaymentID')
        if not payment_id:
            # Handle the case where payment ID is not found (e.g., redirect to a different page)
            return abort(404)

        # Retrieve payment data from MongoDB using the payment ID
        mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
        db = mongo.db
        collection = db.PaymentReferences
        payment_doc = collection.find_one({'_id': ObjectId(payment_id)})
        if not payment_doc:
            session.pop('PaymentRequested', '')
            session.pop('PaymentID', '')
            # Handle the case where payment data is not found (e.g., redirect to a different page)
            return abort(404)

        # Extract payment data from the document
        payment_data = payment_doc['data']
        if(payment_data['Type']=='Add Money'):
            abort(404)
        gross_amount = payment_data['Amount']-payment_data['GlobalDiscount']
        discount = round(calculate_cupon(gross_amount, cupon), 2)
        if(discount>0):
            payment_data['Cupon'] = discount
            collection.update_one(
                {'_id': ObjectId(payment_id)},
                {"$set": {"data.Cupon": discount}}
            )
        return jsonify({'success': True, 'Data':payment_data})
    
#----------------------------------------------------------------------------------------------------------------
#--------------------------------------------Payment Handler ----------------------------------------------------
          
@app.route('/pay', methods=['POST'])
def pay():
    PaymentInfo = request.get_json()
    Type = PaymentInfo['Type']
    mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
    db = mongo.db
    if (Type == 'Toll Payment'):
        Vehicle = PaymentInfo['Vehicle_Type'].strip().lower()
        Journey = PaymentInfo['Journey'].strip().lower()
        Number = PaymentInfo['Vehicle_Number'].strip()
        Amount = get_toll_amount(Vehicle, Journey)
        if Amount == 0:
            abort(404)
        Type = PaymentInfo['Type']
        Gst = round(calculate_gst(Amount), 2)
        if 'Cupon' in PaymentInfo:
            cupon_applied = PaymentInfo['Cupon'].strip()
        else:
            cupon_applied = 'None'
        Global_disc = round(find_Global_discount_amount(Amount), 2)
        cupon_discount = round(calculate_cupon(Amount, cupon_applied), 2)
        
        Data = {
            'Type': Type,
            'Amount': round(float(Amount), 2),
            "Gst": Gst,
            "Cupon": cupon_discount,
            'GlobalDiscount': Global_disc,
            'Number': Number
        }
    elif (Type=='Add Money'):
        Amount=PaymentInfo['Amount']
        if(Amount<=0):
            abort(404)
        Data = {
            'Type': Type,
            'Amount': round(float(Amount), 2),
            "Gst": 0,
            "Cupon": 0,
            'GlobalDiscount': 0,
        }
    # Store the payment data in MongoDB
    expiration_time = datetime.now() + timedelta(minutes=5)
    payment_doc = {
        'data': Data,
        'expiration_time': expiration_time
    }
    result = db.PaymentReferences.insert_one(payment_doc)

    # Set session variables
    session['PaymentRequested'] = True
    # Convert ObjectId to str for storage
    session['PaymentID'] = str(result.inserted_id)
    return redirect(url_for('complete_payment'))

@app.post('/store_pin')
def set_pin():
    recieved=request.get_json()
    PIN=recieved["user_pin"]
    try:
        PIN=int(PIN)
    except:
        abort(404)
    session['PIN']=PIN
    return jsonify({'success':True})

@app.route('/complete_payment', methods=['GET'])
def complete_payment():
    # Check if payment is requested
    payment_requested = session.get('PaymentRequested')
    if not payment_requested:
        # Handle the case where payment is not requested (e.g., redirect to a different page)
        session.pop('PaymentID', '')
        return abort(404)

    # Retrieve the payment ID from the session
    payment_id = session.get('PaymentID')
    if not payment_id:
        session.pop('PaymentRequested', '')
        # Handle the case where payment ID is not found (e.g., redirect to a different page)
        return abort(404)

    # Retrieve payment data from MongoDB using the payment ID
    mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
    db = mongo.db
    collection=db.PaymentReferences
    payment_doc = collection.find_one({'_id': ObjectId(payment_id)})
    if not payment_doc:
        session.pop('PaymentRequested', '')
        session.pop('PaymentID', '')
        # Handle the case where payment data is not found (e.g., redirect to a different page)
        return abort(404)

    # Extract payment data from the document
    payment_data = payment_doc['data']

    # Check if the payment data has expired
    expiration_time = payment_doc['expiration_time']
    current_time = datetime.now()
    if current_time > expiration_time:
        session.pop('PaymentRequested', '')
        session.pop('PaymentID', '')
        # Payment data has expired, delete the document and abort 404
        collection.delete_one({'_id': ObjectId(payment_id)})
        return abort(404)
    mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Users")
    db = mongo.db
    wallet = db.UserWallets.find_one({'Email': session.get('email')},{'_id':False})
    if not wallet:
        wallet={'Logged_in':False,'Balance':0}
    else:
        wallet.update({'Logged_in':True})
    return render_template('Payment.html', PaymentInfo=payment_data,wallet=wallet)



@app.get('/get_payment_id')
def get_payment_id():
    if 'PaymentID' in session and 'PaymentRequested' in session:
        session.pop('PaymentRequested', '')
        payment_id = session.pop('PaymentID', '')
        # Create a MongoDB connection
        mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
        db = mongo.db
        # Get the payment data from PaymentReferences
        payment_doc = db.PaymentReferences.find_one(
            {'_id': ObjectId(payment_id)})

        if payment_doc:
            # Add the payment data to CompletedPayments with a reference number field set to the ID
            payment_doc['ReferenceNumber'] = str(payment_id)
            if 'email' in session:
                email = session.get('email')
                payment_doc['email']=email
                payment_doc['DateTime'] = datetime.now()
                insert_payment_id(email, str(payment_id))
            db.CompletedPayments.insert_one(payment_doc)

            # Delete the payment data from PaymentReferences
            db.PaymentReferences.delete_one({'_id': ObjectId(payment_id)})
            
        payment_data = payment_doc['data']
        if payment_data['Type']=='Add Money':
            mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Users")
            db = mongo.db
            email = session.get('email')
            user_wallet = db.UserWallets.find_one({'Email': email})
            if payment_data['Amount'] > 5000 or payment_data['Amount']<=0:
                return jsonify({'success': False}), 400
            if user_wallet:
                # Update the user's wallet balance by adding payment_data['Amount']
                new_balance = round(user_wallet['Balance'] + payment_data['Amount'],2)
                new_added = user_wallet['Added']+payment_data['Amount']
                l = user_wallet['Transactions']
                l.append(str(payment_id))
                db.UserWallets.update_one(
                    {'Email': email}, {"$set": {"Balance": new_balance, 'Added': new_added, 'Transactions': l}})
            else:
                # Handle the case where the user's wallet document is not found
                print("User not found")
        return jsonify({"success": True, "message": str(payment_id)})
    else:
        return jsonify({"success": False, "message": "Payment data not found"})


@app.get('/update_user_wallet')
def update_wallet():
    payment_id = session.get('PaymentID')
    PIN=session.get('PIN')
    if not PIN or not payment_id:
        return jsonify({'success': False, 'message': "Payment Id not found!"}),400
    # Create a MongoDB connection
    mongo = PyMongo(app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
    db = mongo.db
    # Get the payment data from PaymentReferences
    payment_doc = db.PaymentReferences.find_one(
        {'_id': ObjectId(payment_id)})
    payment_data = payment_doc['data']
    
    mongo2 = PyMongo(app, uri=f"{app.config['MONGO_URI']}/Users")
    db = mongo2.db
    email = session.get('email')
    user_wallet = db.UserWallets.find_one({'Email': email})
    stored_PIN=user_wallet['PIN']
    if(stored_PIN^(turn_into_num(email))!=PIN):
        print('No match')
        return jsonify({'failure': True,'message':"Wrong wallet PIN"}),400
    if user_wallet:
        Amount = payment_data['Amount']+payment_data['Gst'] - \
            payment_data['Cupon']-payment_data['GlobalDiscount']
        if (Amount > user_wallet['Balance']):
            return jsonify({'success': False, 'message': "Low wallet Balance"}),400
        # Update the user's wallet balance by adding payment_data['Amount']
        new_balance = round(user_wallet['Balance'] - Amount,2)
        new_spent = round(user_wallet['Spent'] + Amount,2)
        l=user_wallet['Transactions']
        l.append(str(payment_id))
        db.UserWallets.update_one(
            {'Email': email}, {"$set": {"Balance": new_balance, 'Spent': new_spent, 'Transactions':l}})
        return jsonify({'success':True})
    return jsonify({'success': False, 'message': "Unable to find user wallet"}),400

#---------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------

@app.get('/get_cupons')
def get_cupon_names():
    return jsonify({'success':False}),400
    mongo3 = PyMongo(
        app, uri=f"{app.config['MONGO_URI']}/Global_Discounts")
    db = mongo3.db
    obj = db.Cupons.find()
    for item in obj:
        data=list(item.keys())
        break
    data.remove("_id")
    return jsonify({'success':True,'data':data})
 
 
@app.get('/load_recent_transactions')
def load_recent_transactions():
    # Check if the user is logged in and their email is stored in the session
    if 'email' in session:
        user_email = session['email']
        db_users =db
        # Find the user document by their email
        user_data = db_users.UserData.find_one({'Email': user_email})

        if user_data and 'transactions' in user_data:
            # Get the list of transactions from the user's data
            transactions = user_data['transactions']

            # Connect to the PaymentDetails database
            mongo_payment = PyMongo(
                app, uri=f"{app.config['MONGO_URI']}/PaymentDetails")
            db_payment = mongo_payment.db

            # Find the recent 5 transactions based on ReferenceNumber
            projection = {'_id': 0}

            # Find the recent 5 transactions based on ReferenceNumber
            recent_transactions = list(
                db_payment.CompletedPayments.find(
                    {'ReferenceNumber': {'$in': transactions}},
                    projection=projection
                ).limit(30).sort([('ReferenceNumber', -1)])
            )

            # You now have the recent 5 transactions in the recent_transactions list
            return jsonify({'success': True, 'transactions': recent_transactions})
        else:
            return jsonify({'success': False})
    else:
        return jsonify({'success': False, 'message': 'User not logged in'})


@app.route('/', methods=['GET'])
def index():
  return render_template('Home.html')
    

if __name__ == "__main__":
    app.run(port=8080,debug=True)
