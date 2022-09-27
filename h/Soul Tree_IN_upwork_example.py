###########################################################################################################################
##############  SECTION I - Import all libraries ##########################################################################
###########################################################################################################################

#Selectolax webscraping tool import
from selectolax.parser import HTMLParser
import lxml
import requests

#Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Processing tools import
import time
import re
from re import sub
from decimal import Decimal
import fractions
import json
import codetiming
from datetime import date
today = date.today().strftime("%Y-%m-%d")

#Data tools imports
import pandas as pd
import gc

t = codetiming.Timer(name="execTime")
t.start()

###########################################################################################################################
##############  SECTION II - set up variables including brand name, chrome driver location (for Selenium) #################
###########################################################################################################################

#-------___Set up stage ----------
#Note -
brand_name = 'Soul Tree'
brand_name_locale = 'Soul Tree India'   #### Note - brand_name_locale indicates which site of that brand is scraped. E.g. in this case Soul Tree's India site is scraped (it may have a US site)
chrome_driver_service = Service('/usr/bin/chromedriver')
#chrome_driver_service = Service('/home/thcthchk/chrome_driver/chromedriver')

#------- Set up the URL headers for Selenium -------------

# when including user agent, requests has form: requests.get(url, headers= headers)

import random

header_1 = 'Mozilla/5.0 (X11; CrOS x86_64 14150.64.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.104 Safari/537.36'
header_2 = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.124 Safari/537.36'
header_3 = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.39 Safari/537.36'
header_4 = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'
header_5 = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
header_6 = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'

user_agent_list = [header_1, header_2, header_3, header_4, header_5, header_6]

user_agent_rand = random.choice(user_agent_list)

referer = 'https://google.com'

headers = {'user agent': user_agent_rand, 'referer': referer}




###########################################################################################################################
##############  SECTION III - Define the 3 functions for scraping different types of info    ##############################
###########################################################################################################################

#### Note - we have 3 functions:
###### Function I 'product_list_scrape' - this specialises in scraping the list of products fir File I (Product List) and File III (product category list)
###### Function II 'category_tag_scrape' - this specialises in scraping the categories available to populate File II (category list); the category URL will then be run in Function I to get list of products per category to create File III (product category list)
###### Function III 'product_details_scrape' - this specialises in scraping each product's product details page, to create File IV (product details list) 

#--------- Set up stage - the functions ---------

################### function definition------------------------------------------
def product_list_scrape(page_url):
    global p_name_output_list
    global p_url_output_list
    global pg_num
    p_name_output_list = []
    p_url_output_list = []

    options = webdriver.ChromeOptions()
    #options.headless = True
    driver = webdriver.Chrome(service = chrome_driver_service, options=options)
    #driver.maximize_window()
##    driver = webdriver.Chrome(service = chrome_driver_service)

    user_agent_rand = random.choice(user_agent_list)
    headers = {'userAgent': user_agent_rand}
    driver.execute_cdp_cmd('Network.setUserAgentOverride', headers)


    try:
##        print(page_url)
        driver.get(page_url)
        time.sleep(1)        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        #### Add codes to accept cookies, exit modals, open 'full ingredients' section etc

        pageHtml = driver.page_source
        soup = HTMLParser(pageHtml)

#        page = requests.get(page_url)
#        soup = HTMLParser(page.text)

        try:
            posting = soup.css_first('div[class = "collection-grid__wrapper"]').css('div[class = "product-block__inner"]')
        except:
            posting = []
        print(len(posting))

        if len(posting) > 0: 

            for p in posting:

                try:
                    p_url = p.css_first('a').attributes['href']      #### Use this to grab the product URL
                    #need to simplify the URL to remove association with specific type/collection/skin concern, so that product URLs are not duplicated for the same product 
                    ####(same product may have different URLs in different categories  )
                    p_url = p_url[p_url.rfind('/product'):]
                    p_url = 'https://www.soultree.in' + p_url
                    #print('step 0 product url: ' + str(p_url))
                    
                    p_name = p.css_first('h3[class = "product-block__title"]').text().strip() ### Use this to get the product name. Note - may need to include the collection name 
                    print('p_name is : ' + str(p_name))

                    p_name_output_list.append(p_name)
                    p_url_output_list.append(p_url)


                except Exception as e:
                    print('Step 0 error: ' + str(e))
        else:
            pg_num = 1000  ##### by setting pg_num = 1000, this will force-quit this function when executed in the for loop in Section IV
    except Exception as e:
        print('>>>>>> Step 0 error: ' + str(e))
        pg_num = 1000

    try:
        driver.quit()
    except:
        pass

    return p_name_output_list
    return p_url_output_list

