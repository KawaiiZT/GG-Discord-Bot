from flask import Flask, render_template, request
from oauth import Oauth

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html",discord_url= "Oauth.discord_login_url")

@app.route("/login")
def login():
    code = request.args.get("code")
    return "Success"
if __name__ == "__main__":
    app.run(debug=True)