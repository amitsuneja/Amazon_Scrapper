import re
import string
import requests
from nltk.corpus import wordnet
from bs4 import BeautifulSoup
from copy import deepcopy
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# import get_proxy
import get_header
import pickle
# from autocorrect import spell

# ignore the warning message about insecure request in output.
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def add_prefix_to_url(url):
	"""
	add_prefix_to_url:
	this function accept the url structure . Then check if url need prefix then add it else don't do anything to url
	and return the url

	:param url:
	:return: url
	"""
	url_prefix = "https://www.amazon.in"
	# check if url_prefix is present in string or not.
	if re.match(url_prefix, url):
		pass
	else:
		url = url_prefix + url
	return url


def split_the_url(url):
	"""
	split_the_url : this function split the url based on pattern and return the breaked_url list

	:param url:
	:return: breaked_url
	"""
	# define a pattern
	pattren = r'[_, =]2'
	# splitting the URL , based on pattern
	breaked_url = re.split(pattren, url)
	return breaked_url


def create_soup_of_url(url):
	"""
	this function accept url as a parameter and return the soup of url.

	:param url:
	:return:
	"""
	# create headers to be used with http request
	headers = get_header.get_agent()

	# send request to download web page using headers created earlier
	webpage = requests.get(url, verify=False, headers=headers)

	# Create a web page html format of downloaded page using lxml parser
	my_soup = BeautifulSoup(webpage.text, "lxml")
	return my_soup


def get_user_input():
	"""
	get_user_input:
	This function accept nothing and will prompt user for input and validate it.
	It ensure that used don't enter any punctuation and user must enter noun.

	:return: string

	"""
	# create a regex pattern containing all the punctuations
	pattern = r"[" + re.escape(string.punctuation) + r"\d+]"

	# create a set of all the nouns present in wordnet
	all_nouns = {x.name().split('.', 1)[0] for x in wordnet.all_synsets('n')}

	# keep on running loop unless user enter valid input
	while True:
		product = input("\nPlease enter product :")
		# check the spelling of product
		# product = spell(product)
		# check if user enter punctuation or he did not enter noun.
		if re.findall(pattern, product) or product not in all_nouns:
			print("\n Invalid input")
		else:
			break

	return product


def collect_urls_from_page_numbers(product_string):
	"""
	collect_urls_from_page_numbers:
	This function will accept product name as a argument.
	create a url of product and then collect all the urls given in bottom of page for the product and return the
	list_of_urls

	:param product_string: this is name of product you want to search on amazon.in
	example - collect_urls_from_page_numbers(book)

	:return: list_of_urls
	"""
	# when is url of side . You can open and check it for testing.
	url = 'https://www.amazon.in/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=' + product_string
	# Store the main URL of Product in a list
	list_of_urls = list()
	# list_of_urls.append(url)

	my_soup = create_soup_of_url(url)
	# write an exception as there may be a case that product you searched does not have page number 2 for review
	# i.e. class_ = 'pagnLink' not found then, how we will proceed?
	try:
		# find_all class = pagnLink in web page
		urls_at_bottom = my_soup.find('span', {'class': 'pagnLink'})
		# get the text value from bottom of page and strip to remove spaces
		review_page_start_number = urls_at_bottom.text.strip()
		# get the structure of URL from the first link at bottom of page
		review_page_url_structure = urls_at_bottom.find('a')['href']
		review_page_url_structure = add_prefix_to_url(review_page_url_structure)

		# get the last page number of review
		review_page_end_number = my_soup.find(class_='pagnDisabled').text.strip()
		# pattren to find and break URL into different parts of list
		breaked_url = split_the_url(review_page_url_structure)
		# generate list of all the URLS present in bottom of page
		for i in range(int(review_page_start_number), int(review_page_end_number) + 1):
			review_url = breaked_url[0] + "_" + str(i) + breaked_url[1] + "=" + str(i) + breaked_url[2]
			list_of_urls.append(review_url)

	except (AttributeError, KeyError, TypeError) as ex:
		with open("my_html.html", "w", encoding="utf-8") as myfile:
			print(my_soup, file=myfile)
			print(url)
			print("This Product does not have pages in the bottom: \n", ex)

	return list_of_urls