#####################------------------------

################ define function for category tags

# for categories, there are two parts - the product category menu at top of page (navigation), and the filter tags within 'all--products' (the left hand side of the product list pages, e.g.  https://www.soultree.in/collections/all-skin-care).

def category_tag_scrape(input_url):
    global c_name_list
    global c_url_list

    c_name_1_list = []
    c_url_1_list = []


    page = requests.get(input_url)  ### Note - no Selenium needed as the HTML data could be fetched using Request. Cut down the run time
    soup = HTMLParser(page.text)

    #Part I - get tags from drop-down menu (navigation bar)
    listing = soup.css_first('ul[class = "menu menu--has-meganav"]').css('a')
    print('dropdown menu number: ' + str(len(listing)))

    if len(listing) > 0:
        for l in listing:
            try:        
                c_name = l.text().strip()
                if c_name == '':
                    c_name = 'unknown'
                else:
                    pass
                    #re.sub('([\(\[]).*?([\)\]])','', c_name)
                try:
                    c_url = l.attributes['href']
                    if c_url == '':
                        c_url = 'unknown'
                    else:
                        c_url = c_url.replace('https://www.soultree.in','')  #### Note - some menu href have prefix 'https://www.soultree.in/category_name' , some only have '/category_name', we need to regularise them
                        c_url = 'https://www.soultree.in' + c_url
                        #c_url = c_url[c_url.index('/en_GB'):]
                        #c_url = 'https://www.no7beauty.co.uk' + c_url
                except:
                    c_url = 'unknown'
                if c_url =='https://www.soultree.in#':  #### Note - if there are too many dummy categories, remove them so that the Files are not noisy 
                    pass
                else:
                    c_name_list.append(c_name)
                    c_url_list.append(c_url)
                if l.attributes['class'] == 'menu-item__link' and c_url != 'https://www.soultree.in#' :   ### Note - here we extract only the topline categories (e.g. Skincare, Bath Care, Hair Care) in the navigation bar and use it to look for the categories tags within each topline category. 
                                                                                                        ############ Otherwise we will be looking for in-page filter tags for far too many duplicating pages 
                    c_name_1_list.append(c_name)
                    c_url_1_list.append(c_url)
                else:
                    pass
            except Exception as e:
                    print('Step 1 error: ' + str(e))
    else:
        pass
    
    try:
        driver.quit()
    except:
        pass

    # scrape the filter tags within each category - as mentioned above, we only limit ourselves to the topline categories, to prevent duplicating filter category tags within each product category and excessive runtime 
    c_url_for_tags = list(tuple(c_url_1_list))
    c_name_for_tags = list(tuple(c_name_1_list))

    for i in range(0,len(c_url_for_tags)):
        print('the filter tags to get : ' + str(c_url_for_tags[i]))
        try:
            page = requests.get(c_url_for_tags[i])
            soup = HTMLParser(page.text)  
            filter_tag_list = soup.css_first('div[class = "collection__filters-list"]').css_first('div[class = "collection__filter-container"]').css('a')
            print('number of filter tags : ' + str(len(filter_tag_list)))
            if len(filter_tag_list) >= 0:
                for j in filter_tag_list:
                    try:
                        c_url = j.attributes['href']
                        c_url = c_url.replace('https://www.soultree.in', '')
                        c_url = 'https://www.soultree.in' + c_url
                        c_name = j.text().strip()
                        #Need to remove the 'number of eligible products under this tag'
                    
                        c_name = c_name_for_tags[i] + ' ' + c_name

                        c_name_list.append(c_name)
                        c_url_list.append(c_url)
                    except:
                        pass

            else:
                pass
        except:
            pass



