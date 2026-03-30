import sqlite3
from html_to_markdown import convert

DATABASE = "/home/legendmixer/IntelliJProjects/AceOfGrades/aog.sqlite3"

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

def run_sql(*args):
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    cursor.execute(*args)
    connection.commit()
    return cursor.fetchall()

def run_sql_get_id(*args):
    connection = sqlite3.connect(DATABASE)
    connection.execute("PRAGMA foreign_keys = 1")
    cursor = connection.cursor()
    cursor.execute(*args)
    connection.commit()
    return cursor.lastrowid

def main():
    packs_data = read_csv("cards/packs.csv")
    for pack in packs_data:
        sqlstring = """
            INSERT INTO tblPack (creator_id, name, description, front_color, back_color, is_public)
            VALUES (1, ?, ?, ?, ?, 1)
        """
        pack_id = run_sql_get_id(sqlstring, (pack["pack_name"], pack["pack_description"], pack["pack_front_color"], pack["pack_back_color"]))

        sqlstring = """
            INSERT INTO tblPackLink (pack_id, user_id)
            VALUES (?, 1)
        """
        run_sql(sqlstring, (pack_id,))

        pack_uuid = pack["pack_uuid"]
        cards_data = read_csv(f"cards/packs/{pack_uuid}.csv")
        for card in cards_data:

            md_front = convert(card["front"])
            md_back = convert(card["back"])

            sqlstring = """
                INSERT INTO tblCard (pack_id, front, back, front_color, back_color)
                VALUES (?, ?, ?, ?, ?)
            """
            card_id = run_sql_get_id(sqlstring, (pack_id, md_front, md_back, card["front_color"], card["back_color"]))

            sqlstring = """
                INSERT INTO tblCardLink (card_id, pack_id)
                VALUES (?, ?)
            """
            run_sql(sqlstring, (card_id, pack_id))

            sqlstring = """
                INSERT INTO tblCardStats (card_id, user_id, attempts, correct)
                VALUES (?, 1, ?, ?)
            """
            run_sql(sqlstring, (card_id, card["attemps"], card["correct"]))

if __name__ == "__main__":
    main()