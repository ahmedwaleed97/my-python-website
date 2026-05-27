from flask import Flask, render_template, request, redirect, session, flash
import json, os
from functools import wraps

app = Flask(__name__)

# ─── CHANGE THESE ────────────────────────────────────────────
app.secret_key = "replace-with-something-random-abc123"
ADMIN_PASSWORD = "ahmed123456"
# ─────────────────────────────────────────────────────────────

CONTENT_FILE = "content.json"


def load_content():
    with open(CONTENT_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_content(data):
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/login")
        return fn(*args, **kwargs)
    return wrapper


# ── Public routes ─────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html", c=load_content())

@app.route("/skills")
def skills():
    return render_template("skills.html", c=load_content())

@app.route("/portfolio")
def portfolio():
    return render_template("portfolio.html", c=load_content())

@app.route("/contact")
def contact():
    return render_template("contact.html", c=load_content())


# ── Auth ──────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        flash("Wrong password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ── Admin ─────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html", c=load_content())


@app.route("/admin/save-hero", methods=["POST"])
@admin_required
def save_hero():
    c = load_content()
    c["name"]     = request.form["name"].strip()
    c["bio"]      = request.form["bio"].strip()
    c["roles"]    = [r.strip() for r in request.form["roles"].split(",") if r.strip()]
    c["tags"]     = [t.strip() for t in request.form["tags"].split(",")  if t.strip()]
    c["cv_url"]   = request.form["cv_url"].strip()
    c["email"]    = request.form["email"].strip()
    c["github"]   = request.form["github"].strip()
    c["linkedin"] = request.form["linkedin"].strip()
    save_content(c)
    flash("Hero section saved ✓")
    return redirect("/admin")


@app.route("/admin/save-projects", methods=["POST"])
@admin_required
def save_projects():
    c = load_content()
    titles  = request.form.getlist("title")
    descs   = request.form.getlist("desc")
    links   = request.form.getlist("link")
    techs   = request.form.getlist("tech")
    emojis  = request.form.getlist("emoji")
    photos  = request.form.getlist("photo")
    c["projects"] = [
        {
            "title": t,
            "desc":  d,
            "link":  l,
            "emoji": e,
            "photo": p,
            "tech":  [x.strip() for x in tc.split(",") if x.strip()]
        }
        for t, d, l, e, p, tc in zip(titles, descs, links, emojis, photos, techs)
        if t.strip()
    ]
    save_content(c)
    flash("Projects saved ✓")
    return redirect("/admin")


@app.route("/admin/save-skills", methods=["POST"])
@admin_required
def save_skills():
    c = load_content()
    try:
        skill_groups = json.loads(request.form["skills_json"])
        c["skill_groups"] = skill_groups
    except (KeyError, json.JSONDecodeError):
        flash("Error parsing skills — please try again.")
        return redirect("/admin")
    save_content(c)
    flash("Skills saved ✓")
    return redirect("/admin")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)