def get_product_asin_name_url(list_of_urls):
	"""
	get_product_asin_name_url:
	this function accept list of urls. Iterate over url list. And Generate data in dictionary.
	Here is Data Structure.

product_dict = {
	"ASIN_NUM":  [
					{"name": "Name of product"},
					{"product_url": "http://xyz.com"}
	]
}


	:param list_of_urls:
	:return: product_dict
	"""
	product_dict = dict()

	for url in list_of_urls:
		# create the soup of url
		my_soup = create_soup_of_url(url)
		my_class_1 = 'a-row s-result-list-parent-container'
		my_class_2 = "s-result-item celwidget "
		# try to find class/html code which contain all the product listing (Tip - open site present in center)
		try:
			product_listing_col = my_soup.find_all(class_=my_class_1)
			# now iterate over all the product_listing_col to pick information about particular product
			for product in product_listing_col:
				# try to fetch li tag with specific class , but what to do if no li tag found
				try:
					for result in product.find_all('li', {"class": my_class_2}):
						product_asin_number = result['data-asin']
						# try to fetch h2 and a tag , but what to do if not found.
						try:
							for text in result:
								product_name = text.find('h2')['data-attribute']
								product_url = text.find('a')['href']
								product_url = add_prefix_to_url(product_url)

								product_dict[product_asin_number] = [
									{"name": product_name},
									{"product_url": product_url}
								]
						except (AttributeError, KeyError, TypeError) as ex:
							print("URL does not have h2 tag or a tag:", url)

				except (AttributeError, KeyError, TypeError) as ex:
					print("URL does not have li tag:", url)

		except (AttributeError, KeyError, TypeError) as ex:
			print("URL not having any product:", url, "\n", ex)

	return product_dict


def get_review_url_from_main_page_bottom(url):
	"""
	get_review_url_from_main_page_bottom:

	this function will accept the url as string and scrap review url from its bottom of the page , but and store it
	in variable review_url. But in-case main page of product does not have reviews then it will make value of
	review_url = "not applicable"

	then it creates the dictionary of key review_url and its value and return the dictionary.

	:param url:
	:return:
	"""
	my_soup = create_soup_of_url(url)
	try:
		review_url = my_soup.find('a', {'class': 'a-link-emphasis a-text-bold'})['href']
		review_url = add_prefix_to_url(review_url)
	except (AttributeError, KeyError, TypeError) as ex:
		review_url = "not applicable"

	small_dict = {"review_url": review_url}
	return small_dict


def add_review_url(product_dict):
	"""
	add_review_url:
	this function will accept a dictionary in this format

		product_dict = {
			"ASIN_NUM":  [
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
			]
		}

	it will copy product_dict to temp_product_dict.
	for every product_url in product_dict , it will call get_review_url_from_main_page_bottom(product_url)
	get_review_url_from_main_page_bottom return dictionary . It will append that dictinary to temp_product_dict.
	and will return temp_product_dict

		temp_product_dict = {
			"ASIN_NUM":  [
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "http://1stPageOfReview.url"}
			]
		}

		or

		temp_product_dict = {
			"ASIN_NUM":  [
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "not applicable"}
			]
		}

	:param product_dict:
	:return: temp_product_dict
	"""
	temp_product_dict = deepcopy(product_dict)

	for key in product_dict.keys():
		url = product_dict[key][1]['product_url']
		small_dict = get_review_url_from_main_page_bottom(url)
		temp_product_dict[key].append(small_dict)
	return temp_product_dict


def read_reviews_of_given_url(url):
	"""
	read_reviews :
	this function will accept url as parameter , it scrap the all review and there ratings , append them to list
	then it return the list.

	review_list = [ ("review","rating"), .....]

	:param url:
	:return: review_list
	"""
	my_soup = create_soup_of_url(url)
	text_soup = my_soup.find(class_='a-section a-spacing-none reviews-content a-size-base')
	review_list = list()
	try:
		all_review = text_soup.find_all(class_='a-section celwidget')
		for review in all_review:
			try:
				review_text = review.find(class_='a-size-base review-text').text.strip()
			except (AttributeError, KeyError, TypeError) as ex:
				review_text = "Not Review by user"
			try:
				review_rating = review.find(class_='a-icon-alt').text.strip()[0:3]
			except (AttributeError, KeyError, TypeError) as ex:
				review_rating = "0"
			review_list.append((review_text, review_rating))
	except (AttributeError, KeyError, TypeError) as ex:
		pass

	return review_list


