import numpy as np
import rdflib
import re
from collections import defaultdict
import csv
import os


# Get the required entities from the rdf file
def get_entities(file_loc):
	g = rdflib.Graph()
	g.load(file_loc)

	# Query is missing bibliographic ID
	query = """SELECT ?listItem ?seqID ?author ?title ?keyword
			WHERE {
			?listItem j.2:itemContent ?record .
			?record j.7:references ?manifest .
			?manifest j.4:embodimentOf ?expression .
			
			?listItem j.5:hasSequenceIdentifier ?seqID .
			?manifest j.3:keyword ?keyword .
			
			OPTIONAL { 
				?expression j.0:creator ?author .
				FILTER(datatype(?author) = xsd:string) .
			}
			OPTIONAL {
				?expression j.0:title ?title .
				FILTER(datatype(?title) = xsd:string) .
			}
			}"""

	results = g.query(query)

	print("====== RDF Query ======")
	print("The query returned " + str(len(results)) + " results")
	print()

	g.close()
	return results


# Gather all keyword entities from the rdf graph
def get_keywords(entities):
	result = dict()

	return [entity['keyword'].value for entity in entities]


# Creates a dictionary with entities as keys and the split keyword arrays as values
def clean_and_split(entities):
	result = dict()
	counts = [0, 0, 0, 0, 0, 0, 0, 0]
	for entity in entities:
		keywords = entity['keyword'].value
		keywords = keywords.strip()
		keywords = re.split("[;:]\n\s*", keywords)
		result[entity] = keywords
		if len(keywords) > 6:
			counts[7] += 1
		else:
			counts[len(keywords)] += 1

	print("====== clean_and_split result ======")
	for i in range(7):
		print("Number of entries with " + str(i) + " keywords: " + str(counts[i]))
	print("Number of entries with more than 6 keywords: " + str(counts[7]))
	print()

	return result


# Separates keywords into individual words and adds words to appropriate dictionary
def create_dicts(separated_keywords):
	data_count = 0
	dicts = [defaultdict(int) for x in range(5)]
	for keyword_group in separated_keywords:
		if len(keyword_group) != 5:
			continue
		data_count += 1
		for keyword in keyword_group:
			for num in range(5):
				words = keyword.split()
				for raw in words:
					word = clean_word(raw)
					if word in dicts[num]:
						dicts[num][word] = dicts[num][word] + 1
					else:
						dicts[num][word] = 1

	print("====== create_dicts result ======")
	print("Words from " + str(data_count) + " keyword entries were used to create the dictionaries")
	print()
	if print_dictionaries:
		print_dicts(dicts)

	return dicts


# Removes special characters from words in order to attempt to avoid their influence
def clean_word(word):
	res = word.strip("\",.()[]!?{};’")
	res = re.sub("\w?[’'‘]", "", res)
	return res


# Prints dictionaries
def print_dicts(dicts):
	for dic in dicts:
		for w in sorted(dic, key=dic.get, reverse=True):
			print(w, dic[w])
		print("==============")


# Sorts separated keywords into categories according to the dictionaries.
# Extra word are included to prevent data loss
def sort_words(dicts, keyword_dicts, entities):
	sorted = defaultdict()
	for entity in entities:
		keywords = keyword_dicts.get(entity)
		if len(keywords) >= 5:
			sorted[entity] = keywords
		else:
			last_placed = -1
			indices = []
			order = ["NULL", "NULL", "NULL", "NULL", "NULL"]
			for num in range(len(keywords)):
				# Reduce the potential fields the keyword could be in by eliminating possibilities
				# This relies on the assumption that the data is in the correct order, even if incomplete
				front_lim = max(num, last_placed + 1)
				back_lim = 5 - len(keywords) + num

				words = keywords[num].split()
				scores = []

				for dict_num in range(front_lim, back_lim + 1):
					score = 0
					for raw_word in words:
						word = clean_word(raw_word)
						if word in dicts[num]:
							score = score + dicts[dict_num][word]
					scores.append(score)
				if not len(scores) == 0:
					order[num + np.argmax(scores)] = re.sub("\s{2,}", ", ", keywords[num])  # get rid of whitespace here
					last_placed = num + np.argmax(scores)
			sorted[entity] = order
	return sorted


def to_csv(entities, sorted_dict):
	with open("output.csv", 'w') as output:
		wr = csv.writer(output)
		if os.stat("output.csv").st_size == 0:
			wr.writerow(
				["ID", "Autor", "Titel", "Form", "Handlungsort", "Protagonisten", "Handlung", "Themen", "Extras ->"])
		# seqID author title keywords
		for entity in entities:
			row = []

			if entity['seqID'] is not None:
				row.append(entity['seqID'].value)
			else:
				row.append("NULL")

			if entity['author'] is not None:
				row.append(entity['author'].value)
			else:
				row.append("NULL")

			if entity['title'] is not None:
				row.append(entity['title'].value)
			else:
				row.append("NULL")

			row.extend(sorted_dict[entity])
			wr.writerow(row)


#################
# Config values #
#################
print_dictionaries = False
file_location = "MA_MODEL.rdf"

if __name__ == '__main__':
	print()

	entities = get_entities(file_location)

	entities = sorted(entities, key=lambda row: row['seqID'].value)

	keyword_dicts = clean_and_split(entities)

	dictionaries = create_dicts(keyword_dicts.values())

	sorted_dict = sort_words(dictionaries, keyword_dicts, entities)

	to_csv(entities, sorted_dict)
