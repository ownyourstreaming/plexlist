#! /usr/bin/env python3

import sqlite3
import getopt
import sys
import os.path

columns = [
    "width",
    "height",
    "size",
    "container",
    "video_codec",
    "audio_codec",
]

db_paths = [
    "/var/lib/plexmediaserver/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db",
]

def main(argv):
    db_path = None
    outputfile = 'plexlist.csv'
    cols = ''
    library_id = None
    try:
        opts, args = getopt.getopt(argv,"o:")
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-o"):
            outputfile = arg

    for db in db_paths:
        if os.path.exists(db):
            db_path = db
            break

    if db_path is None:
        print("Couldn't find Database")
        sys.exit(2)

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT id,name FROM library_sections")
    library_dict = list(cursor.fetchall())
    library_dict.sort(key=lambda item: item[0])
    library_dict = dict(library_dict)

    while library_id == None:
        print("Select Library: " + str(library_dict))
        lid = input()
        try:
            lid = int(lid)
            if lid in library_dict.keys():
                library_id = lid
            else:
                print("Invalid")
        except:
            print("Invalid")

    cursor.execute("SELECT id,title FROM metadata_items WHERE library_section_id={} AND media_item_count=1".format(library_id))
    item_list = cursor.fetchall()

    def get_data(item):
        cursor.execute("SELECT {} FROM media_items WHERE metadata_item_id={}".format(','.join(columns), item[0]))
        return item + cursor.fetchall()[0] 
    full_item_data = list(map(get_data, item_list))

    full_item_data.sort(key=lambda item: item[1])

    with open(outputfile, "w") as file:
        file.write(','.join(['id', 'title'] + columns) + '\n')
        for item in full_item_data:
            file.write(','.join(map(lambda i: '"' + str(i) + '"', item)) + '\n')

    print("Output {} title(s) from '{}' library to {}".format(len(full_item_data), library_dict[library_id], outputfile))

if __name__ == "__main__":
   main(sys.argv[1:])
