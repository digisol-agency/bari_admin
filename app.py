from flask import Flask, render_template, url_for, flash, redirect, abort


app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template("main.html")

@app.route('/login')
def login():
    return render_template("login.html")

if __name__ == "__main__":
	app.run(debug=True)
