import json

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


def get_simple_folks_db():
    connection = sqlite3.connect("simplefolks.sqlite")
    cursor = connection.cursor()
    return connection, cursor


def create_person_dictionary(person):
    return {
        "name": person[0].lower(),
        "gender": "female" if person[1] == "F" else "male",
        "age": person[2]
    }


# da se kreiraat CRUD funkcionalnosti za tabelata 'people' or simplefolks db

@app.route("/get-people", methods=["GET"])
def get_people():
    connection, cursor = get_simple_folks_db()
    sql = "SELECT * FROM people"
    statement = cursor.execute(sql)
    data = statement.fetchall()
    formatted_data = []
    for d in data:  # d = ["Austin", "M", 33]
        formatted_data.append(create_person_dictionary(d))
        # {"name": "Austin", "gender": "M", "age": 33}
    connection.close()
    return {
        "data": formatted_data
    }


@app.route("/get-person/<name>", methods=["GET"])
def get_person(name):
    name = name.capitalize()
    try:
        connection, cursor = get_simple_folks_db()
    except Exception as e:
        print("=>", e)
        return jsonify({"error": "Database not available. Try again later"}), 500
    try:
        data = cursor.execute("SELECT * FROM people WHERE name=?", (name,))
        data = data.fetchone()
        connection.close()
        return jsonify({"person": create_person_dictionary(data)}), 200
    except Exception as e:
        print("--->", e)
        connection.close()
        return jsonify({"error": "Name not found in this database"}), 400


@app.route("/create-person", methods=["POST"])
def create_person():
    person_data = json.loads(request.data)

    if "name" not in person_data.keys() or "gender" not in person_data.keys() or "age" not in person_data.keys():
        return jsonify({"error": "Not all data has been sent. Please try again later"}), 400
    # name = person_data["name"]
    name = person_data.get("name").capitalize()  # od person_data dictionary-to zemi ja vrednosta za kluchot name

    # person_data = {"name": "jessica"}
    # name = "jessica"

    connection, cursor = get_simple_folks_db()
    sql_stmt = "INSERT INTO people (name, sex, age) VALUES (?, ?, ?)"
    cursor.execute(sql_stmt, (name, person_data.get("gender"), person_data.get("age")))
    connection.commit()
    connection.close()
    return jsonify({"message": "Successfully created a new person"}), 201


@app.route("/change-person/<name>", methods=["PUT"])
def change_person(name):
    person_data = json.loads(request.data)
    connection, cursor = get_simple_folks_db()
    sql_stmt = "UPDATE people SET name=?, sex=?, age=? WHERE name=?"

    cursor.execute(sql_stmt, (person_data.get("name").capitalize(),
                              person_data.get("gender"),
                              person_data.get("age"),
                              name.capitalize(),
                              ))
    connection.commit()
    connection.close()
    return jsonify({"message": f"Successfully updated user with new values: {list(person_data.items())}"}), 200


@app.route("/delete-person/<name>", methods=["DELETE"])
def delete_person(name):
    connection, cursor = get_simple_folks_db()
    name = name.capitalize()
    try:
        sql_stmt = "DELETE FROM people WHERE name=?"
        cursor.execute(sql_stmt, (name,))
        connection.commit()
        connection.close()
        return jsonify({"message": f"Successfully deleted the person with name {name}"}), 200
    except Exception as e:
        return jsonify({"error": f"an error has happened"}), 500


if __name__ == "__main__":
    app.run()
