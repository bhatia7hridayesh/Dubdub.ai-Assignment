from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
#Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

ma = Marshmallow(app)

#MODELS

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    task = db.Column(db.String(250))
    completed = db.Column(db.Boolean, default=False)

    def __init__(self, task, completed):
        self.task = task
        self.completed = completed
    

db.init_app(app)
with app.app_context():
    db.create_all()
#Schemas

class TodoSchema(ma.Schema):
    class Meta:
        fields = ('id', 'task', 'completed')


todoSchema = TodoSchema()
allTasksSchema = TodoSchema(many=True)



"""
Endpoint to add a task
Req. body:
{
    "task": String,
    "completed": Bool
}
"""
@app.route('/add-task', methods=["POST"])
def create():
    task = request.json['task']
    completed = request.json['completed']

    new_task = Todo(task, completed)

    db.session.add(new_task)
    db.session.commit()

    return todoSchema.jsonify(new_task)


"""
Endpoint to view all tasks.
"""
@app.route('/', methods=["GET"])
def get_all_tasks():
    all_tasks = Todo.query.all()
    result = allTasksSchema.dump(all_tasks)

    return jsonify(result)

"""
next to endpoints can also be created as one to update either or both status and task .
"""

"""
Endpoint to Update status
"""
@app.route('/update-status/<id>', methods=['PUT'])
def update_status(id):
    try:
        task = Todo.query.get(id)

        task.completed = not task.completed
        """
        Can also use  by sending completed as true/false in request body :
        completed = request.json['completed']
        task.completed = completed
        """
        db.session.commit()
    
        return todoSchema.jsonify(task)
    except:
        return jsonify({"msg": f"Task with id {id} does not exist"})
"""
Endpoint to Update task 
"""
@app.route('/update-task/<id>', methods=["PUT"])
def update_task(id):
    updated_task = request.json["task"]
    try:
        todo = Todo.query.get(id)
        todo.task = updated_task
        db.session.commit()

        return todoSchema.jsonify(todo)
    except:
        return jsonify({"msg": f"Task with id {id} does not exist"})

"""
Endpoint to Delete task
"""
@app.route('/delete-task/<id>', methods=["DELETE"])
def delete_task(id):
    try:
        task = Todo.query.get(id)
        db.session.delete(task)
        db.session.commit()

        return jsonify({"msg": f"{task.task} task deleted"})
    except:
        return jsonify({"msg": f"Task with id {id} does not exist"})