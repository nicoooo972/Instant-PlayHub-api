from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__, template_folder='templates')
CORS(app)

sample_data = [
    {
        "id": 1,
        "name": "Doe",
        "prenom": "John",
        "mot_de_passe": "secret123",
        "type": "Action",
        "version": "1.1"
    },
    {
        "id": 2,
        "name": "Smith",
        "prenom": "Jane",
        "mot_de_passe": "qwerty",
        "type": "Action",
        "version": "1.1"
     },
]


@app.route('/')
def getGames():
    return ''


@app.route('/admin')
def admin():
    data_to_return = [
        {
            "id": entry["id"],
            "name": entry["name"],
            "prenom": entry["prenom"],
            "type": entry["type"],
            "version": entry["version"]
        }
        for entry in sample_data
    ]
    return jsonify(data_to_return)


if __name__ == '__main__':
    app.run()
