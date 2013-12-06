from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, render_template, flash, send_from_directory

from werkzeug import secure_filename
import os
from subprocess import Popen, PIPE
import json
import xlwt
import zipfile

app = Flask(__name__)

app.debug = True
app.secret_key = 'a42u208nI^*^SDF*&^SD*FP'
app.config['UPLOAD_FOLDER'] = '/srv/http/dash/tmp'

def connect_db():
  rv = sqlite3.connect('tag.db')
  rv.row_factory = sqlite3.Row
  return rv

def get_db():
  if not hasattr(g, 'sqlite_db'):
    g.sqlite_db = connect_db()
  return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
  if hasattr(g, 'sqlite_db'):
    g.sqlite_db.close()

def settings(key):
  db = get_db()
  cursor = db.execute('select value from settings where key = ?',[key])
  rows = cursor.fetchall()
  return rows[0]["value"]

@app.route('/')
def show_dash():
  return render_template('dash.html')

@app.route('/table')
def show_table():
  db = get_db()
  cursor = db.execute('select * from tags')
  rows = cursor.fetchall()
  return render_template('table.html', tags=rows)

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    if username == settings('dash_username') and password == settings('dash_password'):
      flash('You were logged in')
      session['logged_in'] = True
      return render_template('admin.html')
    else:
      return render_template('login.html', error="Invalid Username or Password")

  if 'logged_in' in session:
    return redirect(url_for('admin'))
  else:
    return render_template('login.html')

@app.route('/admin')
def admin():
  if 'logged_in' in session:
    return render_template('admin.html')
  else:
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
  if 'logged_in' in session:
    session.pop('logged_in', None)
    flash('You were logged out')

  return redirect(url_for('login'))

@app.route('/charts')
def show_charts():
  db = get_db()
  cursor = db.execute('select * from rssi')
  rows = cursor.fetchall()
  uptime = exec_cmd(["uptime"])
  timedate = exec_cmd(["timedatectl"])
  who = exec_cmd(["w", "-i"])
  return render_template('stats.html', rssi=rows, uptime=uptime, timedate=timedate, who=who)

def exec_cmd(cmd):
  process = Popen(cmd, stdout=PIPE)
  (output, err) = process.communicate();
  exit_code = process.wait()
  return output

@app.route('/upload', methods=['GET', 'POST'])
def upload():
  if request.method == 'POST':

    f = request.files['file']

    filename = secure_filename(f.filename)

    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # TODO pass csv,excel

    flash('Upload Succesful: ' + filename)

  return render_template('admin.html')

@app.route('/download/<filename>')
def download_tags(filename=None):

  if filename.endswith('.xls'):
    save_to_xls(filename)

  if filename.endswith('.zip'):
    save_to_xls("tags.xls")
    zip = zipfile.ZipFile(filename,'w')
    zip.write("tags.xls")
    zip.close()

  return send_from_directory('.', filename)

@app.route('/tags')
def get_tags():
  db = get_db()
  cursor = db.execute('select * from tags')
  rows = cursor.fetchall()
  objects = ()
  for row in rows:
    objects += ((row['id'],row['epoch'],row['time'],row['tag']),);
  return jsonify(result=objects)

@app.route('/rssi')
def get_rssi():
  db = get_db()
  cursor = db.execute('select * from rssi order by id desc limit 500')
  rows = cursor.fetchall()
  objects = ()
  for row in rows:
    objects += ((row['id'], row['value']),);
  return jsonify(result=objects)

def save_to_xls(filename):
  db = get_db()
  cursor = db.execute('select * from tags')
  rows = cursor.fetchall()
  ID = ()
  epoch = ()
  dates = ()
  tags = ()

  for row in rows:
    dates += (row['time'],)
    tags += (row['tag'],)
    ID += (row['id'],)
    epoch += (row['epoch'],)

  book = xlwt.Workbook()
  sh = book.add_sheet('sheet1')

  sh.write(0, 0, '#')
  sh.write(0, 1, 'Epoch')
  sh.write(0, 2, 'Date')
  sh.write(0, 3, 'Tag ID')

  for m, e0 in enumerate(ID, 1):
    sh.write(m, 0, e0)

  for m, e1 in enumerate(epoch, 1):
    sh.write(m, 1, e1)

  for m, e2 in enumerate(dates, 1):
    sh.write(m, 2, e2)

  for m, e3 in enumerate(tags, 1):
    sh.write(m, 3, e3)

  book.save(filename)

@app.route('/start_rssi')
def start_rssi():
  db = get_db()
  cursor = db.execute('update settings set value="true" where key = "rssi_active"')
  db.commit()
  return '',200

@app.route('/stop_rssi')
def stop_rssi():
  db = get_db()
  cursor = db.execute('update settings set value="false" where key = "rssi_active"')
  db.commit()
  return '',200

@app.route('/clear_rssi')
def clear_rssi():
  db = get_db()
  cursor = db.execute('delete from rssi')
  db.commit()
  return '',200
