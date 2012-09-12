import os
import re
from string import letters
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'template')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir)
    ,autoescape = True)

form = """
<form method = "post">
    what is your name?
    <br>
    <label> Month
        <input type = "text" name= "name">
    </label>
    <input type = "submit">
</form>
"""

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class MainPage(webapp2.RequestHandler):
    def get(self):
      # self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(form)
    def post(self):
    	self.response.write(self.request)

class BaseHandler(webapp2.RequestHandler):
    """docstring for BaseHandler"""
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)
        

class Rot13(BaseHandler):
    def get(self):
        self.render('rot13-form.html')
    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
        self.render('rot13-form.html', text=rot13)

class Welcome(BaseHandler):
    def get(self):
        usr_name = self.request.get('username')
        if valid_username(usr_name):
            self.render('welcome.html', username = usr_name)
        else:
            self.redirect('/unit2/signup')

class Signup(BaseHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username, email = email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            print "error"
            self.render('signup-form.html', **params)
        else:
            self.redirect('/unit2/welcome?username=' + username)


        


app = webapp2.WSGIApplication([('/about', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Signup),
                               ( '/unit2/welcome', Welcome)],
                               debug=True)