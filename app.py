from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Database Setup ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Model ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

# --- Home page: instructions ---
@app.route('/')
def home():
    return render_template('home.html')

# --- Visual Task Manager page ---
@app.route('/tasks')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title:
        new_task = Task(title=title)
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>')
def update_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.done = not task.done
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

# --- REST API endpoints remain unchanged ---
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return {"tasks": [t.__dict__ for t in tasks]}

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return task.__dict__
    return {"error": "Task not found"}, 404

@app.route('/api/tasks', methods=['POST'])
def api_add_task():
    data = request.get_json()
    new_task = Task(title=data['title'])
    db.session.add(new_task)
    db.session.commit()
    return new_task.__dict__, 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def api_update_task(task_id):
    data = request.get_json()
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    task.title = data.get('title', task.title)
    task.done = data.get('done', task.done)
    db.session.commit()
    return task.__dict__

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def api_delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {"error": "Task not found"}, 404
    db.session.delete(task)
    db.session.commit()
    return {"message": "Task deleted successfully"}

if __name__ == '__main__':
    app.run(debug=True)
