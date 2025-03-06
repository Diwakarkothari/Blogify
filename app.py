from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, TextAreaField, SelectMultipleField, StringField
from wtforms import PasswordField, EmailField, URLField
from wtforms.validators import InputRequired, Email, Length, EqualTo
import os
from medium import Client
import requests
import json
from checkForLogin import login_required


# AI Related
import google.generativeai as genai

genai.configure(api_key="AIzaSyA_CaLGBaewkhIu4ez5vgolg5lYQUAa6p4")
# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 1000,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
)

mutation = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post{
     id
     slug
    }
  }
}
"""
# output mein jo chahiye wo milega
# post{slug}  slug apan ko title dega jiski help se url banayenge


app = Flask(__name__)
app.config.from_object('config.Config')
app.config['SECRET_KEY'] = 'supersecretkey'  # GET and POST ko use ke liye lagana jaruri hai


class UploadForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    title = TextAreaField("Title", validators=[InputRequired()])
    platforms = SelectMultipleField("Choose Platforms  [ctrl+click to select multiple platforms]",
                                    choices=[('med', 'Medium'), ('dev', 'DevCommunity'), ('hn', 'HashNode')],
                                    validators=[InputRequired()])
    # Medium frontend pe dikhayi dega  med backend mein use aayega
    image_url = URLField(label="Upload image url")
    submit = SubmitField("Submit")


class UploadForm2(FlaskForm):
    platforms = SelectMultipleField("Choose Platforms  [ctrl+click to select multiple platforms]",
                                    choices=[('med', 'Medium'), ('dev', 'DevCommunity'), ('hn', 'HashNode')],
                                    validators=[InputRequired()])
    # Medium frontend pe dikhayi dega  med backend mein use aayega
    image_url = URLField(label="Upload image url")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), InputRequired()])
    email_address = EmailField(label='Email Address', validators=[Email(), InputRequired()])
    password1 = PasswordField(label='password:', validators=[Length(min=6), InputRequired()])
    password2 = PasswordField(label='confirm password:', validators=[EqualTo('password1'), InputRequired()])
    submit = SubmitField(label='Create account')


class DetailsForm(FlaskForm):
    dev_api = StringField(label="Dev.to API Key", validators=[InputRequired()])
    medium_access_key = StringField(label="Medium Integration Token", validators=[InputRequired()])
    hashnode_api = StringField(label="HashNode Access Key", validators=[InputRequired()])
    hashnode_publication_id = StringField(label="Hashnode Publication ID", validators=[InputRequired()])
    submit = SubmitField(label='Create Account')


class LoginForm(FlaskForm):
    username = StringField(label="Enter username", validators=[InputRequired()])
    password = PasswordField(label="Enter Password", validators=[InputRequired()])
    submit = SubmitField(label='Log-in')


class AiForm(FlaskForm):
    title = TextAreaField("Title", validators=[InputRequired()])
    submit = SubmitField(label='Generate Article')


class EditArticleForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])
    submit = SubmitField("Save")


def getArticle(title):
    str1 = "Give me an article on " + title
    response = model.start_chat().send_message(str1)
    return response.text


# dev.to
def create_post(title, content, dev_token, image_url):
    # dev.to
    api_key = dev_token  # api ko access karne ki key
    url_site = "https://dev.to/api/articles"  # api ka endpoint post karne ke liye

    headers = {
        "content-type": "application/json",  # header of HTTP batayega ki data json format mein hai
        "api-key": api_key  # client server connection ko complete karne ke liye
    }  # server ko access karne k password ek tareeke ka

    if image_url:
        data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": True,  # publish Draft ->False
                "main_image": image_url
            }
        }
    else:
        data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": True,  # publish Draft ->False
            }
        }
    response = requests.post(url=url_site, json=data, headers=headers)
    response.raise_for_status()  # exception raise karega
    # return response.json()["url"]  # dictionary ka element chahiye url


# medium
def publish_post_md(title, x, token):
    # medium
    # TOKEN = '257c07e5d5fcda561f1188087769b63275c597a3836b8141efcb9e9b16d5f1fd8'
    client = Client(access_token=token, application_id=None, application_secret=None)
    user = client.get_current_user()  # dictionary return hogi
    # print(user)
    post = client.create_post(user_id=user["id"], title=title, content=x, content_format="markdown",
                           publish_status='draft')


def upload_on_hashnode(title_article, data, hashnode_token, hashnode_publication_id, image_url):
    # hashnode
    access_token = hashnode_token
    hashnode_url = "https://gql.hashnode.com/"

    hashnode_header = {
        "Content-Type": "application/json",  # header of HTTP batayega ki data json format mein hai
        "Authorization": access_token  # client server connection ko complete karne ke liye
    }  # server ko access karne k password ek tareeke ka

    if image_url:
        variables = {
            "input": {
                "title": title_article,
                "contentMarkdown": data,
                "publicationId": hashnode_publication_id,
                "tags": [],
                "coverImageURL": image_url
            }
        }
    else:
        variables = {
            "input": {
                "title": title_article,
                "contentMarkdown": data,
                "publicationId": hashnode_publication_id,
                "tags": []
            }
        }

    hashnode_data = {
        "query": mutation,
        "variables": variables
    }  # json.dumps() ->python data ko convert karta hai
    response = requests.post(hashnode_url, headers=hashnode_header, data=json.dumps(hashnode_data))  # json mein
    # response.raise_for_status()


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')


@app.route('/details', methods=['GET', 'POST'])
def details():
    form = DetailsForm()
    if form.validate_on_submit():
        dev_token = form.dev_api.data
        med_token = form.medium_access_key.data
        hashnode_key = form.hashnode_api.data
        hashnode_publication_id = form.hashnode_publication_id.data

        with open("database.json", "r") as file:
            data = json.load(file)

        demo = {
            "dev_token": dev_token,
            "med_token": med_token,
            "hashnode_key": hashnode_key,
            "hashnode_publication_id": hashnode_publication_id
        }
        data[session['username']].update(demo)
        with open("database.json", "w") as file:
            json.dump(data, file, indent=4)
        return redirect('home')
    return render_template('details.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email_address = form.email_address.data
        password = form.password1.data
        with open("database.json", "r") as file:
            data = json.load(file)

        if username in data:
            return "Username already exists. Please choose a different one."

        data[username] = {
            "email_address": email_address,
            "password": password
        }
        session['username'] = username
        with open("database.json", "w") as file:
            json.dump(data, file, indent=4)
        return redirect(url_for('details'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        with open("database.json", "r") as file:
            data = json.load(file)
        if username in data and data[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('choose'))
        else:
            return "Login credentials wrong"
    return render_template('login.html', form=form)


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = file.filename
        title = form.title.data
        blog_site = form.platforms.data
        image_url = form.image_url.data
        if filename and title:
            file_ext = os.path.splitext(filename)[1]
            if file_ext.lower() in ['.md']:
                content = file.read().decode('utf-8')  # medium-no need    dev.to- needed
                with open("database.json", "r") as file:
                    data = json.load(file)
                if 'dev' in blog_site:
                    dev_token = data[session['username']]['dev_token']
                    create_post(title, content, dev_token, image_url)
                if 'med' in blog_site:
                    med_token = data[session['username']]['med_token']
                    publish_post_md(title, content, med_token)
                if 'hn' in blog_site:
                    hashnode_token = data[session['username']]['hashnode_key']
                    hashnode_publication_id = data[session['username']]['hashnode_publication_id']
                    upload_on_hashnode(title, content, hashnode_token, hashnode_publication_id, image_url)
                return redirect(url_for('result'))
            else:
                return "Invalid file extension. Only .md files are allowed."
    return render_template('base.html', form=form)


@app.route('/home2', methods=['GET', 'POST'])
@login_required
def home2():
    form = UploadForm2()
    if form.validate_on_submit():
        blog_site = form.platforms.data
        image_url = form.image_url.data
        title = request.args.get('title')
        content = request.args.get('content')
        with open("database.json", "r") as file:
            data = json.load(file)
        if 'dev' in blog_site:
            dev_token = data[session['username']]['dev_token']
            create_post(title, content, dev_token, image_url)
        if 'med' in blog_site:
            med_token = data[session['username']]['med_token']
            publish_post_md(title, content, med_token)
        if 'hn' in blog_site:
            hashnode_token = data[session['username']]['hashnode_key']
            hashnode_publication_id = data[session['username']]['hashnode_publication_id']
            upload_on_hashnode(title, content, hashnode_token, hashnode_publication_id, image_url)
        return redirect(url_for('result'))
    return render_template('aiUpload.html', form=form)


@app.route('/choose', methods=['GET', 'POST'])
@login_required
def choose():
    return render_template('choose.html')


@app.route('/editai', methods=['GET', 'POST'])
@login_required
def editai():
    title = request.args.get('title')
    content = request.args.get('content')
    form = EditArticleForm(title=title, content=content)
    if form.validate_on_submit():
        titlenew = form.title.data
        contentnew = form.content.data
        return redirect(url_for('home2', title=titlenew, content=contentnew))
    return render_template('editai.html', form=form)


@app.route('/aichat', methods=['GET', 'POST'])
@login_required
def aichat():
    form = AiForm()
    if form.validate_on_submit():
        title = form.title.data
        content = getArticle(title)
        if content and title:
            return redirect(url_for('editai', title=title, content=content))

    return render_template('aichat.html', form=form)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main'))


@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('result.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# docker build -t flask:latest .
# docker run -i -p 5000:5000 -d flask
# docker ps
# docker logs CONTAINER_ID
# /home/Diwakar810/mysite/database.json

