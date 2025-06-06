import csv, sqlite3

def get_col_datatypes(fin):
    """
    Helper function for getting column data types!
    """
    dr = csv.DictReader(fin) #, delimiter=';'
    field_types = {}

    for entry in dr:
        fields_left = [f for f in dr.fieldnames if f not in field_types.keys()]
        if not fields_left:
            break
        for field in fields_left:
            data = entry[field]

            # Make sure there is data
            if len(data) == 0:
                continue

            # Find data's type!
            if data.isdigit():
                field_types[field] = "INTEGER"
            else:
                field_types[field] = "TEXT"

    return field_types


def escaping_generator(f):
    """
    Helper functio n for encoding and decoding
    """
    for line in f:
        yield line.encode("ascii", "xmlcharrefreplace").decode("ascii")

def csv_to_db(table, csv_file, attrs):
    """
    Function for converting CSV file to SQLite DB!
    """

    # Institution CSV
    with open(csv_file, mode="r", encoding="utf-8-sig") as fin:
        # Prepare reading CSV
        dt = get_col_datatypes(fin)
        fin.seek(0)
        reader = csv.DictReader(fin) #, delimiter=';'

        # Keep the order of the columns name just as in the CSV
        fields = reader.fieldnames
        cols = []
        for f in fields:
            if f == 'IRIS':
                cols.append("IRIS TEXT")
            if f == 'dist_to_green':
                cols.append("dist_to_green FLOAT")
            else:
                cols.append("%s %s" % (f, dt[f]))

        # Find the indices of the columns we need to keep
        filtered_cols = []
        indices = []
        for attr in attrs:
            index = fields.index(attr)
            indices.append(index)
            filtered_cols.append(cols[index])

        # Keep only the cells of data at these indices
        reader = csv.reader(escaping_generator(fin))  #, delimiter=';'
        rows = []
        for row in reader:
            rows.append([row[i] for i in indices if i < len(row)])

        connection = sqlite3.connect("stats_big.db")
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS %s;" % table)

        statement1 = "CREATE TABLE %s (%s)" % (table, ",".join(filtered_cols))
        cursor.execute(statement1)

        fin.seek(0)

        # Generate insert statements
        statement1 = "INSERT INTO %s VALUES(%s);" % (table, ','.join('?' * len(filtered_cols)))

        cursor.executemany(statement1, rows)
        connection.commit()

attr_income = ["IRIS", "DISP_MED21"]
attr_distance = ["nom_iris" ,"code_iris", "DISP_MED21" ,"dist_to_green"]


# csv_to_db("income", "data\BASE_TD_FILO_IRIS_2021_DISP.csv", attr_income)
csv_to_db("income_and_distance", "data\iris_revenu_distance.csv", attr_distance)