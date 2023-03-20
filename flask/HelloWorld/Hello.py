from flask import Flask, redirect, url_for, render_template

import os
app = Flask(__name__)

@app.route('/hello')
def hello_world():
   return 'hello world'

@app.route('/blog/<int:postID>')
def show_blog(postID):
   return 'Blog Number %d' % postID

@app.route('/admin')
def hello_admin():
   return 'Hello Admin'

@app.route('/guest/<guest>')
def hello_guest(guest):
   return 'Hello %s as Guest' % guest

@app.route('/user/<name>')
def hello_user(name):
   if name =='admin':
      return redirect(url_for('hello_admin'))
   else:
      return redirect(url_for('hello_guest',guest = name))

@app.route('/')
@app.route('/index')
def show_index():
    return render_template("index.html", user_image = 'static/projection_plot.png')

if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug = True)