################################### end of category tags function

###########------------ product details function defining ------
def product_details_scrape(input_url):

    global p_url_list_3
    global p_name_list_3
    global p_ingre_list  ### this is for full ingnredients
    global p_key_ingre_list   ### this is for key ingredients
    global p_description_list   ### this is for product descriptions   
    global p_price_normal_list   ### this is for the regular price
    global p_price_sale_list    ### this is for the on-sale price
    global p_sale_list          ### this is for Y/N on whether a product is on sale
    global p_out_of_stock_list    #### this is for Y/N on whether a product is out-of-stock

    try:
            print(input_url)

            page = requests.get(input_url)
            soup = HTMLParser(page.text)

            

            try:
                p_name = soup.css_first('h1[class = "product-title"]').text().strip()
            except:
                p_name = 'N/A'

#-- find full ingredients

            #Note - ingredients/INCI lists are within the 'Ingredients' content tab
            full_ingre_1 = ''

            counter = 0
            ingre_loc = ''
            try:
                content_tabs = soup.css_first('div[class = "product-tabs-nav"]').css('button[class ^= "product-tab-title"]')
                for ct in content_tabs:
                    heading = ct.text().strip().lower()
                    if 'ingredient' in heading:
                        ingre_loc = counter
                    else:
                        pass
                    counter += 1
                if ingre_loc == '':
                    pass
                else:
                    full_ingre_1 = soup.css_first('div[class = "product-tabs-contents"]').css('div[class ^= "product-tab-content rte"]')[ingre_loc].text().strip()
            except:
                pass

            if full_ingre_1 == '':
                full_ingre_1 = 'N/A'
            else:
                pass

            print('full_ingre_1 = ' + str(full_ingre_1) )  ### Note - print out the scraped data so that we could observe abnormalities

#-- find key ingredients
            # Code for recording key ingredients - usually a description of the active ingredients 

#-- get descriptions
            # Code for recording product descriptions
            # Include both 'headline description' (usually at the top, around the product name, price info etc) and the detailed description (usually under the product name/price/add to cart area, and in tabs) 

#-- get price info
            #note - No on sale items for this brand at time of script creation
            price_normal = 'N/A'   ### this is the regular price 
            price_sale = 'N/A'    ### this is the on-sale price
            sale_1_0 = 'N'        #### if 'Y', the product is on sale, otherwise 'N' 

            try:
                price_normal = soup.css_first('div[class = "priceBox-btn"]').css_first('div[class = "product__price"]').css_first('span').text().strip()
                ##### Add scripts here to detect whether a product is on sale, then capture price_sale and change sale_1_0 to 'Y'
            except:
                pass         

            print('price_normal = ' + str(price_normal))    ### Note - print out the scraped data so that we could observe abnormalities
            print('price_sale = ' + str(price_sale))       ### Note - print out the scraped data so that we could observe abnormalities
            print('sale_1_0 = ' + str(sale_1_0))          ### Note - print out the scraped data so that we could observe abnormalities

#--- see if out of stock
            # Please explain how 'out of stock' is detected -  if out of stock, the ad-to-cart button is still displayed but disabled and have 'sold out' text
            
            out_of_stock_1_0 = 'N'    ### Note - if a product is out of stock, then 'out_of_stock_1_0' is 'Y'; if unknown or it's available to buy, then use 'N'

            try:
                buy_button = soup.css_first('div[class = "addBox-btn"]').css_first('button[name = "add"]')
                buy_button_1 = buy_button.text().strip().lower()
                buy_button_1.index('add')
                try:
                    buy_button.attributes['disabled']
                    out_of_stock_1_0 = 'Y'
                except:
                    pass
            except:
                out_of_stock_1_0 = 'Y'


            print('out_of_stock_1_0 = ' + str(out_of_stock_1_0))

            p_url_list_3.append(input_url)
            p_name_list_3.append(p_name)
            p_ingre_list.append(full_ingre_1)
            p_key_ingre_list.append(key_ingre_1)
            p_description_list.append(p_descrption)
            p_price_normal_list.append(price_normal)
            p_price_sale_list.append(price_sale)
            p_sale_list.append(sale_1_0)
            p_out_of_stock_list.append(out_of_stock_1_0)

    except Exception as e:
        print('Step 3 Error: ' + str(e))


    try:
        driver.quit()
    except:
        pass

