import flask
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name =  db.Column(db.String(80), nullable=False)
    email =  db.Column(db.String(100), unique=True, nullable=False)
    password =  db.Column(db.String(50), nullable=False)
    bugs = db.relationship('Bug', backref='user', lazy=True)
    ccs = db.relationship('CC', backref='user', lazy=True)
    assignees = db.relationship('Assignee', backref='user', uselist=False, lazy=True)
    reporters = db.relationship('Reporter', backref='user', uselist=False, lazy=True)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.username


class Project(db.Model):
    # project_id, title, description, start, end
    project_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(80), nullable=False)
    start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end =  db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    components = db.relationship('Component', backref='project', lazy=True)
    bugs = db.relationship('Bug', backref='project', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Project %r>' % self.title


class Component(db.Model):
    # project_id, title, description, start, end
    component_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    component_relations = db.relationship('ComponentRelation', backref='component', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Components %r>' % self.name


class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(30), nullable=False)
    bugs = db.relationship('Bug', backref='status', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Status %r>' % self.status

class IssueType(db.Model):
    issue_type_id = db.Column(db.Integer, primary_key=True)
    issue_type = db.Column(db.String(30), nullable=False)
    bugs = db.relationship('Bug', backref='issue_type', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Issue_Type %r>' % self.issue_type

class Priority(db.Model):
    #TODO: Why use db with say 5 priorities
    pid = db.Column(db.Integer, primary_key=True)
    priority = db.Column(db.String(30), nullable=False)
    bugs = db.relationship('Bug', backref='priority', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Priority %r>' % self.priority

class FixVersion(db.Model):
    version = db.Column(db.String(30), primary_key=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bugs = db.relationship('Bug', backref='fix_version', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Version %r>' % self.version


class Reporter(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    bugs = db.relationship('Bug', backref='reporter', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Reporter %r>' % self.user_id

class Assignee(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    bugs = db.relationship('Bug', backref='assignee', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Assignee %r>' % self.user_id


class Bug(db.Model):
    bug_id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(72), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'), nullable=False)
    issue_type_id = db.Column(db.Integer, db.ForeignKey('issue_type.issue_type_id'), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('priority.pid'), nullable=False)
    version = db.Column(db.String(30), db.ForeignKey('fix_version.version'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('reporter.user_id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('assignee.user_id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    component_relations = db.relationship('ComponentRelation', backref='bug', lazy=True)
    ccs = db.relationship('CC', backref='bug', lazy=True)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Bug %r: %r><br><Description: %r>' % (self.bug_id, self.summary, self.description)

class CC(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.bug_id'), primary_key=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r, Bug %r>' % (self.user_id, self.bug_id)




class ComponentRelation(db.Model):
    component_id = db.Column(db.Integer, db.ForeignKey('component.component_id'), primary_key=True)
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.bug_id'), primary_key=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Component %r, Bug %r>' % (self.component_id, self.bug_id)

