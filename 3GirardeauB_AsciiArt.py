import webapp2
import logging
import re
import jinja2
import os
import time
from google.appengine.ext import db

## see http://jinja.pocoo.org/docs/api/#autoescaping
def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=guess_autoescape,     ## see http://jinja.pocoo.org/docs/api/#autoescaping
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def validateTitle(title):
    return title

def validateArt(art):
    return art

class MyHandler(webapp2.RequestHandler):
    def write(self, *items):    
        self.response.write(" : ".join(items))

    def render_str(self, template, **params):
        tplt = JINJA_ENVIRONMENT.get_template('templates/'+template)
        return tplt.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(MyHandler):
    def get(self):
        logging.info("********** MainPage GET **********")
        self.render_ascii()

    def render_ascii(self, title="", art="", error=""):
        logging.info(title)
        logging.info("********** MainPage RENDER **********")
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC ")
        self.render("ascii.html", title=title, art=art, error=error, arts=arts)

    def post(self):
        logging.info("********** MainPage POST **********")
        artInstance = Art()
        artInstance.title = self.request.get("title")
        artInstance.art = self.request.get("art")
        if artInstance.title and artInstance.art:
            artInstance.put()
            time.sleep(.1)
            self.redirect("/")
            id = artInstance.key().id()
            logging.info("*** ID of this Art is " + str(id))
        else:
            self.render_ascii(artInstance.title, artInstance.art, "Need both a title and some artwork!")

class FavoritePage(MyHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/favorite.html')
        self.response.write(template.render(favoriteArt=Art.get_by_id(6554239279038464).art, favoriteTitle=Art.get_by_id(6554239279038464).title))


class Art(db.Model):
    title = db.StringProperty()
    art = db.TextProperty()
    created = db.DateTimeProperty(auto_now_add = True)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/favorite', FavoritePage)
], debug=True)
