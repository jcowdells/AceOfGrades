from flask import Flask, render_template, request, url_for, redirect
import json
import os
import uuid
import sys

from requests import get

#ip = get('https://api.ipify.org').content.decode('utf8')

host_address = sys.argv[2].split("=")[1]
app = Flask(__name__)
app.config["SECRET_KEY"] = "A_SECRET!!!!"
# app.config["SERVER_NAME"] = f"{host_address}:5000"


def read_csv(filepath):
    with open(filepath) as file_ptr:
        keys = None
        lines = list()
        out = list()
        for line in file_ptr:
            lines.append(line.rstrip())
        for i, line in enumerate(lines):
            builder = ""
            mark_depth = 0
            addon = ""
            chunks = []
            for character in line:
                if character == "\"":
                    if mark_depth % 2 == 0:
                        builder += character
                    mark_depth += 1
                elif character == ",":
                    if mark_depth % 2 == 0:
                        chunks.append(builder)
                        builder = ""
                    else:
                        builder += character
                else:
                    builder += character
            chunks.append(builder)
            for j, chunk in enumerate(chunks):
                if len(chunk) > 0 and chunk[0] == "\"":
                    chunk = chunk[1:]
                chunks[j] = chunk

            if i == 0:
                keys = chunks
            else:
                chunk = dict()
                for j, key in enumerate(keys):
                    chunk[key] = chunks[j]
                out.append(chunk)
        return out
    return None


def format_csv(data):
    data_builder = ""
    for i, character in enumerate(str(data)):
        if character == "\"":
            data_builder += "\"\""
        elif ord(character) == 10 or ord(character) == 13:
            pass
        else:
            data_builder += character
    data = data_builder
    if "," in data or "\"" in data:
        data = f"\"{data}\""
    return data


def write_csv(filepath, data):
    if len(data) == 0: return
    keys = list(data[0].keys())
    with open(filepath, "w") as file_ptr:
        def writeLine(string):
            file_ptr.write(string + "\n")
        def writeData(data):
            writeLine(",".join([format_csv(x) for x in data]))
        writeData(keys)
        for chunk in data:
            values = list(chunk.values())
            writeData(values)


@app.route("/")
@app.route("/index/")
def index():
    data = read_csv("cards/packs.csv")
    return render_template("index.html")


@app.route("/card/<card_uuid>", methods=["GET", "POST"])
def card(card_uuid):
    filepath = f"cards/packs/{card_uuid}.csv"
    if not os.path.exists(filepath):
        return render_template("error.html", error="UUID does not correlate to a pack.")
    cards_data = read_csv(filepath)
    cards_dict = {
        "uuid": card_uuid,
        "num_cards": len(cards_data),
        "cards": cards_data
    }

    pack_data = read_csv("cards/packs.csv")
    front_color = "#000000"
    back_color = "#000000"
    for pack in pack_data:
        if pack["pack_uuid"] == card_uuid:
            front_color = pack["pack_front_color"]
            back_color = pack["pack_back_color"]

    return render_template("card.html", cards_json=json.dumps(cards_dict), front_color=front_color, back_color=back_color)


@app.route("/card_update/<card_uuid>", methods=["POST"])
def card_update(card_uuid):
    card_data = request.get_json()["cards"]
    filepath = f"cards/packs/{card_uuid}.csv"
    write_csv(filepath, card_data)
    return "success"


@app.route("/packs/")
def packs():
    packs_data = read_csv("cards/packs.csv")
    return render_template("packs.html", packs=sorted(packs_data, key=lambda pack: pack["pack_name"] + pack["pack_description"]))

@app.route("/packs_view/")
def packs_view():
    packs_data = read_csv("cards/packs.csv")
    return render_template("packs-view.html", packs=sorted(packs_data, key=lambda pack: pack["pack_name"] + pack["pack_description"]))

@app.route("/cards_list/<card_uuid>")
def cards_list(card_uuid):
    packs_data = read_csv("cards/packs.csv")
    pack_index = -1
    for i, pack in enumerate(packs_data):
        if card_uuid == pack["pack_uuid"]:
            pack_index = i
            break
    if pack_index == -1:
        return render_template("error.html", error="Pack does not exist!")
    pack_name = packs_data[pack_index]["pack_name"] + " - " + packs_data[pack_index]["pack_description"]
    pack_front_color = packs_data[pack_index]["pack_front_color"]
    cards_data = read_csv(f"cards/packs/{card_uuid}.csv")
    MAX_LEN = 50
    for i, card in enumerate(cards_data):
        if card["front_color"] == "":
            card["front_color"] = pack_front_color
        if len(card["front"]) > MAX_LEN:
            card["front"] = card["front"][:MAX_LEN - 3] + "..."
        if len(card["back"]) > MAX_LEN:
            card["back"] = card["back"][:MAX_LEN - 3] + "..."
        card["index"] = i
    return render_template("cards-list.html", pack_name=pack_name, pack_uuid=card_uuid, cards=cards_data)

