from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Rezept(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titel = db.Column(db.String, nullable=True)
    anweisung = db.Column(db.String, nullable=True)
    hauptrezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), nullable=True)
    zutaten = db.relationship("Zutat", backref="rezept", lazy=True)
    schritte = db.relationship("RezeptSchritt", backref="rezept", lazy=True)
    bewertungen = db.relationship("Bewertung", backref="rezept", lazy=True)
    bilder = db.relationship("Bild", backref="rezept", lazy=True)
    tags = db.relationship(
        "Tag",
        secondary="rezept_tag",
        lazy="subquery",
        backref=db.backref("rezepte", lazy=True),
    )


class RezeptSchritt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), nullable=True)
    schritt_nummer = db.Column(db.Integer, nullable=True)
    anweisung = db.Column(db.String, nullable=True)


class Zutat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), nullable=True)
    menge = db.Column(db.String, nullable=True)
    einheit = db.Column(db.String, nullable=True)
    bezeichnung = db.Column(db.String, nullable=True)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bezeichnung = db.Column(db.String, nullable=True)


class Bewertung(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), nullable=True)
    sterne = db.Column(db.Integer, nullable=True)
    kommentar = db.Column(db.String, nullable=True)


class Bild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), nullable=True)
    path = db.Column(db.String, nullable=True)


class RezeptTag(db.Model):
    __tablename__ = "rezept_tag"
    rezept_id = db.Column(db.Integer, db.ForeignKey("rezept.id"), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tag.id"), primary_key=True)


def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
