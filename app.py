import os
import json
import pickle
import numpy as np
import pandas as pd
import plotly
import plotly.express as px
from flask import Flask, redirect, render_template, flash, request, jsonify, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_required, logout_user, login_user, LoginManager, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from groq import Groq

# Try to import joblib for better sklearn model loading
try:
    import joblib
    USE_JOBLIB = True
except ImportError:
    USE_JOBLIB = False 

# --- App Configuration ---
app = Flask(__name__, 
            static_url_path='', 
            static_folder='static', 
            template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "tandrima"
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Groq Configuration (NEW KEY UPDATED) ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --- Load Machine Learning Models ---
# Numerical stress detection model
model = None
try:
    if USE_JOBLIB:
        try:
            model = joblib.load('stresslevel.pkl')
            print("✅ Numerical stress model loaded successfully (joblib)")
        except:
            model = pickle.load(open('stresslevel.pkl', 'rb'))
            print("✅ Numerical stress model loaded successfully (pickle)")
    else:
        model = pickle.load(open('stresslevel.pkl', 'rb'))
        print("✅ Numerical stress model loaded successfully (pickle)")
except FileNotFoundError:
    print(f"⚠️ Stress model file 'stresslevel.pkl' not found")
    model = None
except Exception as e:
    print(f"⚠️ Error loading stress model: {e}")
    print("⚠️ This may be due to sklearn version incompatibility. Try retraining the model.")
    model = None

# Text-based stress detection model
text_model = None
text_vectorizer = None
try:
    if os.path.exists('stresslevel_text_model.pkl') and os.path.exists('stresslevel_text_vectorizer.pkl'):
        if USE_JOBLIB:
            try:
                text_model = joblib.load('stresslevel_text_model.pkl')
                text_vectorizer = joblib.load('stresslevel_text_vectorizer.pkl')
                print("✅ Text-based stress model loaded successfully (joblib)")
            except:
                text_model = pickle.load(open('stresslevel_text_model.pkl', 'rb'))
                text_vectorizer = pickle.load(open('stresslevel_text_vectorizer.pkl', 'rb'))
                print("✅ Text-based stress model loaded successfully (pickle)")
        else:
            text_model = pickle.load(open('stresslevel_text_model.pkl', 'rb'))
            text_vectorizer = pickle.load(open('stresslevel_text_vectorizer.pkl', 'rb'))
            print("✅ Text-based stress model loaded successfully (pickle)")
    else:
        print("ℹ️ Text-based stress model files not found. Run 'python train_text_model.py' to create them.")
except Exception as e:
    print(f"⚠️ Error loading text-based stress model: {e}")
    text_model = None
    text_vectorizer = None

# --- Database Model ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(20), unique=True)
    pas = db.Column(db.String(1000))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Authentication Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        usn = request.form.get('usn')
        pas = request.form.get('pas')
        if User.query.filter_by(usn=usn).first():
            flash("UserID is already taken", "warning")
            return render_template("usersignup.html")
        new_user = User(usn=usn, pas=generate_password_hash(pas))
        db.session.add(new_user)
        db.session.commit()
        return render_template("userlogin.html")
    return render_template("usersignup.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        usn, pas = request.form.get('usn'), request.form.get('pas')
        user = User.query.filter_by(usn=usn).first()
        if user and check_password_hash(user.pas, pas):
            login_user(user)
            return redirect(url_for('home'))
        flash("Invalid Credentials", "danger")
    return render_template("userlogin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Feature Routes ---
@app.route('/music')
@login_required
def music(): return render_template('music.html')

@app.route('/quizandgame')
@login_required
def quizandgame(): return render_template('quizandgame.html')

@app.route('/exercises')
@login_required
def exercises(): return render_template('exercises.html')

@app.route('/analysis')
@login_required
def analysis():
    try:
        train_df = pd.read_csv('dreaddit-train.csv', encoding='ISO-8859-1')
        fig = px.pie(train_df, names='subreddit', title='Subreddit Distribution')
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('analysis.html', graphJSON=graphJSON)
    except:
        return "Analysis data not found."

# --- Stress Detection Routes ---
@app.route('/i', methods=['GET', 'POST'])
@login_required
def i():
    """Route for numerical stress detection (GET: show form, POST: process prediction)"""
    if request.method == 'POST':
        try:
            # Get form inputs
            rr = request.form.get('rr')  # Sleeping hours
            bp = request.form.get('bp')  # Blood pressure
            bo = request.form.get('bo')  # Respiration rate
            hr = request.form.get('hr')  # Heart rate
            
            # Validate inputs
            if not all([rr, bp, bo, hr]):
                return render_template('stress.html', prediction_text3="Please fill in all fields.")
            
            # Convert to float and validate ranges
            try:
                rr = float(rr)
                bp = float(bp)
                bo = float(bo)
                hr = float(hr)
            except ValueError:
                return render_template('stress.html', prediction_text3="Please enter valid numbers.")
            
            # Make prediction if model exists
            if model is None:
                return render_template('stress.html', prediction_text3="Model not available. Please contact administrator.")
            
            # Prepare input array for prediction (format: [sleeping_hours, blood_pressure, respiration_rate, heart_rate])
            input_data = np.array([[rr, bp, bo, hr]])
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Format result
            if prediction == 0 or prediction == '0' or str(prediction).lower() == 'no stress':
                result = "✅ Stress Level: Low/No Stress\nYou seem to be managing stress well. Keep up the good habits!"
            else:
                result = "⚠️ Stress Level: High Stress\nIt looks like you might be experiencing elevated stress. Consider:\n• Taking breaks and practicing relaxation\n• Getting adequate sleep\n• Consulting with a healthcare professional\n• Using our Music Therapy and Exercises features"
            
            return render_template('stress.html', prediction_text3=result)
            
        except Exception as e:
            print(f"Error in stress prediction: {e}")
            return render_template('stress.html', prediction_text3=f"Error processing request: {str(e)}")
    
    # GET request - show form
    return render_template('stress.html', prediction_text3="")

@app.route('/stress_text', methods=['GET', 'POST'])
@login_required
def stress_text():
    """Route for text-based stress detection (GET: show form, POST: process prediction)"""
    if request.method == 'POST':
        try:
            # Get text input
            text = request.form.get('text', '').strip()
            
            if not text:
                return render_template('stress_text.html', prediction_text3="Please enter some text to analyze.")
            
            # Make prediction if model exists
            if text_model is None or text_vectorizer is None:
                return render_template('stress_text.html', prediction_text3="Text-based stress detection model not available. Please use the numerical input method or contact administrator.")
            
            # Vectorize the text
            text_vectorized = text_vectorizer.transform([text])
            
            # Make prediction
            prediction = text_model.predict(text_vectorized)[0]
            
            # Get prediction probability if available
            try:
                prediction_proba = text_model.predict_proba(text_vectorized)[0]
                stress_prob = prediction_proba[1] if len(prediction_proba) > 1 else 0.5
            except:
                stress_prob = 0.5
            
            # Format result
            if prediction == 0 or prediction == '0':
                result = f"✅ Stress Level: Low/No Stress\n\nBased on your text, you appear to be managing stress well. The model detected {stress_prob*100:.1f}% probability of stress indicators.\n\nKeep up the positive coping strategies!"
            else:
                result = f"⚠️ Stress Level: High Stress Detected\n\nThe model detected {stress_prob*100:.1f}% probability of stress indicators in your text.\n\nSuggestions:\n• Consider our Music Therapy feature for relaxation\n• Try our Exercises section for stress relief\n• Practice mindfulness and deep breathing\n• Consider speaking with a healthcare professional\n• Remember: It's okay to ask for help"
            
            return render_template('stress_text.html', prediction_text3=result)
            
        except Exception as e:
            print(f"Error in text-based stress prediction: {e}")
            return render_template('stress_text.html', prediction_text3=f"Error processing request: {str(e)}")
    
    # GET request - show form
    return render_template('stress_text.html', prediction_text3="")

@app.route('/stressdetect', methods=['POST'])
@login_required
def stressdetect():
    """Alternative route name for POST requests from stress.html form"""
    return i()

@app.route('/stressdetect_text', methods=['POST'])
@login_required
def stressdetect_text():
    """Route name for POST requests from stress_text.html form"""
    return stress_text()

# --- CHAT ROUTE (Fixed 302 and AI logic) ---
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'reply': 'Empty message.'})

        # Safety Check
        if any(word in user_message.lower() for word in ['suicide', 'kill']):
            return jsonify({'reply': "Please contact 988 Crisis Line immediately."})

        # Groq Call
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are MindEase, a supportive mental health assistant. Give short responses."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = completion.choices[0].message.content
            return jsonify({'reply': reply})
        except Exception as api_err:
            print(f"API Error: {api_err}")
            return jsonify({'reply': "Connection failed. Please check your internet or API key."})

    except Exception as e:
        return jsonify({'reply': "System error. Please try again."})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)