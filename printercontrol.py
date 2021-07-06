from flask import Flask
from flask import request
from flask import render_template
import sys
import os

app = Flask(__name__, template_folder='temp')

@app.route("/", methods=["GET","POST"])
def upload_analyze():
    if request.method == "POST":
        print(os.system('dir'))
        return render_template('test2.html')
    return render_template('test1.html')
    
if __name__ == "__main__":
    app.run(port=40000, debug=True)      