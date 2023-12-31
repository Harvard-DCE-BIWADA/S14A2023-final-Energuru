from flask import Flask, request, render_template, redirect, url_for
import os
import json
import utils



app = Flask(__name__)



@app.route('/')
def home():
    return render_template('home.html')



@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/data')
def data():
    return render_template('data.html')



@app.route('/blog')
def blog():
    return render_template('blog.html')



@app.route('/form', methods=['GET', 'POST'])
def form0():
    if request.method == 'GET':
        return render_template('form0.html')
    elif request.method == 'POST':
        if os.path.exists('results.json'):
            with open('results.json', 'r') as file:
                results = json.load(file)
            if request.form['username'] in results:
                return redirect(url_for('result', username = request.form['username']))
        return redirect(url_for('form', username = request.form['username']))



@app.route('/form/<username>')
def form(username):
    if os.path.exists('results.json'):
        with open('results.json', 'r') as file:
            results = json.load(file)
        if username in results:
            return redirect(url_for('result', username = username))
                
    with open('model/allowed_choices.json', 'r') as file:
        allowed_choices = json.load(file)
    with open('model/columns.json', 'r') as file:
        columns = json.load(file)
    with open('model/col_descriptions.json', 'r') as file:
        col_descriptions = json.load(file)
    enterable_features = [col for col in columns[1:] if col.split(' / ')[0] not in allowed_choices]
    autofill = autofill_inputs = None
    
    autofill = request.args.get('autofill')
    if autofill and autofill != 'none':
        with open('model/' + autofill + '_inputs.json', 'r') as file:
            autofill_inputs = json.load(file)
            autofill_inputs = {key: value if key in allowed_choices else int(value) for key, value in autofill_inputs.items()}
    else:
        autofill_inputs = None
    
    metadata = {'allowed_choices': allowed_choices,
                'enterable_features': enterable_features,
                'col_descriptions': col_descriptions, 
                'options_for_autofill': {'inefficient': 'Sample inefficient dwelling unit', 
                                         'average': 'Sample average dwelling unit', 
                                         'efficient': 'Sample efficient dwelling unit'}, 
                'autofill': autofill if autofill != 'none' else None, 
                'autofill_inputs': autofill_inputs
               }
    return render_template('form.html', metadata=metadata, username=username)



@app.route('/results')
def results():
    with open('results.json', 'r') as file:
        results = json.load(file)
    graphsJSON = []
    for username, result in results.items():
        graphsJSON.append( utils.plot_results(username, result['prediction'], result['max_reductions']) )
    return render_template('results.html', graphsJSON=graphsJSON)



@app.route('/results/<username>', methods=['GET', 'POST'])
def result(username):

    if os.path.exists('results.json'):
        with open('results.json', 'r') as file:
            results = json.load(file)
    else:
        results = {}

    if request.method == 'GET':
        if username in results:
            result=results[username]
            graphJSON = utils.plot_results(username, result['prediction'], result['max_reductions'])
            return render_template('result.html', graphJSON=graphJSON)
        else:
            return f'No results for {username} in our database :('

    elif request.method == 'POST':  
        with open('model/allowed_choices.json', 'r') as file:
            allowed_choices = json.load(file)
        args = request.form.to_dict()
        inputs = {key: value if key in allowed_choices else int(value) for key, value in args.items()}
        prediction, max_reductions = utils.predict_and_advise(inputs)
        result = {'prediction': prediction, 
                  'max_reductions': max_reductions
                 }
        results[username] = result
        with open('results.json', 'w') as file:
            json.dump(results, file)

        graphJSON = utils.plot_results(username, prediction, max_reductions)

        return render_template('result.html', graphJSON=graphJSON)
    
