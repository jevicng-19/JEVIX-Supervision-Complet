from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    session,
    jsonify
)

import mysql.connector

from mysql.connector import Error

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from datetime import datetime
from pathlib import Path


HEARTBEAT_TIMEOUT_SECONDS = 20
MAX_FUTURE_CLOCK_SKEW_SECONDS = 10


app = Flask(__name__)

secret_key_file = Path(__file__).with_name(".flask_secret")
if not secret_key_file.exists():
    raise RuntimeError(
        "Clé Flask absente. Lancez d'abord : python generer_cle_flask.py"
    )

app.secret_key = secret_key_file.read_text(encoding="ascii").strip()
if not app.secret_key:
    raise RuntimeError("Le fichier .flask_secret est vide. Régénérez la clé Flask.")


# Connexion à la base de données

def get_db():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="jevix"
    )


# Accueil

@app.route("/")
def accueil():

    if "user" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# Connexion

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user" in session:
        return redirect(url_for("dashboard"))

    erreur = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        cursor = db.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT id, username, password, role
            FROM administrateurs
            WHERE username = %s
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["user"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        erreur = "Nom d'utilisateur ou mot de passe incorrect."



    return render_template(
        "login.html",
        erreur=erreur
    )

# Verification des machines en ligne

def verifier_machines_hors_ligne():

    db = get_db()

    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT id, hostname, last_update FROM machines")

    machines = cursor.fetchall()

    for machine in machines:

        if machine["last_update"] is None:
            continue

        difference = (
            datetime.now() - machine["last_update"]
        ).total_seconds()

        if (
            difference > HEARTBEAT_TIMEOUT_SECONDS
            or difference < -MAX_FUTURE_CLOCK_SKEW_SECONDS
        ):

            creer_alerte(
                machine["id"],
                "MACHINE",
                "CRITIQUE",
                "OFFLINE",
                f"La machine {machine['hostname']} ne répond plus."
            )

        else:

            cursor.execute(
                """
                UPDATE alertes
                SET
                    statut='RESOLUE',
                    diagnostic='Machine revenue en ligne.',
                    date_resolution=NOW()
                WHERE machine_id=%s
                AND type='MACHINE'
                AND statut!='RESOLUE'
                """,
                (machine["id"],)
            )

    db.commit()

    cursor.close()

    db.close()

# Dashboard

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    verifier_machines_hors_ligne()

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    cursor.execute(
        "SELECT * FROM machines ORDER BY hostname"
    )

    machines = cursor.fetchall()

    cursor.close()
    db.close()

    online_count = 0
    total_health = 0

    for machine in machines:

        machine["online"] = False

        last_update = machine["last_update"]

        if last_update:

            difference = (
                datetime.now() - last_update
            ).total_seconds()

            if (
                -MAX_FUTURE_CLOCK_SKEW_SECONDS
                <= difference
                <= HEARTBEAT_TIMEOUT_SECONDS
            ):

                machine["online"] = True
                online_count += 1


        cpu = machine["cpu_percent"] or 0

        ram = machine["ram_used_percent"] or 0

        disk = machine["disk_used_percent"] or 0


        health = round(
            100 - ((cpu + ram + disk) / 3),
            1
        )


        if health < 0:
            health = 0

        if health > 100:
            health = 100


        machine["health"] = health

        total_health += health


    if len(machines) > 0:

        etat_general = round(
            total_health / len(machines),
            1
        )

    else:

        etat_general = 0


    return render_template(
        "dashboard.html",
        machines=machines,
        online_count=online_count,
        etat_general=etat_general,
        username=session["user"],
        role=session["role"]
    )

# Alertes

@app.route("/alertes")
def alertes():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    cursor.execute("""
        SELECT
            alertes.*,
            machines.hostname,
            administrateurs.username AS admin_nom
        FROM alertes

        INNER JOIN machines
            ON machines.id = alertes.machine_id

        LEFT JOIN administrateurs
            ON administrateurs.id = alertes.admin_id

        ORDER BY date_detection DESC
    """)
    liste_alertes = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alertes
        WHERE statut <> 'RESOLUE'
    """)
    total_alertes = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alertes
        WHERE gravite='CRITIQUE'
        AND statut <> 'RESOLUE'
    """)
    critiques = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alertes
        WHERE statut='EN_COURS'
    """)
    en_cours = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM alertes
        WHERE statut='RESOLUE'
    """)
    resolues = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return render_template(

    "alertes.html",

    alertes=liste_alertes,

    total_alertes=total_alertes,

    critiques=critiques,

    en_cours=en_cours,

    resolues=resolues,

    username=session["user"],

    role=session["role"]

)

# Notification des alertes

@app.context_processor
def inject_notification_alertes():

    if "user" not in session:

        return dict(notification_alertes=0)

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    cursor.execute(
        "SELECT COUNT(*) AS total FROM alertes WHERE statut='NOUVELLE'"
    )

    notification_alertes = cursor.fetchone()["total"]

    cursor.close()
    db.close()

    return dict(
        notification_alertes=notification_alertes
    )

