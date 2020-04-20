from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from werkzeug.utils import secure_filename
from datetime import datetime

bp =  Blueprint('urlshort',__name__)

@bp.route('/')

def home():
    #homepage with cookies of created short names
    return render_template('home.html',session=session, short_names=session.keys())

@bp.route('/your-url',methods = ['GET','POST'])

def your_url():
    if request.method == 'POST':
        urls = {}
        #if json file that stores urls exists, load it into dictionary
        if os.path.exists ("urls.json"):
            with open("urls.json") as url_file:
                urls = json.load(url_file)
        #redirect to home page if there are conflicting entries
        if request.form['short_name'] in urls.keys():
            flash("This short name has already been taken. Please select another short name.")
            return redirect(url_for("urlshort.home"))
        #create new entry in the urls dictionary and save it to json file
        if 'url' in request.form.keys(): #for entries that are urls
            urls[request.form['short_name']] = {'url': request.form['url']}

        else:         #for entries that are files
            f = request.files['file']
            full_name = request.form['short_name'] + secure_filename(f.filename)
            f.save("/Users/chidoan/Desktop/url-shortener/urlshort/static/user_files/" + full_name)
            urls[request.form['short_name']] = {'file':full_name}


        with open("urls.json","w") as url_file:
            json.dump(urls,url_file)
            #store created short names for cookies
            session[request.form['short_name']] = datetime.now().strftime('%Y-%m-%d  %H:%M')
        return render_template('your-url.html', short_name = request.form['short_name'])
    else:
        return redirect(url_for("urlshort.home"))

@bp.route('/<string:short_name>')
#redirect from '/{short name}' to its full url
def redirect_to_url(short_name):
    if os.path.exists("urls.json"):
        with open("urls.json") as url_file:
            urls = json.load(url_file)
            if short_name in urls.keys():
                if "url" in urls[short_name].keys():
                    return redirect(urls[short_name]["url"])
                else:
                    return redirect(url_for('static',filename = 'user_files/' + urls[short_name]['file']))
    return abort(404)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'),404

@bp.route('/api')
def session_api():
    return jsonify(list(session.keys(),session.values()))
