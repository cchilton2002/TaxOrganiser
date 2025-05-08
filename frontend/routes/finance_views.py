from flask import Blueprint, render_template
from backend.database import DatabaseManager

finance_views = Blueprint('finance_views', __name__)

@finance_views.route("/upload")
def upload():
    return render_template("upload.html")

@finance_views.route("/summary/<int:user_id>")
def summary(user_id):
    db = DatabaseManager()
    summary = db.get_summaries(user_id)
    return render_template("summary.html", summaries=summary, user_id=user_id)