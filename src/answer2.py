# -*- coding: utf-8 -*-
# Decide the named entity type(person, place) of the answer

from rake_nltk import Rake
import spacy
import collections
from enum import Enum
import sys
import io


TOP_K = 10
class WHType(Enum):
	WHO = 'who'
	WHOSE = 'whose'
	WHOM = 'whom'
	WHAT = 'what'
	WHERE = 'where'
	WHEN = 'when'
#Binary type
class BINType(Enum):
	AM = 'am'
	IS = 'is'
	ARE = 'are'
	WAS = 'was'
	WERE = 'were'
	HAD = 'had'
	HAS = 'has'
	HAVE = 'have'
	DO = 'do'
	DID = 'did'
	WILL = 'will'
	WOULD = 'would'
	CAN = 'can'
	COULD = 'could'


def read_data(file):
    with open(file) as f:
        data = f.readlines()
    return data

# isinstance(obj, WHType)
def detect_type(sentence):
	sentence = sentence.lower()
	for w_type in WHType:
		if sentence.startswith(w_type.value):
			return w_type

	for b_type in BINType:
		if sentence.startswith(b_type.value):
			return b_type

	return 'Unknown answer type'



# Generate keywords for quetion
def keywords_generation(question):
	r = Rake()
	r.extract_keywords_from_text(question)
	keywords = r.get_ranked_phrases()
	return keywords

# topK Most Relevant Sentences
def find_relevant_sentences(keywords, article):
	nlp = spacy.load('en')
	article_dict = collections.Counter()
	for sentence in article:
		tokens = set()
		doc = nlp(sentence)
		for token in doc:
			tokens.add(str(token))
		matched_words = set(filter(set(keywords).__contains__, tokens))
		article_dict[sentence] = len(matched_words)

	relevant_sents = []
	for (sentence, num_matchwords) in article_dict.most_common(TOP_K):
		relevant_sents.append(sentence)

	return relevant_sents

# Parse sentence dependency parser
def extract_answer_by_NER(relevant_sents, ner_list):
	answers = []
	for sent in relevant_sents:
		nlp = spacy.load('en')
		doc = nlp(sent)
		# answer = set()
		for ent in doc.ents:
			if ent.label_ in ner_list:
				# answer.add(ent.text)
				answers.append(ent.text)
	return answers


def answerWH(question_type, relevant_sents):
	ner_list = []
	if question_type in [WHType.WHO, WHType.WHOSE, WHType.WHOM]:
		ner_list = ["PERSON"]
	elif question_type == WHType.WHERE:
		ner_list = ["LOC", "ORG", "GPE"]
	elif question_type == WHType.WHEN:
		ner_list = ["DATE", "TIME"]
	elif question_type == WHType.WHERE:
		ner_list = ["ORG", "GPE", "LOC"]
	elif question_type == WHType.WHAT:
		ner_list = ["ORG", "PRODUCT"]

	# answers = []
	# for sent in relevant_sents:
	# 	answer = extract_answer_by_NER(sent, ner_list)
	# 	answers.append(answer)
	answers = extract_answer_by_NER(relevant_sents, ner_list)
	return answers


def extract_answer_by_not(sent, not_list):
	for w in sent:
		if w in not_list:
			return "No"
	return "Yes"


def answerBIN(question_type, relevant_sents):
	not_list = []
	if question_type in [BINType.AM]:
		not_list = ["not"]
	elif question_type in [BINType.IS]:
		not_list = ["not", "isn't"]
	elif question_type in [BINType.ARE]:
		not_list = ["not", "aren't"]
	elif question_type in [BINType.WERE]:
		not_list = ["not", "weren't"]
	elif question_type in [BINType.HAD]:
		not_list = ["not", "hadn't"]
	elif question_type in [BINType.HAS]:
		not_list = ["not", "hasn't"]
	elif question_type in [BINType.HAVE]:
		not_list = ["not", "haven't"]
	elif question_type in [BINType.DO]:
		not_list = ["not", "don't"]
	elif question_type in [BINType.DID]:
		not_list = ["not", "didn't"]
	elif question_type in [BINType.WILL]:
		not_list = ["not", "won't"]
	elif question_type in [BINType.WOULD]:
		not_list = ["not", "wouldn't"]
	elif question_type in [BINType.CAN]:
		not_list = ["not", "cann't"]
	elif question_type in [BINType.COULD]:
		not_list = ["not", "couldn't"]

	# answers = []
	for sent in relevant_sents:
		answer = extract_answer_by_not(sent, not_list)
		# answers.append(answer)
	return answer

#'Who is the presentend?'
def answer(article, question):
	keywords = keywords_generation(question)
	question_type = detect_type(question)

	relevant_sents = find_relevant_sentences(keywords, article)

	answers = []
	if isinstance(question_type, WHType):
		answers = answerWH(question_type, relevant_sents)
	elif isinstance(question_type, BINType):
		answers = answerBIN(question_type, relevant_sents)
	return answers



def main(article, question):
	question = read_data(question)
	answer_list = []
	out_file = 'answers.txt'
	for q in question:
		answers = answer(article, q)
		print(answers)
		answer_list.append(answers)
	# write_file(out_file, answer_list)


if __name__ == "__main__":
	# question = "Who is the presentend?"
	# article = ["Donald Trump is the presentend."]

	# print(question)
	# print(answer(question, article))
	article = sys.argv[1]
	question = sys.argv[2]
	main(article, question)