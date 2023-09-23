from flask import Flask, jsonify, request, render_template, redirect, url_for, session, abort, send_file
from flask_pymongo import PyMongo
from pytz import timezone
from flask_cors import CORS
from datetime import datetime
from flask_session import Session
import gridfs
from bson import ObjectId
import io
import pymongo

IST = timezone('Asia/Kolkata')

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Users"
app.config['SECRET_KEY'] = 'ea5691dc5cddf9f9c4cc457e135e8b44066641c940cc5b6278e20afb2b1b'

# Use MongoDB for session storage
app.config["SESSION_TYPE"] = "mongodb"
# Set the MongoDB connection details for sessions
app.config["SESSION_MONGODB"] = pymongo.MongoClient(
    host="localhost", port=27017)
# Set the desired session collection name (e.g., "sessions") and database name (e.g., "UserData")
app.config["SESSION_MONGODB_DB"] = "UserSessions"
app.config["SESSION_MONGODB_COLLECT"] = "sessions"

Session(app)

mongo = PyMongo(app)
db = mongo.db
CORS(app)


# Replace 'your_db_name' with your actual database name

fs = gridfs.GridFS(db)


@app.route('/get_image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Retrieve the image data from GridFS using the provided image_id
        image_data = fs.get(ObjectId(image_id))

        # Set the appropriate response headers
        response = send_file(io.BytesIO(image_data.read()),
                             mimetype='image/jpeg')

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
            file_id = fs.put(uploaded_file.read(),
                             filename=uploaded_file.filename)

            # You can associate the file_id with a specific user in your database
            # For example, if you have a user profile with an 'image_id' field:
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


def allowed_file(filename):
    # Define the allowed file extensions (e.g., for images)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


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
                print(profile_url)
                return jsonify({"success": True, 'Default': False, "profile_url": profile_url})

        return jsonify({"success": False, "message": "Profile image not found for this user."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/remove_profile_image', methods=['POST'])
def remove_profile_image():
    try:
        # Get the user's email (or any unique identifier) from the session or request
        # Replace with your actual session data retrieval
        email = session.get('email')

        # Check if the user has a profile picture in the database
        # Assuming you have a 'UserData' collection with a field 'image_id'
        user_data = db.UserData.find_one({"Email": email})
        if user_data and "image_id" in user_data:
            # Delete the profile picture from your database (MongoDB GridFS, for example)
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


@app.route('/', methods=['GET'])
def index():
  return render_template('Home.html')



@app.route('/Register',methods=['POST'])
def Register_user():
  Recieved=request.get_json()
  gender=Recieved.get('Gender','')
  name=Recieved.get('Name','')
  if(len(name)<4 or len(name)>30):
    abort(404)
  if gender=='male':
    Recieved.update(
        {"Defualt_Profile": True, 'Profile_Url': 'https://img.freepik.com/free-psd/3d-illustration-person-with-sunglasses_23-2149436188.jpg'})
  elif gender=='female':
    Recieved.update({"Defualt_Profile": True,
                    'Profile_Url': 'https://img.freepik.com/free-psd/3d-illustration-person-with-glasses_23-2149436185.jpg'})
  else:
    Recieved.update({"Defualt_Profile": False,
                    'Profile_Url': '650ed668b0d448411c3e2e50'})
  
  Recieved.update(
      {'IsAdmin':False,'RegistrationDate': datetime.now(), 'Address': ' '})
  db.UserData.insert_one(Recieved)
  return jsonify("Sucesss")
  
  
  
  
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

        return 'ok',200
      
    else:
        abort(404)

  
  
  
  
@app.route('/Find_user',methods=['POST'])
def find_user():
  Recieved = request.get_json()
  User=db.UserData.find_one(Recieved)
  if User:
    return 'ok',200
  abort(404)
  
@app.route('/Get_user_details',methods=['POST'])
def get_data():
  return find_user()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    # Simplified authentication (replace with your authentication logic)
    user = db.UserData.find_one({"Email": email})
    if user:
        session['email'] = email 
        # Store user's email in the session
        # Redirect to the profile page upon successful login
        return 'ok',200
    else:
        return redirect(url_for('Log_in')) # Return an appropriate response for failed login



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
        if user:
            # Render the profile template with user data
            return render_template('Account.html', user=user)
        else:
            return jsonify("User not found")
    else:
        print("session empty")
        return redirect(url_for('Log_in'))


@app.route('/Check_login', methods=['GET'])
def check_login():
    if 'email' in session:
        return "ok",200
    else:
        abort(404)

if __name__ == "__main__":
    app.run(port=8080,debug=True)

