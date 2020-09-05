import flask
from hashlib import md5
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.search import add_to_index, remove_from_index, query_index
from markdown import markdown
import bleach

class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name =  db.Column(db.String(80), nullable=False)
    email =  db.Column(db.String(100), unique=True, nullable=False)
    password =  db.Column(db.String(50), nullable=False)
    bugs = db.relationship('Bug', backref='creator', lazy=True)
    ccs = db.relationship('CC', backref='user', lazy=True)
    commments = db.relationship('Comment', backref='user', lazy=True)
    assignees = db.relationship('Assignee', backref='user', uselist=False, lazy=True)
    reporters = db.relationship('Reporter', backref='user', uselist=False, lazy=True)
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def avatar(self,size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

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


component_relation = db.Table('component_relation_table',
    db.Column('component_id',db.Integer, db.ForeignKey('component.component_id')),
    db.Column('bug_id',db.Integer, db.ForeignKey('bug.bug_id'))
)

class Component(db.Model):
    # project_id, title, description, start, end
    component_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    component_relation = db.relationship('Bug', secondary=component_relation, lazy='subquery', backref=db.backref('component', lazy=True) )
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Components %r>' % self.name


class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(40), nullable=False)
    bugs = db.relationship('Bug', backref='status', lazy=True)
    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<Status %r>' % self.status

class IssueType(db.Model):
    issue_type_id = db.Column(db.Integer, primary_key=True)
    issue_type = db.Column(db.String(40), nullable=False)
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


class BugSearchableMixin(object):
    @classmethod
    def search(cls, expression):
        ids, total = query_index(cls.__tablename__, expression)
        if total == 0:
            return cls.query.filter_by(bug_id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.bug_id.in_(ids)).order_by(
            db.case(when, value=cls.bug_id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, BugSearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, BugSearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, BugSearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


class Bug(BugSearchableMixin, db.Model):
    #TODO: Add searching comments
    __searchable__ = ['bug_id', 'summary', 'description', 'version']
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
    ccs = db.relationship('CC', backref='bug', lazy=True)
    comments = db.relationship('Comment', backref='bug', lazy='dynamic')


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


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    bug_id = db.Column(db.Integer, db.ForeignKey('bug.bug_id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<User %r, Bug %r, Comment %r>' % (self.user_id, self.bug_id, self.body)


db.event.listen(Comment.body, 'set', Comment.on_changed_body)

db.event.listen(db.session, 'before_commit', BugSearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', BugSearchableMixin.after_commit)