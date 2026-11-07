from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, json, os
from datetime import date

app = Flask(__name__)
app.jinja_env.filters["fromjson"] = json.loads
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB = os.path.join(os.path.dirname(__file__), "carnet_femme.db")

SECTIONS = {
    "identite": {"title":"Informations concernant la femme", "fields":[
        ("date_naissance","Date de naissance","date"),("nationalite","Nationalité","text"),
        ("cin","N° CIN","text"),("instruction","Niveau d’instruction","text"),
        ("profession","Occupation","text"),("telephone","Téléphone","tel"),
        ("contact_urgence","Personne à contacter en cas d’urgence","text"),
        ("medecin","Médecin traitant","text"),("groupe_sanguin","Groupe sanguin","select:A,B,AB,O"),
        ("rhesus","Rhésus","select:Positif,Négatif"),("allergies","Allergies / traitement suivi","textarea"),
        ("antecedents","Antécédents médicaux et chirurgicaux","textarea"),
        ("antecedents_familiaux","Antécédents familiaux","textarea"),
        ("couverture","Couverture médicale (AMO, RAMED, autre)","text")]},
    "vaccination": {"title":"Statut vaccinal", "fields":[
        ("vaccin","Vaccin","select:Antitétanique 1,Antitétanique 2,Antitétanique 3,Antitétanique 4,Antitétanique 5,Rubéole,Autre"),
        ("date","Date d’administration","date"),("dose","N° de prise / dose","text"),
        ("lieu","Lieu de vaccination","text"),("prestataire","Prestataire","text"),("notes","Observations","textarea")]},
    "prenuptial": {"title":"Examen prénuptial", "fields":[
        ("date","Date de l’examen","date"),("clinique","Résultats de l’examen clinique","textarea"),
        ("paraclinique","Résultats des examens complémentaires","textarea"),("medecin","Médecin / cachet","text")]},
    "planification": {"title":"Planification familiale", "fields":[
        ("date","Date de la visite","date"),("methode","Méthode contraceptive utilisée","text"),
        ("examen","Synthèse de l’examen clinique","textarea"),("decision","Décisions prises","textarea"),
        ("prestataire","Nom du prestataire","text")]},
    "grossesse": {"title":"Suivi de la grossesse", "fields":[
        ("numero","N° de grossesse","select:1,2,3,4,5,6+"),("date_regles","Date des dernières règles","date"),
        ("date_probable","Date probable de l’accouchement","date"),("date_visite","Date de la visite","date"),
        ("age_sa","Âge de grossesse (SA)","text"),("poids","Poids (kg)","number"),
        ("ta","Tension artérielle","text"),("sucre","Sucre","text"),("albumine","Albumine","text"),
        ("hemoglobine","Hémoglobine","text"),("bcf","BCF","text"),("hu","H.U","text"),
        ("clinique","Synthèse clinique","textarea"),("biologie","Examens biologiques","textarea"),
        ("echo","Examens échographiques / radiologiques","textarea"),("fer","Supplémentation en fer","text"),
        ("vitamine_d","Supplémentation en vitamine D","text"),("decision","Décision prise","textarea"),
        ("etablissement","Établissement sanitaire","text"),("prestataire","Prestataire","text")]},
    "accouchement": {"title":"Accouchement et post-partum", "fields":[
        ("date","Date de l’accouchement","date"),("lieu","Lieu","text"),
        ("mode","Mode","select:Voie basse,Voie haute"),("complications","Complications","textarea"),
        ("nouveau_ne","État du nouveau-né","select:Vivant,Mort-né,Décès inférieur à 24 h"),
        ("poids","Poids du nouveau-né (g)","number"),("anti_d","Immunoglobuline humaine ANTI-D","select:Oui,Non,Non concernée"),
        ("consultations","Consultations post-natales (sortie, J8, J40)","textarea"),
        ("observations","Observations / conseils","textarea")]},
    "cancers": {"title":"Dépistage des cancers du sein et du col de l’utérus", "fields":[
        ("type","Type de dépistage","select:Cancer du sein,Cancer du col de l’utérus"),
        ("date","Date du dépistage","date"),("resultat","Résultat du test de dépistage","textarea"),
        ("examens","Examens complémentaires","textarea"),("decision","Décisions ou traitements prescrits","textarea"),
        ("prestataire","Nom du prestataire de soins","text"),("prochain","Date du prochain contrôle","date")]},
    "consultations": {"title":"Synthèse des consultations médicales", "fields":[
        ("date","Date","date"),("examens","Synthèse des examens cliniques et paracliniques","textarea"),
        ("traitement","Traitement et décisions prises","textarea"),("medecin","Médecin / cachet","text")]},
    "chirurgie": {"title":"Interventions chirurgicales", "fields":[
        ("date","Date","date"),("diagnostic","Diagnostic","textarea"),("type","Type d’intervention","text"),
        ("lieu","Lieu d’intervention","text"),("medecin","Médecin traitant","text"),("evolution","Évolution","textarea")]},
    "chroniques": {"title":"Maladies chroniques", "fields":[
        ("date","Date du rendez-vous","date"),("examens","Synthèse des examens cliniques et paracliniques","textarea"),
        ("traitement","Traitement","textarea"),("medecin","Médecin / cachet","text")]},
    "menopause": {"title":"Suivi de la ménopause", "fields":[
        ("pre_menopause","Date d’apparition de la pré-ménopause","date"),
        ("menopause","Date d’apparition de la ménopause","date"),("date","Date de consultation","date"),
        ("manifestations","Manifestations cliniques","textarea"),("examens","Examens complémentaires","textarea"),
        ("traitement","Traitement","textarea")]}
}

def db():
    con=sqlite3.connect(DB)
    con.row_factory=sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK(id=1), nom TEXT, prenom TEXT, date_ouverture TEXT,
            adresse TEXT, telephone TEXT)""")
        con.execute("""CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT, section TEXT NOT NULL,
            payload TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
        con.execute("INSERT OR IGNORE INTO profile(id) VALUES(1)")

@app.route("/")
def index():
    init_db()
    with db() as con:
        profile=con.execute("SELECT * FROM profile WHERE id=1").fetchone()
        records=con.execute("SELECT * FROM records ORDER BY created_at DESC").fetchall()
    counts={key:sum(1 for r in records if r["section"]==key) for key in SECTIONS}
    return render_template("index.html", sections=SECTIONS, profile=profile, records=records,
                           counts=counts, active=request.args.get("section","identite"))

@app.post("/profile")
def save_profile():
    values=[request.form.get(k,"").strip() for k in ("nom","prenom","date_ouverture","adresse","telephone")]
    with db() as con:
        con.execute("UPDATE profile SET nom=?,prenom=?,date_ouverture=?,adresse=?,telephone=? WHERE id=1",values)
    flash("Fiche d’identité enregistrée.")
    return redirect(url_for("index",section="identite"))

@app.post("/add/<section>")
def add_record(section):
    if section not in SECTIONS: return redirect(url_for("index"))
    payload={key:request.form.get(key,"").strip() for key,_,_ in SECTIONS[section]["fields"]}
    if not any(payload.values()):
        flash("Veuillez renseigner au moins un champ.")
        return redirect(url_for("index",section=section))
    with db() as con:
        con.execute("INSERT INTO records(section,payload) VALUES(?,?)",(section,json.dumps(payload,ensure_ascii=False)))
    flash("Information ajoutée au carnet.")
    return redirect(url_for("index",section=section))

@app.post("/delete/<int:record_id>")
def delete_record(record_id):
    with db() as con: con.execute("DELETE FROM records WHERE id=?",(record_id,))
    flash("Entrée supprimée.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
