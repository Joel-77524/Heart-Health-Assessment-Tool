from flask import Flask, request, render_template, redirect, url_for, session
import pickle
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 

try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('scaler.pkl', 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
except FileNotFoundError as e:
    print(f"Error loading pickle files: {e}")
    print("Please make sure 'model.pkl' and 'scaler.pkl' are in the same directory as app.py")
    model = None
    scaler = None

@app.route('/')
def home():
    prediction_text = session.pop('prediction_text', None)
    risk_class = session.pop('risk_class', None)
    form_data = session.pop('form_data', {})
    
    return render_template('index.html', 
                           prediction_text=prediction_text,
                           risk_class=risk_class,
                           form_data=form_data)

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not scaler:
        session['prediction_text'] = "Error: Model or scaler not loaded. Check server logs."
        session['risk_class'] = 'high-risk'
        return redirect(url_for('home'))

    session['form_data'] = request.form

    try:
        feature_names = [
            'age', 'anaemia', 'creatinine_phosphokinase', 'diabetes',
            'ejection_fraction', 'high_blood_pressure', 'platelets',
            'serum_creatinine', 'serum_sodium', 'sex', 'smoking', 'time'
        ]
        
        features = [float(request.form[name]) for name in feature_names]
        
        final_features = np.array(features).reshape(1, -1)
        scaled_features = scaler.transform(final_features)
        
        prediction = model.predict(scaled_features)
        
        if prediction[0] == 1:
            session['prediction_text'] = "High risk of heart failure event detected. Immediate clinical attention recommended."
            session['risk_class'] = 'high-risk'
        else:
            session['prediction_text'] = "Low risk of heart failure event. Continue regular monitoring."
            session['risk_class'] = 'low-risk'

    except (ValueError, KeyError) as e:
        session['prediction_text'] = f"Invalid input. Please check all fields. Error: {e}"
        session['risk_class'] = 'high-risk'

    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)