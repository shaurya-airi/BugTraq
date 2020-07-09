from app import app, db
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from app.models import User, Project, Component, ComponentRelation, Assignee, Reporter, FixVersion, CC, Bug, Status, IssueType, Priority
from datetime import datetime

def jsonify_sqlalchemy(sqlalchemy_object):
    all = sqlalchemy_object.query.all()
    print(jsonify(json_list= [repr(x) for x in all]))
    return jsonify(json_list= [repr(x) for x in all])

def project():
    Project(project_id=1, title="BugTraq", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1)).save()
    Project(project_id=2, title="Content Aggregator", description="Social Media Content Aggregation Application", start=datetime(2020,7,1), end=datetime(2020,10,1)).save()
    return jsonify_sqlalchemy(Project)

def component():
    Component(component_id=1, name="Database", project_id=1).save()
    Component(component_id=2, name="Icon", project_id=1).save()
    Component(component_id=3, name="Images", project_id=1).save()
    return jsonify_sqlalchemy(Component)

def status():
    Status(status_id=1, status="NEW").save()
    Status(status_id=2, status="ASSIGNED").save()
    Status(status_id=3, status="ACCEPTED").save()
    Status(status_id=4, status="FIXED").save()
    Status(status_id=5, status="FIXED(Verified)").save()
    Status(status_id=6, status="WON'T FIX (Not reproducible)").save()
    Status(status_id=7, status="WON'T FIX ((Intended behavior)").save()
    Status(status_id=8, status="WON'T FIX (Obsolete)").save()
    Status(status_id=9, status="WON'T FIX (Infeasible)").save()
    Status(status_id=10, status="DUPLICATE").save()
    return jsonify_sqlalchemy(Status)

def issue_type():
    IssueType(issue_type_id=1, issue_type="Feature").save()
    IssueType(issue_type_id=2, issue_type="Bug").save()
    IssueType(issue_type_id=3, issue_type="Task").save()
    IssueType(issue_type_id=4, issue_type="Maintenance").save()
    IssueType(issue_type_id=5, issue_type="Support").save()
    return jsonify_sqlalchemy(IssueType)

def user():
    return jsonify_sqlalchemy(User)

def fix_version():

    FixVersion(version="0.1.1", updated_at=datetime.now()).save()
    FixVersion(version="0.1.2", updated_at=datetime.now()).save()
    return jsonify_sqlalchemy(FixVersion)

def priority():
    Priority(pid=1, priority="P0").save()
    Priority(pid=2, priority="P1").save()
    Priority(pid=3, priority="P2").save()
    Priority(pid=4, priority="P3").save()
    Priority(pid=5, priority="P4").save()
    return jsonify_sqlalchemy(Priority)


def reporter():
    Reporter(user_id=3).save()
    return jsonify_sqlalchemy(Reporter)

def assignee():
    Assignee(user_id=3).save()
    return jsonify_sqlalchemy(Assignee)

def bug():
    summary = "Checking addition of the first bug after database design is completed"
    description = "Manually added priority, status, issue_types, fix_version, assignee, reporter entries to the BugTraq.db so that Bug could be added."
    Bug(bug_id=1, summary=summary, description= description, status_id=2, issue_type_id=1, pid=2, version="0.1.1", reporter_id=3, assignee_id=3, creator_id=3, project_id=1).save()
    return jsonify_sqlalchemy(Bug)