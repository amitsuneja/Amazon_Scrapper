from amazon_scrapper import get_user_input
from amazon_scrapper import collect_urls_from_page_numbers
from amazon_scrapper import get_product_asin_name_url
from amazon_scrapper import add_review_url
from amazon_scrapper import add_all_review_urls
from amazon_scrapper import read_all_reviews_of_product
import pickle


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
