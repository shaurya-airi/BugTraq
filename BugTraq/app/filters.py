from app.models import User, Project, Component, Assignee, Reporter, FixVersion, CC, Bug, Status, IssueType, Priority
from sqlalchemy import or_, and_,desc
from flask import session

FILTER_FIELDS = ['Recently_Updated','Date_Created','Active_Features', 'Active_BUGS', 'ACCEPTED','FIXED','FIXED_or_FIXED(Verified)',f"Your_Issues"]
updated_date_filter = Bug.query.order_by(desc(Bug.updated_at)).all
created_date_filter = Bug.query.order_by(desc(Bug.created_at)).all
feature_filter = Bug.query.filter(and_(Bug.issue_type_id==1, Bug.status_id<=3)).all
bug_filter = Bug.query.filter(and_(Bug.issue_type_id==2, Bug.status_id<=3)).all
accepted_filter = Bug.query.filter_by(status_id=3).all
fixed_filter = Bug.query.filter_by(status_id=4).all
finished_filter = Bug.query.filter(or_(Bug.status_id==4, Bug.status_id==5)).all
# print(User.query.filter(username=session.get('username')).first())
# TODO: Add session user instead of hardcoded assignee_id
user_bugs = Bug.query.filter(and_(Bug.assignee_id==3, Bug.status_id<=3)).all

FILTERS = [updated_date_filter, created_date_filter, feature_filter, bug_filter, accepted_filter, fixed_filter, finished_filter, user_bugs]
FILTER_DICT = {}
for field, query in zip(FILTER_FIELDS, FILTERS):
    FILTER_DICT[field] = query