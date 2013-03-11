import os
import re
from string import letters
import webapp2
import jinja2
import hashlib
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir)
    ,autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def render_post(response, post):
    response.out.write('<b>' + post.subject + '</b><br>')
    response.out.write(post.content)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw):
    salt = make_salt()
    s = "%s,%s" % (hashlib.sha256(name + pw + salt).hexdigest(), salt)
    return s
def valid_pw(name, pw, h):
    ###Your code here
    salt = h.split(",")[1]
    return (h.split(",")[0] == hashlib.sha256(name + pw + salt).hexdigest())

# h = make_pw_hash('spez', 'hunter2')
# print valid_pw('spez', 'hunter2', h)

SECRET = 'mySecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    s = h.split("|")[0]
    if ( h == make_secure_val(s)):
        return s


# webapp2.request is the generic request handler
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a,**kw)
    def render(self, template, **kw):
        self.write(render_str(template, **kw))
    def render_str(template, **params):
        return render_str(template, **params)

#unit 4
class Login(BlogHandler):
    def get(self):
        username_cookie = self.request.cookies.get('username')
        if username_cookie: 
            self.redirect('/blog/welcome?username=' + username_cookie)
        self.render("login.html", username = "longwei", password = "123")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        key = db.Key.from_path('account', str(username), parent=account_key())

        if key:
            self.write(key.id())
            self.write(key.name())
            self.write("**")
        else:
            self.write("can't find the key") 
        
        # self.write(key)  
        account = db.get(key)
        if account:
            self.write(account.toString())
        else:
            self.write("can't find the account") 
        # if account:
        #     # self.redirect('/blog/welcome?username=' + username)
        #     self.write("invalid account\n")
        # else:
        #     self.write("invalid account\n") 
        

class Account(db.Model):
    username = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty
    @classmethod
    def get_id(cls, uid):
        return Account.get_id
    def login(cls, name, pw):

class MainPage(BlogHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        self.write("Hello CS253\n") 
        visits_cookie_str = self.request.cookies.get('visits')
        if visits_cookie_str:
            cookies_val = check_secure_val(visits_cookie_str)
            self.write("***\n") 
            if cookies_val:
                visits = int(cookies_val)
        visits += 1
        new_cookie_val = make_secure_val(str(visits))
        self.response.headers.add_header('Set-Cookie', 'visits= %s' % new_cookie_val)
        if visits == 100005:
            self.write("You are the best") 
        else:
            self.write("You have been here for %s times" % visits) 

#blog unit3
#database
def blog_key(name = 'default'):
    return db.Key.from_path('blogs',name)
def account_key(name = 'default'):
    return db.Key.from_path('account',name)

# entity or table
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        # posts = Post.all().order('-created')
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return
        self.render("permalink.html", post = post)

class NewPost(BlogHandler):
    def get(self):
        self.render("newpost.html")
    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)


# Unit2
class Rot13(BlogHandler):
    def get(self):
        self.render('rot13-form.html')
    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
        self.render('rot13-form.html', text=rot13)

class Welcome(BlogHandler):
    def get(self):
        usr_name = self.request.get('username')
        if valid_username(usr_name):
            self.render('welcome.html', username = usr_name)
        else:
            self.redirect('/unit2/signup')

class Signup(BlogHandler):
    def get(self):
        username_cookie = self.request.cookies.get('username')
        if username_cookie: 
            self.redirect('/blog/welcome?username=' + username_cookie)
        self.render("signup-form.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username, email = email)

        if  self.usrname_used(username):
            params['error_username'] = "Username used."
            have_error = True

        if not valid_username(username) :
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
            u = Account(parent = account_key(), username = username, 
                    password = password, email = email)
            # TODO
            # make_pw_hash(username, password)
            u.put()
            self.response.headers.add_header('Set-Cookie', 'username= %s, Path=/' % str(username) )
            self.redirect('/blog/welcome?username=' + username)
    def usrname_used(self, un):
        u = db.GqlQuery("select * from Account where username = :1", un)
        return u.get()

class SearchPage(BlogHandler):
    def get(self):
        # self.response.out.write(form)
        self.render("play.html", 
            month = 1,
            day = 2,
            year = 3,
            error="no error")

class TestHandle(webapp2.RequestHandler):
    def get(self):
        q = self.request.get("q")
        self.response.out.write(q)
        # self.response.headers['Content-Type'] = 'text/plain'
        # self.response.out.write(self.request)
    def post(self):
        # q = self.request.get("q")
        # self.response.out.write(q)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write(self.request)
        self.redirect('/static/test.xls')


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)
        

# url mapping 
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/testform', TestHandle),
                               ('/unit4', MainPage),
                               ('/unit2/rot13', Rot13),
                               ('/blog/signup', Signup),
                               ('/blog/login', Login),
                               ('/blog/welcome', Welcome),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost)
                               ],
                               debug=True)