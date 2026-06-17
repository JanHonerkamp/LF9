"""
Todo-Listen-Verwaltung als einfache REST-API mit Flask.

Wichtig:
- Die Daten werden nur im Arbeitsspeicher gespeichert.
- Nach einem Neustart des Servers sind neu angelegte Daten wieder weg.
- IDs werden als zufällige UUIDs erzeugt, nicht als fortlaufende Nummern.
"""

from uuid import uuid4

from flask import Flask, abort, jsonify, request

app = Flask(__name__)

# Beispiel-Daten, damit man die API direkt testen kann.
# Eine Todo-Liste hat eine ID und einen Namen.
todo_lists = [
    {"id": "1318d3d1-d979-47e1-a225-dab1751dbe75", "name": "Einkaufsliste"},
    {"id": "3062dc25-6b80-4315-bb1d-a7c86b014c65", "name": "Arbeit"},
]

# Ein Todo-Eintrag hat eine ID, einen Namen, eine optionale Beschreibung
# und die Zuordnung zu einer Todo-Liste über list_id.
todo_entries = [
    {
        "id": "5ef64d6d-02df-4381-9303-2a7df86e1d41",
        "name": "Milch kaufen",
        "description": "1 Liter Vollmilch",
        "list_id": "1318d3d1-d979-47e1-a225-dab1751dbe75",
    },
    {
        "id": "e9d226f8-2a3e-4d45-a79a-98dff7ed83d2",
        "name": "Arbeitsblaetter ausdrucken",
        "description": "Fuer den Unterricht vorbereiten",
        "list_id": "3062dc25-6b80-4315-bb1d-a7c86b014c65",
    },
]


def find_todo_list(list_id):
    """Sucht eine Todo-Liste anhand ihrer ID."""
    for todo_list in todo_lists:
        if todo_list["id"] == list_id:
            return todo_list
    return None


def find_todo_entry(entry_id):
    """Sucht einen Todo-Eintrag anhand seiner ID."""
    for todo_entry in todo_entries:
        if todo_entry["id"] == entry_id:
            return todo_entry
    return None


def get_json_body():
    """Liest den JSON-Body aus einer Anfrage. Bei Fehlern wird 400 zurückgegeben."""
    if not request.is_json:
        abort(400, description="Der Request-Body muss JSON sein.")
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        abort(400, description="Der Request-Body muss ein JSON-Objekt sein.")
    return data


def validate_name(data):
    """Prüft, ob ein gültiger Name im JSON-Body vorhanden ist."""
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        abort(400, description="Das Feld 'name' ist Pflicht und muss Text enthalten.")
    return name.strip()


@app.after_request
def add_cors_headers(response):
    """Erlaubt einfache Tests aus Tools wie Swagger Editor oder REST-Clients."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PATCH,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/todo-list", methods=["GET"])
def get_all_lists():
    """Liefert alle Todo-Listen zurück."""
    return jsonify(todo_lists), 200


@app.route("/todo-list", methods=["POST"])
def create_list():
    """Erstellt eine neue Todo-Liste."""
    data = get_json_body()
    name = validate_name(data)

    new_list = {
        "id": str(uuid4()),
        "name": name,
    }
    todo_lists.append(new_list)
    return jsonify(new_list), 201


@app.route("/todo-list/<list_id>", methods=["GET"])
def get_entries_from_list(list_id):
    """Liefert alle Einträge einer bestimmten Todo-Liste zurück."""
    if find_todo_list(list_id) is None:
        abort(404, description="Todo-Liste wurde nicht gefunden.")

    entries = [entry for entry in todo_entries if entry["list_id"] == list_id]
    return jsonify(entries), 200


@app.route("/todo-list/<list_id>", methods=["POST"])
def create_entry_in_list(list_id):
    """Fügt einer bestehenden Todo-Liste einen neuen Eintrag hinzu."""
    if find_todo_list(list_id) is None:
        abort(404, description="Todo-Liste wurde nicht gefunden.")

    data = get_json_body()
    name = validate_name(data)
    description = data.get("description", "")
    if description is None:
        description = ""
    if not isinstance(description, str):
        abort(400, description="Das Feld 'description' muss Text sein.")

    new_entry = {
        "id": str(uuid4()),
        "name": name,
        "description": description,
        "list_id": list_id,
    }
    todo_entries.append(new_entry)
    return jsonify(new_entry), 201


@app.route("/todo-list/<list_id>", methods=["DELETE"])
def delete_list(list_id):
    """Löscht eine Todo-Liste und alle Einträge dieser Liste."""
    todo_list = find_todo_list(list_id)
    if todo_list is None:
        abort(404, description="Todo-Liste wurde nicht gefunden.")

    todo_lists.remove(todo_list)

    # Alle Einträge der gelöschten Liste entfernen.
    todo_entries[:] = [entry for entry in todo_entries if entry["list_id"] != list_id]
    return "", 204


@app.route("/todo-list/entry/<entry_id>", methods=["PATCH"])
def update_entry(entry_id):
    """Aktualisiert einen bestehenden Todo-Eintrag."""
    entry = find_todo_entry(entry_id)
    if entry is None:
        abort(404, description="Todo-Eintrag wurde nicht gefunden.")

    data = get_json_body()
    allowed_fields = {"name", "description"}
    if not any(field in data for field in allowed_fields):
        abort(400, description="Es muss mindestens 'name' oder 'description' gesendet werden.")

    if "name" in data:
        entry["name"] = validate_name(data)

    if "description" in data:
        description = data["description"]
        if description is None:
            description = ""
        if not isinstance(description, str):
            abort(400, description="Das Feld 'description' muss Text sein.")
        entry["description"] = description

    return jsonify(entry), 200


@app.route("/todo-list/entry/<entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    """Löscht einen einzelnen Todo-Eintrag."""
    entry = find_todo_entry(entry_id)
    if entry is None:
        abort(404, description="Todo-Eintrag wurde nicht gefunden.")

    todo_entries.remove(entry)
    return "", 204


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": "Bad Request", "message": error.description}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Not Found", "message": error.description}), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "Diese HTTP-Methode ist hier nicht erlaubt."}), 405


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