def get_me_all_urls_for_given_review_page(url):
	"""
	get_me_all_urls_for_review_page:
	this function accept the url of first page of view of product.Then it generate urls for all the reviews pages
	append them to list along  with first url it received in parameter and return the list

	:param url:
	:return: all_reviews_url_list
	"""
	my_soup = create_soup_of_url(url)
	all_reviews_url_list = list()
	all_reviews_url_list.append(url)
	try:
		text_soup = my_soup.find(class_='a-section a-spacing-none reviews-content a-size-base')
		try:
			sub_soup = text_soup.find('ul', {"class": "a-pagination"})
			try:
				page_number_soup = sub_soup.find_all('li', {"class": "page-button"})
				start_range = page_number_soup[1].text.strip()
				end_range = page_number_soup[-1].text.strip()
				review_url_structure = page_number_soup[1].find('a')['href']
				review_url_structure = add_prefix_to_url(review_url_structure)
				breaked_url = split_the_url(review_url_structure)
				for i in range(int(start_range), int(end_range) + 1):
					review_url_structure = breaked_url[0] + "_" + str(i) + breaked_url[1] + "=" + str(i)
					all_reviews_url_list.append(review_url_structure)
			except (AttributeError, KeyError, TypeError) as ex:
				pass
		except (AttributeError, KeyError, TypeError) as ex:
			pass
	except (AttributeError, KeyError, TypeError) as ex:
		pass
	return all_reviews_url_list


def add_all_review_urls(product_dict):
	"""
	add_all_review_urls: this function receive the dictionary parameter.

			product_dict = {
			"ASIN_NUM":  [
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "http://1stPageOfReview.url"}
			]
		}

	copy the dictionary to temporary dictionary.
	interate over dictionary and extract value of first page of review i.e "review_url".

	then call another function  get_me_all_urls_for_given_review_page which will return the list of all the urls of
	review pages.
	it add that info to the temporary dictionary and return this temporary dictionary

		temp_product_dict = {
			"ASIN_NUM":  [
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "http://1stPageOfReview.url"}

							{"all_review_url" : [	"http://review2",
													"https://review3",
													"https://review4"
												]
							}
			]
		}

	:param product_dict:
	:return: temp_product_dict
	"""
	temp_product_dict = deepcopy(product_dict)
	for key in product_dict.keys():
		print(temp_product_dict[key][2]['review_url'])
		if 'not applicable' == temp_product_dict[key][2]['review_url']:
			temp_list = "not applicable"
			temp_dict = {"all_review_urls": temp_list}
		else:
			temp_list = get_me_all_urls_for_given_review_page(temp_product_dict[key][2]['review_url'])
			temp_dict = {"all_review_urls": temp_list}
		temp_product_dict[key].append(temp_dict)

	return temp_product_dict


def read_all_reviews_of_product(product_dict):
	"""
	read_all_reviews_of_product :

	this function accept the dictionary(product_dict)
			product_dict = {
			"ASIN_NUM":
			[
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "http://1stPageOfReview.url"}

							{"all_review_url" : [	"http://review2",
													"https://review3",
													"https://review4"
												]
							}
			]
		}


	and copy it to temporary dictionary(temp_product_dict) then it extract all_review_url i.e list from dictionary .
	for each url it calls function read_reviews_of_given_url and read it reviews.

	read_reviews_of_given_url return the list of tuples.
				temp_product_dict = {
			"ASIN_NUM":
			[
							{"name": "Name of product"},
							{"product_url": "http://xyz.com"}
							{"review_url: "http://1stPageOfReview.url"}

							{"all_review_url" : [	"http://review2",
													"https://review3",
													"https://review4"
												]
							}
							{"all_review_text" : [ ( text ,3.4 ) ( text , 5 ) (text  ,3 )  ]
			]
		}


	:param product_dict:
	:return: temp_product_dict
	"""
	temp_product_dict = deepcopy(product_dict)
	for key in product_dict.keys():

		if temp_product_dict[key][3]['all_review_urls'] == "not applicable":
			temp_dict = {"all_reviews_text": "not applicable"}
		else:
			temp_list = list()
			for url in temp_product_dict[key][3]['all_review_urls']:
				text_of_this_page = read_reviews_of_given_url(url)
				temp_list.append(text_of_this_page)
			temp_dict = {"all_reviews_text": temp_list}

		temp_product_dict[key].append(temp_dict)

	return temp_product_dict


print("step1")
my_product = get_user_input()
list_of_url = collect_urls_from_page_numbers(my_product)
with open('step1.pickle', 'wb') as pkl_file:
	pickle.dump(list_of_url, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

print("step2")
my_dict = get_product_asin_name_url(list_of_url)
with open('step2.pickle', 'wb') as pkl_file:
	pickle.dump(my_dict, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

print("step3")
my_dict = add_review_url(my_dict)
with open('step3.pickle', 'wb') as pkl_file:
	pickle.dump(my_dict, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

print("step4")
my_dict = add_all_review_urls(my_dict)
with open('step4.pickle', 'wb') as pkl_file:
	pickle.dump(my_dict, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

print("step5")
my_dict = read_all_reviews_of_product(my_dict)
with open('step5.pickle', 'wb') as pkl_file:
	pickle.dump(my_dict, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)