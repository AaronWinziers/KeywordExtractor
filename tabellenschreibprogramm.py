# Dieses Skript liest die Datei keywords_korrigiert.csv ein
# Die Datei wird in Tabellenkalkulationsprgrammen nicht richtig dargestellt,
# weil Spalten durch "" getrennt wurden + mehrere Trennzeichen verwendet wurden
# Dieses Skript säubert die Datei und schreibt das Ergebnis neu in
# ein csv-file

import re

with open("..//data_in//Keywords_Korrigiert.csv", encoding="utf-8") as file:
    data = file.read()

outputfile = open("..//data_out//keywords_korrigiert2.csv", "w", encoding="utf-8")

name_file = open("..//data_out//name_file.csv", "w", encoding="utf-8")

p_id = re.compile('[0-9]{2,2}\.[0-9]+')
#print(p_id.findall(data))
id_year = (p_id.findall(data))

p_name = re.compile("\"[A-Z\s-]+,[a-zA-Z\s-]+\"")
names = (p_name.findall(data))
#print(names)

for i in range(len(id_year)):
    outputfile.write(id_year[i] + "; \n")

for i in range(len(names)):
    name_file.write(names[i] + "; \n")


#print(len(names))


test_file = open("..//data_out//test_file.csv", "w", encoding="utf-8")
p_all = re.split("\" * \"", data)
#print("p_all")
#print(p_all)

test = re.split("\"", data)
# print(test)

split_data = re.sub(
    "\",\"",   # pattern
    "\"; \"",       # replacement
    data
)

print(split_data)

for item in split_data:
    test_file.write(item)