####################---------------------------------

###########################################################################################################################
##############  SECTION IV - Execute the 3 functions to get data    #######################################################
###########################################################################################################################

#---- Step 0: create starting list of products table -------------
#Example URL with page number ---- https://www.soultree.in/collections/all-skin-care?page=3

print('Step 0 - create product table')

url_list = []
product_name_list= []

main_cate_url = [ 'https://www.soultree.in/collections/all-skin-care' , 'https://www.soultree.in/collections/all-hair-care-products' , 'https://www.soultree.in/collections/all-bath-care' , 'https://www.soultree.in/collections/all-makeup' , 'https://www.soultree.in/collections/rituals' , 'https://www.soultree.in/collections/gifting' ]
for url_0 in main_cate_url:
    pg_num = 1
    url_1 = '?page='

    while pg_num <= 15:    ####Note - loop through the pages

        print('Step 0: Pg ' + str(pg_num))

        url = url_0 + url_1 + str(pg_num)

        product_list_scrape(url)

        url_list.extend(p_url_output_list)
        product_name_list.extend(p_name_output_list)

        pg_num += 1


product_table =pd.DataFrame({'URL':url_list, 'Brand Name': brand_name_locale, 'Product Name': product_name_list, 'scrape_date': today})

product_table = product_table.drop_duplicates(subset = ['URL'])   ##### remember to de-duplicate


#---- Step 1: create category table -------------

print('Step 1 -- create category table ')

c_name_list = []
c_url_list = []

url = 'https://www.soultree.in/'
category_tag_scrape(url)

category_table = pd.DataFrame({'Category name': c_name_list, 'Category URL': c_url_list, 'Brand name': brand_name_locale, 'scrape_date': today})

category_table = category_table.drop_duplicates(subset = ['Category URL'])

#some category names are empty - give 'unknown' designation for now

category_table['Category name'].replace('', 'unknown', inplace = True)
category_table['Category URL'].replace('', 'unknown', inplace = True)

#------------ Step 2: create category product table & get product details - toggle between functions -----------

##### Note - in this loop function, we would scrape one category to get its list of product, then scrape the product details page of one product. This usually disarms anti-scrape detection mechanisms
##### Note - at the step, we may miss out on scraping product details for products that are only present in very specific categories. There is a 'backup' Step 3 for these missed products 

print('Step 2: create category product table')

#-- for category product scrape
p_url_list = []
p_name_list = []
c_url_list_1 = []
c_name_list_1 = []
#reuse c_url_list above
# reuse c_name_list above


#-- for product details scrape
p_url_list_3 = []
p_name_list_3 = []
p_ingre_list = []
p_price_normal_list = []
p_price_sale_list = []
p_sale_list = []
p_out_of_stock_list = []

#-- get category product list

for i in range(0,10000):

    if i< len(c_url_list):

        c_url = c_url_list[i]
        c_name = c_name_list[i]
        try:
            print(c_name)
            print(c_url)
        except:
            pass

        pg_num = 1
        url_1 = '?page='
        url_1b = '&page='

        while pg_num <= 15:
            print('page: ' + str(pg_num))
            try:
                if c_url.find('?') >= 0:   #### Note - different URL suffix for page numbers based on URL structure
                    url = c_url + url_1b + str(pg_num)
                else:
                    url = c_url + url_1 + str(pg_num)
            except Exception as e:
                print('Step 2 get category product list error: ' + str(e))
                url = 'N/A'

            product_list_scrape(url)

            p_url_list.extend(p_url_output_list)
            p_name_list.extend(p_name_output_list)

            c_url_list_1.extend([c_url]*len(p_url_output_list))
            c_name_list_1.extend([c_name]*len(p_name_output_list))

            pg_num += 1

        time.sleep(3)
    else:
        pass

    #-- get product details
    if i < len(url_list):
            url = url_list[i]
            product_details_scrape(url)
            time.sleep(2)
    else:
            pass

