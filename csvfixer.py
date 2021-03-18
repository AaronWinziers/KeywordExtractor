import csv

# Einlesen der Datei
max_row_len = 0
with open("Keywords_Korrigiert.csv", newline='') as file:
    reader = csv.reader(file, delimiter=',', quotechar='"')

    # Daten werden in zwei Varianten gelesen
    # data1 = so wie in Input-Datei
    # data2 = aus Input-Datei ohne Leerzeichen am Anfang und Ende des Eintrags
    data1 = []
    data2 = []

    for row in reader:
        max_row_len = max(len(row), max_row_len)

        # data1
        data1.append(row)

        # data2
        stripped_row = []
        for d in row:
            stripped_row.append(d.strip())
        data2.append(stripped_row)

# Alle Zeilen auf die gleiche Länge verlängern (falls notwendig)
for row in data1:
    while len(row) < max_row_len:
        row.append('')
for row in data2:
    while len(row) < max_row_len:
        row.append('')

# Speichern
with open("Keywords_Korrigiert3.csv", 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"')
    writer.writerows(data1)

with open("Keywords_Korrigiert4.csv", 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',', quotechar='"')
    writer.writerows(data2)