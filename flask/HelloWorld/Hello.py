from flask import Flask, redirect, url_for, render_template, make_response
from flask_restx import Api, Resource, fields

import os
app = Flask(__name__)
api = Api(app, version='1.0', title='GROW - ESG Analytics API')
ns = api.namespace('api')

@ns.route('/hello')
class HelloWorld(Resource):
   def get(self):
      return 'hello world'

@ns.route('/blog/<int:postID>')
class BlogNumber(Resource):
   def get(self, postID):
      return 'Blog Number %d' % postID

@ns.route('/admin')
class HelloAdmin(Resource):
   def get(self):
      return 'Hello Admin'

@ns.route('/guest/<guest>')
class HelloGuest(Resource):
   def get(self, guest):
      return 'Hello %s as Guest' % guest

@ns.route('/user/<name>')
class HelloUser(Resource):
   def get(self, name):
      if name =='admin':
         return redirect(url_for('hello_admin'))
      else:
         return redirect(url_for('hello_guest',guest = name))

@ns.route('/', doc=False)
@ns.route('/index', doc=False)
class IndexHtml(Resource):
   def get(self):
      headers = { 'Content-Type': 'text/html' }
      return make_response(render_template("index.html", user_image = '../static/projection_plot.png'), 200, headers)

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)