# Prendre en charge une alerte

@app.route("/prendre-alerte/<int:id>")
def prendre_alerte(id):

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()

    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE alertes
        SET
            statut='EN_COURS',
            admin_id=%s,
            date_prise_en_charge=NOW()
        WHERE id=%s
        """,
        (
            session["user_id"],
            id
        )
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("alertes"))

# Résoudre une alerte

@app.route("/resoudre-alerte/<int:id>", methods=["GET", "POST"])
def resoudre_alerte(id):

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        diagnostic = request.form["diagnostic"]

        cursor.execute(
            """
            UPDATE alertes
            SET
                statut='RESOLUE',
                diagnostic=%s,
                date_resolution=NOW()
            WHERE id=%s
            """,
            (
                diagnostic,
                id
            )
        )

        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for("alertes"))

    cursor.execute(
        "SELECT * FROM alertes WHERE id=%s",
        (id,)
    )

    alerte = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "resoudre_alerte.html",
        alerte=alerte,
        username=session["user"],
        role=session["role"]
    )

# Profil

@app.route("/profil")
def profil():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "profil.html",
        username=session["user"],
        role=session["role"]
    )

@app.route("/modifier-profil", methods=["GET", "POST"])
def modifier_profil():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    cursor.execute(
        """
        SELECT *
        FROM administrateurs
        WHERE id=%s
        """,
        (session["user_id"],)
    )

    admin = cursor.fetchone()

    erreur = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        cursor.execute(
            """
            SELECT id
            FROM administrateurs
            WHERE username=%s
            AND id<>%s
            """,
            (
                username,
                session["user_id"]
            )
        )

        if cursor.fetchone():

            erreur = "Ce nom d'utilisateur existe déjà."

        else:

            if password.strip() == "":

                cursor.execute(
                    """
                    UPDATE administrateurs
                    SET username=%s
                    WHERE id=%s
                    """,
                    (
                        username,
                        session["user_id"]
                    )
                )

            else:

                password_hash = generate_password_hash(password)

                cursor.execute(
                    """
                    UPDATE administrateurs
                    SET
                        username=%s,
                        password=%s
                    WHERE id=%s
                    """,
                    (
                        username,
                        password_hash,
                        session["user_id"]
                    )
                )

            db.commit()

            session["user"] = username

            cursor.close()
            db.close()

            return redirect(url_for("profil"))

    cursor.close()
    db.close()

    return render_template(
        "modifier_profil.html",
        admin=admin,
        erreur=erreur,
        username=session["user"],
        role=session["role"]
    )

# À propos

@app.route("/apropos")
def apropos():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "apropos.html",
        username=session["user"],
        role=session["role"]
    )


# Administrateurs

@app.route("/admins")
def admins():

    if "user" not in session:
        return redirect(url_for("login"))

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    cursor.execute(
        """
        SELECT
            id,
            username,
            role,
            date_creation
        FROM administrateurs
        ORDER BY date_creation DESC
        """
    )

    liste_admins = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admins.html",
        admins=liste_admins,
        username=session["user"],
        role=session["role"]
    )

# Creer un administrateur

@app.route("/ajouter-admin", methods=["GET", "POST"])
def ajouter_admin():

    if "user" not in session:
        return redirect(url_for("login"))

    if session["role"] != "superadmin":
        return redirect(url_for("admins"))

    db = get_db()

    cursor = db.cursor(
        dictionary=True,
        buffered=True
    )

    erreur = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        cursor.execute(
            """
            SELECT id
            FROM administrateurs
            WHERE username=%s
            """,
            (username,)
        )

        if cursor.fetchone():

            erreur = "Ce nom d'utilisateur existe déjà."

        else:

            from werkzeug.security import generate_password_hash

            password_hash = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO administrateurs
                (
                    username,
                    password,
                    role
                )
                VALUES
                (%s,%s,%s)
                """,
                (
                    username,
                    password_hash,
                    role
                )
            )

            db.commit()

            cursor.close()
            db.close()

            return redirect(url_for("admins"))

    cursor.close()
    db.close()

    return render_template(
        "ajouter_admin.html",
        erreur=erreur,
        username=session["user"],
        role=session["role"]
    )

# Déconnexion

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# Alertes

