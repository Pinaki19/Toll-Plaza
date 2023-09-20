from flask import Flask, jsonify, request, render_template, redirect, url_for, session,abort
from flask_pymongo import PyMongo
from pytz import timezone
from flask_cors import CORS
from datetime import datetime
from flask_session import Session

IST = timezone('Asia/Kolkata')

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/Users"
app.config['SECRET_KEY'] = 'ea5691dc5cddf9f9c4cc457e135e8b44066641c940cc5b6278e20afb2b1b'

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

mongo = PyMongo(app)
db = mongo.db
CORS(app)

@app.route('/', methods=['GET'])
def index():
  return render_template('Home.html')


@app.route('/Sign_up', methods=['GET'])
def Sign_up():
  return render_template("Sign_up.html")


@app.route('/Log_in',methods=['GET'])
def Log_in():
  return render_template('Log_in.html'),200

@app.route('/Register',methods=['POST'])
def Register_user():
  Recieved=request.get_json()
  Recieved.update(
      {'RegistrationDate': datetime.now()})
  db.UserData.insert_one(Recieved)
  return jsonify("Sucesss")
  
  
@app.route('/Find_user',methods=['POST'])
def find_user():
  Recieved = request.get_json()
  User=db.UserData.find_one_or_404(Recieved,{'_id':False})
  return jsonify(User)
  
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
        print(email)
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
    print("Profile route. Session email:", session.get('email'))
    if 'email' in session:
        # Retrieve the user's email from the session
        email = session.get('email')
        print(email)
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

