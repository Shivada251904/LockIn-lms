from flask import jsonify
from . import lockdown_bp

@lockdown_bp.route("/test")
def test_lockdown():
    return jsonify({"message": "Lockdown blueprint working"})
