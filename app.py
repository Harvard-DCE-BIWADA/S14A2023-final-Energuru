from flask import Flask, request, render_template, redirect, url_for
import json
import os
import utils



app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')



@app.route('/form', methods=['GET', 'POST'])
def form():
    
    with open('allowed_choices.json', 'r') as file:
        allowed_choices = json.load(file)
    with open('columns.json', 'r') as file:
        columns = json.load(file)
    with open('col_descriptions.json', 'r') as file:
        col_descriptions = json.load(file)
    with open('inefficient_inputs.json', 'r') as file:
        inefficient_inputs = json.load(file)
    with open('average_inputs.json', 'r') as file:
        average_inputs = json.load(file)
    with open('efficient_inputs.json', 'r') as file:
        efficient_inputs = json.load(file)
    enterable_features = [col for col in columns[1:] if col not in allowed_choices]

    return render_template('form.html', 
                           allowed_choices = allowed_choices, 
                           enterable_features = enterable_features, 
                           inefficient_inputs = inefficient_inputs, 
                           average_inputs = average_inputs, 
                           efficient_inputs = efficient_inputs,
                           default_inputs = None if request.method == 'GET' else request.form.get('default_inputs')
                          )



@app.route('/results')
def results(user):
    with open('results.json', 'r') as file:
        results = json.load(file)
        return render_template('results.html', results=results)

@app.route('/results/<user>', methods=['GET', 'POST'])
def result(user):
    
    if request.method == 'GET':
        with open('results.json', 'r') as file:
            results = json.load(file)
        if user in results:
            prediction = results[user]['prediction']
            max_reductions = results[user]['max_reductions']
            return render_template('result.html', prediction=prediction, max_reductions=max_reductions)
        else:
            return f'No results for {user} in our database :('

    elif request.method == 'POST':
        with open('allowed_choices.json', 'r') as file:
            allowed_choices = json.load(file)
        args = request.form
        inputs = {key: value if key in allowed_choices else key: int(value) for key, value in args.items()}
        prediction, max_reductions = predict_and_advise(inputs)
        return render_template('result.html', prediction=prediction, max_reductions=max_reductions)

