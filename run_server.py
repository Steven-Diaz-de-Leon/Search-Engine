from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_wtf.csrf import CSRFProtect

from SearchInterface import SearchInterface

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super secret passcode'
csrf = CSRFProtect(app)


class MyForm(FlaskForm):
    query = StringField('query', render_kw={"placeholder": "Search..."}, validators=[DataRequired()])


@app.route("/")
@app.route("/<search>")
def start(search=None):
    if search:
        terms = interface.getQuery(search)
        docs = interface.matchingDocuments(terms, "combinedIndex.txt")

        urls = interface.getURLs(docs)
        # doc_string = "document ids: " + ", ".join([d[0] for d in docs])
        dc_size = "number of matching documents: " + str(len(docs))
        url_string = "<br>".join(urls)
        return render_template("web.html", form=MyForm(), search=search, results=[dc_size, url_string])
    else:
        return render_template("web.html", form=MyForm(), search=None, results=None)


@app.route('/', methods=['POST'])
def submit():
    x = request.form["query"]
    return redirect(f'/{x}')


if __name__ == "__main__":
    interface = SearchInterface()
    app.run()
