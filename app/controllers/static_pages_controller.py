from flask import render_template

def home():
    return render_template('static_pages/home.html')

def help():
    return render_template('static_pages/help.html')