def creer_alerte(machine_id, type_alerte, gravite, valeur, message):

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute(
        """
        SELECT id FROM alertes
        WHERE machine_id=%s
        AND type=%s
        AND statut!='RESOLUE'
        """,
        (machine_id, type_alerte)
    )

    if cursor.fetchone():
        cursor.close()
        db.close()
        return

    cursor.execute(
        """
        INSERT INTO alertes
        (machine_id,type,gravite,valeur,message)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (machine_id,type_alerte,gravite,str(valeur),message)
    )

    db.commit()
    cursor.close()
    db.close()

# Réception des données des agents

@app.route("/metrics", methods=["POST"])
def metrics():

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "Aucune donnée reçue"
        }), 400


    db = None
    cursor = None

    try:

        db = get_db()

        cursor = db.cursor(
            dictionary=True,
            buffered=True
        )


        cursor.execute(
            """
            SELECT id
            FROM machines
            WHERE hostname = %s
            """,
            (data["hostname"],)
        )


        machine = cursor.fetchone()


        if machine:

            sql = """
            UPDATE machines SET

                username = %s,
                ip = %s,

                os = %s,
                os_version = %s,
                architecture = %s,

                cpu_percent = %s,
                cpu_cores = %s,

                ram_total_gb = %s,
                ram_used_percent = %s,
                ram_available_gb = %s,

                disk_total_gb = %s,
                disk_used_percent = %s,
                disk_free_gb = %s,

                bytes_sent = %s,
                bytes_recv = %s,

                process_count = %s,

                battery_percent = %s,

                last_update = %s

            WHERE hostname = %s
            """


            values = (

                data["username"],
                data["ip"],

                data["os"],
                data["os_version"],
                data["architecture"],

                data["cpu_percent"],
                data["cpu_cores"],

                data["ram_total_gb"],
                data["ram_used_percent"],
                data["ram_available_gb"],

                data["disk_total_gb"],
                data["disk_used_percent"],
                data["disk_free_gb"],

                data["bytes_sent"],
                data["bytes_recv"],

                data["process_count"],

                data["battery_percent"],

                datetime.now(),

                data["hostname"]

            )


            cursor.execute(sql, values)


        else:

            sql = """
            INSERT INTO machines (

                hostname,
                username,
                ip,

                os,
                os_version,
                architecture,

                cpu_percent,
                cpu_cores,

                ram_total_gb,
                ram_used_percent,
                ram_available_gb,

                disk_total_gb,
                disk_used_percent,
                disk_free_gb,

                bytes_sent,
                bytes_recv,

                process_count,

                battery_percent,

                last_update

            )

            VALUES (

                %s, %s, %s,

                %s, %s, %s,

                %s, %s,

                %s, %s, %s,

                %s, %s, %s,

                %s, %s,

                %s,

                %s,

                %s

            )
            """


            values = (

                data["hostname"],
                data["username"],
                data["ip"],

                data["os"],
                data["os_version"],
                data["architecture"],

                data["cpu_percent"],
                data["cpu_cores"],

                data["ram_total_gb"],
                data["ram_used_percent"],
                data["ram_available_gb"],

                data["disk_total_gb"],
                data["disk_used_percent"],
                data["disk_free_gb"],

                data["bytes_sent"],
                data["bytes_recv"],

                data["process_count"],

                data["battery_percent"],

                datetime.now()

            )


            cursor.execute(sql, values)


        db.commit()

        machine_id = machine["id"] if machine else cursor.lastrowid

        if data["cpu_percent"] >= 95:
            creer_alerte(machine_id,"CPU","CRITIQUE",data["cpu_percent"],"Utilisation CPU supérieure à 95 %")
        elif data["cpu_percent"] >= 80:
            creer_alerte(machine_id,"CPU","ELEVE",data["cpu_percent"],"Utilisation CPU supérieure à 80 %")

        if data["ram_used_percent"] >= 95:
            creer_alerte(machine_id,"RAM","CRITIQUE",data["ram_used_percent"],"RAM presque saturée")
        elif data["ram_used_percent"] >= 85:
            creer_alerte(machine_id,"RAM","ELEVE",data["ram_used_percent"],"Utilisation RAM élevée")

        if data["disk_used_percent"] >= 95:
            creer_alerte(machine_id,"DISQUE","CRITIQUE",data["disk_used_percent"],"Disque presque plein")
        elif data["disk_used_percent"] >= 85:
            creer_alerte(machine_id,"DISQUE","ELEVE",data["disk_used_percent"],"Espace disque faible")

        if data["battery_percent"] is not None:

            if data["battery_percent"] <= 20:
                creer_alerte(
                    machine_id,
                    "BATTERIE",
                    "CRITIQUE",
                    data["battery_percent"],
                    "Batterie critique (moins de 20 %)"
                )

            elif data["battery_percent"] <= 35:
                creer_alerte(
                    machine_id,
                    "BATTERIE",
                    "ELEVE",
                    data["battery_percent"],
                    "Batterie faible (moins de 30 %)"
                )    

        return jsonify({
            "status": "ok",
            "machine": data["hostname"]
        }), 200


    except Error as e:

        if db:
            db.rollback()

        print("Erreur MySQL :", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


    except Exception as e:

        if db:
            db.rollback()

        print("Erreur serveur :", e)

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


    finally:

        if cursor:
            cursor.close()

        if db and db.is_connected():
            db.close()


# Empêcher le cache des pages protégées

@app.after_request
def no_cache(response):

    response.headers[
        "Cache-Control"
    ] = "no-store, no-cache, must-revalidate, max-age=0"

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response


# Lancement du serveur

if __name__ == "__main__":

    app.run(
    host="0.0.0.0",
    port=5000,
    debug=False
)