@app.route("/editor_select/")
def editor_select():
    packs_data = read_csv("cards/packs.csv")
    return render_template("packs-editor.html", packs=sorted(packs_data, key=lambda pack: pack["pack_name"] + pack["pack_description"]))


@app.route("/create/", methods=["GET", "POST"])
def create():
    errors = list()
    if request.method == "POST":
        if len(request.form["name"]) == 0:
            errors.append("Name must not be empty!")
        if len(errors) == 0:
            packs_data = read_csv("cards/packs.csv")
            pack_uuid = str(uuid.uuid4())
            packs_data.append({
                "pack_name": request.form["name"],
                "pack_description": request.form["description"],
                "pack_front_color": request.form["front_color"],
                "pack_back_color": request.form["back_color"],
                "pack_uuid": pack_uuid
            })
            write_csv("cards/packs.csv", packs_data)
            with open(f"cards/packs/{pack_uuid}.csv", "w") as _:
                pass
            return redirect(url_for("editor", card_uuid=pack_uuid))
    return render_template("create.html", errors=errors)


@app.route("/editor/<card_uuid>", methods=["GET", "POST"])
def editor(card_uuid):
    errors = list()
    successes = list()
    pack_data = read_csv("cards/packs.csv")
    front_color = "#000000"
    back_color = "#000000"
    for pack in pack_data:
        if pack["pack_uuid"] == card_uuid:
            front_color = pack["pack_front_color"]
            back_color = pack["pack_back_color"]
    if request.method == "POST":
        if len(request.form["front"]) == 0:
            errors.append("Card cannot have an empty front!")
        if len(request.form["back"]) == 0:
            errors.append("Card cannot have an empty back!")
        if len(errors) == 0:
            filepath = f"cards/packs/{card_uuid}.csv"
            card_data = read_csv(filepath)
            new_front_color = request.form["front_color"]
            if new_front_color == front_color:
                new_front_color = ""
            new_back_color = request.form["back_color"]
            if new_back_color == back_color:
                new_back_color = ""
            card_data.append({
                "front": request.form["front"],
                "back": request.form["back"],
                "front_color": new_front_color,
                "back_color": new_back_color,
                "attemps": "0",
                "correct": "0"
            })
            write_csv(filepath, card_data)
            successes.append("Successfully added card")
    return render_template("editor.html", errors=errors, successes=successes,
                           front_color=front_color, back_color=back_color)

@app.route("/update/<card_uuid>/<card_index>", methods=["GET", "POST"])
def update(card_uuid, card_index):
    errors = list()
    successes = list()

    pack_data = read_csv("cards/packs.csv")
    front_color = "#000000"
    back_color = "#000000"

    try:
        card_index = int(card_index)
    except ValueError:
        return render_template("error.html", error="Not a valid card index!")

    filepath = f"cards/packs/{card_uuid}.csv"
    card_data = read_csv(filepath)
    if len(card_data) <= card_index:
        return render_template("error.html", error="Card index out of range!")

    for pack in pack_data:
        if pack["pack_uuid"] == card_uuid:
            front_color = pack["pack_front_color"]
            back_color = pack["pack_back_color"]

    if card_data[card_index]["front_color"] != "":
        cfront_color = card_data[card_index]["front_color"]
    else:
        cfront_color = front_color

    if card_data[card_index]["back_color"] != "":
        cback_color = card_data[card_index]["back_color"]
    else:
        cback_color = back_color

    front = card_data[card_index]["front"]
    back = card_data[card_index]["back"]

    if request.method == "POST":
        if len(request.form["front"]) == 0:
            errors.append("Card cannot have an empty front!")
        if len(request.form["back"]) == 0:
            errors.append("Card cannot have an empty back!")
        if len(errors) == 0:
            new_front_color = request.form["front_color"]
            if new_front_color == front_color:
                new_front_color = ""
            new_back_color = request.form["back_color"]
            if new_back_color == back_color:
                new_back_color = ""
            new_card_data = {
                "front": request.form["front"],
                "back": request.form["back"],
                "front_color": new_front_color,
                "back_color": new_back_color,
                "attemps": "0",
                "correct": "0"
            }
            card_data[card_index] = new_card_data
            write_csv(filepath, card_data)
            successes.append("Successfully updated card")
    return render_template("update.html", errors=errors, successes=successes,
                           front_color=cfront_color, back_color=cback_color,
                           front=front, back=back)

if __name__ == "__main__":
    app.run(port=5000)