category_product_table = pd.DataFrame({'URL':p_url_list, 'Name':p_name_list, 'Category tag': c_name_list_1, 'Category URL': c_url_list_1, 'Brand name':brand_name_locale, 'scrape_date': today})
category_product_table = category_product_table.drop_duplicates(subset = ['URL', 'Category URL'])

#------ Step 2a: Concat category product table with product table to ensure all products are included, especially the out of stock ones -----
print('Step 2a: Concat category product table with product table to ensure all products are included')
product_table_1 = category_product_table.drop_duplicates(subset = ['URL'])
product_table_1 = product_table_1[['URL', 'Brand name', 'Name', 'scrape_date']]
product_table_1 = product_table_1.rename(columns = {'Name': 'Product Name', 'Brand name': 'Brand Name'})

product_table = pd.concat([product_table, product_table_1], ignore_index = True)  ### note - we combine the product_table in Step 1 with data collected from Step 2 so that we have a complete product_table (no product missed out) 

product_table = product_table.drop_duplicates(subset = ['URL'])


#----- Step 3: create product details table ------------

#### Note: in this step we identify products that do not have their product details scraped, then apply the 'product_details_scrape' function to scrape them

print('Step 3: create product details table')
new_product_table_url_list = product_table['URL'].tolist()

product_list_working = []
product_list_working = list(set(new_product_table_url_list) - set(url_list))

for i in product_list_working:
    url = i
    product_details_scrape(url)
    time.sleep(1)


product_details_table = pd.DataFrame({'URL': p_url_list_3, 'Brand Name': brand_name_locale, 'Product Name': p_name_list_3, 'Full ingredients': p_ingre_list, 'Key ingredients': p_key_ingre_list, 'Price': p_price_normal_list, 'Sale': p_sale_list,'Sale Price': p_price_sale_list, 'Descriptions': p_description_list, 'Sold Out?': p_out_of_stock_list, 'New Arrival?': '', 'scrape_date': today})
product_details_table = product_details_table.drop_duplicates(subset = ['URL'])


###########################################################################################################################
##############  SECTION V - Output the 4 files    #######################################################
###########################################################################################################################
product_table_csv = '/home/thcthchk/{}_product_table.csv'.format(brand_name_locale)
category_table_csv = '/home/thcthchk/{}_category_table.csv'.format(brand_name_locale)
category_product_table_csv = '/home/thcthchk/{}_category_product_table.csv'.format(brand_name_locale)
product_details_table_csv = '/home/thcthchk/{}_product_details_table.csv'.format(brand_name_locale)

product_table.to_csv(product_table_csv)
category_table.to_csv(category_table_csv)
category_product_table.to_csv(category_product_table_csv)
product_details_table.to_csv(product_details_table_csv)

print('############### Soul Tree IN DONE############')


###########################################################################################################################
##############  SECTION VI - Delete functions to save memory    #######################################################
###########################################################################################################################

try:
    del posting
except:
    pass
try:
    del product_table
    del category_table
    del category_product_table
    del product_details_table
except:
    pass
try:
    del p_url_list
    del p_name_list
    del p_url_list_3
    del p_name_list_3
    del p_ingre_list
    del p_price_normal_list
    del p_price_sale_list
    del p_sale_list
    del p_out_of_stock_list
except:
    pass
try:
    del c_url_list_1
    del c_name_list_1
    del url_list
    del product_name_list
    del c_url_list
    del c_name_list

except:
    pass

gc.collect()

t.stop()