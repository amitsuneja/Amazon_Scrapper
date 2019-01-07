"""
We are trying to classify review of product is related to python book or television using K neariest neighbour
There are other ways also like bayes method or svm.

what we did ?  we used amazon scrapper to scrap the reviews from amazon.in to create a data set in pickle format.

1. we wrote pickle_to_csv function to convert those pickle formatted data sets to csv file.
But while storing the data in csv file we cleaned up the data and

2. we wrote read_csv_reviews_to_big_string to convert all reviews into single big_string.

3.  we wrote calculate_word_freq to cleanup data more .
    a. convert big string to small letters
    b. removed stop words and punctuations from big_string.
"""

import re
import pandas as pd
from nltk.tokenize import word_tokenize
from string import punctuation
from copy import deepcopy
from nltk.corpus import stopwords
import nltk
import pickle

def clean_training_csv_file(csv_file_name, category):
	"""
	clean_csv_file:
	This will receive the name of csv file in clean_csv_file and category
	convert the column names as 'Review' into string .
	then pick the lines whose length is >  6. i.e if review contain small character like good , bad because right now
	we are categorizing text on basis of PythonBook or Television , So these single words reviews should be ignored.
	then it store the output in csv_file_name along with category



	:param csv_file_name:
	:param category:
	:return:
	"""

	df = pd.read_csv(csv_file_name)
	df['Review'] = df['Review'].astype('str')
	df = df[df['Review'].str.len() > 6]
	df['Category'] = category
	df.to_csv(csv_file_name, index=None)
	return csv_file_name


def pickle_to_csv(pickle_file):
	"""
	pickle_to_csv:
	this function created a dictionary from pickle file. then extract review and rating from dictionary.
	then it tries to replace unwanted character from review (data cleanup) and finally dump both values in csv file.

	:param pickle_file: name of pickle file
	:param category:  category of csv file, remember if category is television then csv file name is Television.csv
	:return: None
	"""

	category_dict = pickle.load(open(pickle_file, "rb"))

	# here in search_pattern is (A|B|C) means A or B or C i.e if any character match A or B or C
	# \.\.+ --> means if you see multiple dots in text like .......
	# [^\x00-\x7F]+ --> means any unicode character like smile face or thumbs up or down symbol and similar shapes.
	# Basically all non-ASCII  characters.
	search_pattern = r'([,\(\)\"\"\']|\.\.+|[^\x00-\x7F]+)'

	# replacement pattern is just a blank space
	replacement_pattern = r' '

	csv_file_name = pickle_file.replace(".pickle", ".csv")

	with open(csv_file_name, 'w', encoding="utf-8") as my_csv_file:
		print('Review, Rating', file=my_csv_file)
		for key, value in category_dict.items():
			review_text = value[4]['all_reviews_text']
			if review_text != "not applicable":
				for item in review_text:
					if len(item) != 0:
						for review, rating in item:
							print(re.sub(search_pattern, replacement_pattern, review).strip(), ",", rating,
								  file=my_csv_file)
	return csv_file_name


def split_training_and_test_data(csv_file_name):
	train_file = "train_" + csv_file_name
	test_file = "test_" + csv_file_name

	df = pd.read_csv(csv_file_name)
	number_of_records = len(df.index)
	if number_of_records < 100:
		print("you need to train well this model, please provide more records to train")
	else:
		train_number = int(number_of_records/2)
		test_number = number_of_records - train_number
	df_train = df.head(train_number)
	df_test = df.tail(test_number)
	df_train.to_csv(train_file, index=None)
	df_test.to_csv(test_file, index=None)
	return train_file, test_file


def combine_csv_files(file1,file2,result_file_name):
	df_1 = pd.read_csv(file1)
	df_2 = pd.read_csv(file2)
	df_result = df_1.append(df_2)
	df_result.to_csv(result_file_name, index=None)


def csv_to_dict(csv_fine_name):
	df = pd.read_csv(csv_fine_name)
	my_dict_name = df.to_dict('index')
	return my_dict_name


def add_word_freq_to_model(my_dict):
	temp_product_dict = deepcopy(my_dict)
	# Create the list of stop words and punctuation
	list_of_punctuation = list(punctuation)
	english_stops = set(stopwords.words('english') + list_of_punctuation)
	for key in temp_product_dict.keys():
		review_text = temp_product_dict[key]['Review']
		tok_words_of_review = list(word_tokenize(review_text))
		clean_tok_of_review = list(word for word in tok_words_of_review if word not in english_stops and len(word) > 1)
		my_dict[key]['freq_dist_of_review'] = dict(nltk.FreqDist(clean_tok_of_review))
	return my_dict


def find_nearest_neighbour(training_model_dict, test_model_dict):
	temp_test_model_dict = deepcopy(test_model_dict)

	for key in temp_test_model_dict.keys():
		outer_book_count = 0
		outer_tv_count = 0
		for word, count_value in temp_test_model_dict[key]['freq_dist_of_review'].items():
			category_book_count = 0
			category_tv_count = 0
			for key1 in training_model_dict.keys():
				for word1, count_value1 in training_model_dict[key1]['freq_dist_of_review'].items():
					if word == word1:
						if training_model_dict[key1]['Category'] == 'pythonbook':
							category_book_count = category_book_count + count_value1
						if training_model_dict[key1]['Category'] == 'Television':
							category_tv_count = category_tv_count + count_value1
			# decision for particular word.
			outer_book_count = outer_book_count + category_book_count
			outer_tv_count = outer_tv_count + category_tv_count
		# decision for complete line
		if outer_book_count > outer_tv_count:
			test_model_dict[key]['Category'] = 'pythonbook'
		elif outer_book_count < outer_tv_count:
			test_model_dict[key]['Category'] = 'Television'
		else:
			test_model_dict[key]['Category'] = 'confused'

	return test_model_dict


def dict_to_csv_file(my_dict, file_name):
	with open(file_name, 'w') as final_file:
		print("Review,Rating,Category", file=final_file)
		for key, value in my_dict.items():
			print(value['Review'], value[' Rating'], value['Category'], file=final_file)


print("step1")
# convert the pickle to csv files.
csv_file = pickle_to_csv('PythonBook.pickle')
train_1, test_1 = split_training_and_test_data(csv_file)
clean_training_csv_file(train_1, 'pythonbook')
csv_file = pickle_to_csv('Television.pickle')
train_2, test_2 = split_training_and_test_data(csv_file)
clean_training_csv_file(train_2, 'Television')


# train_1 = 'train_Television.csv'
# train_2 = 'train_PythonBook.csv'
# test_1 = 'test_Television.csv'
# test_2 = 'test_PythonBook.csv'

print("step2")
combine_csv_files(train_1, train_2, 'complete_training_data.csv')
combine_csv_files(test_1, test_2, 'complete_test_data.csv')

print("step3")
training_model_dict = csv_to_dict('complete_training_data.csv')
test_model_dict = csv_to_dict('complete_test_data.csv')

print("step4")
training_model_dict = add_word_freq_to_model(training_model_dict)
test_model_dict = add_word_freq_to_model(test_model_dict)

print("step5")
test_model_dict = find_nearest_neighbour(training_model_dict, test_model_dict)
with open('test_model_dict.pickle', 'wb') as pkl_file:
	pickle.dump(test_model_dict, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

test_model_dict = pickle.load(open('test_model_dict.pickle', 'rb'))
dict_to_csv_file(test_model_dict, 'updated_complete_training_data.csv')

