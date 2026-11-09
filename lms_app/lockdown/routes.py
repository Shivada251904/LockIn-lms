from flask import render_template, session, redirect, url_for, flash
from . import lockdown_bp
from lms_app.auth.jwt_utils import call_auth


@lockdown_bp.route("/", methods=["GET"])
def lockdown_home():
    if "user_id" not in session:
        return redirect(url_for("users.sign_in_page"))
    
    if session.get("role") != "student":
        flash("Access Denied: The Lockdown workspace is restricted to student assessment.", "danger")
        return redirect(url_for("users.lms_dashboard"))

    return render_template(
        "lockdown.html",
        mode="preview"
    )


@lockdown_bp.route("/soft", methods=["GET"])
def soft_lockdown():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("users.sign_in_page"))

    return render_template(
        "lockdown.html",
        mode="soft"
    )


@lockdown_bp.route("/hard", methods=["GET"])
def hard_lockdown():
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("users.sign_in_page"))

    return render_template(
        "hard_lockdown.html",
        mode="hard"
    )