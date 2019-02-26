# load selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from threading import Thread
import time
import sys
import base64
import json
from time import sleep

# =================================================================
# INITIAL ELEMENT
# =================================================================

URL_PIHPS = [
	"http://hargapangan.id/tabel-harga/pedagang-besar/daerah",
	"http://hargapangan.id/tabel-harga/pasar-tradisional/komoditas",
	"http://hargapangan.id/tabel-harga/pasar-modern/daerah",
	"http://hargapangan.id/tabel-harga/pasar-modern/komoditas",
	"http://hargapangan.id/tabel-harga/pedagang-besar/daerah",
	"http://hargapangan.id/tabel-harga/pedagang-besar/komoditas"
]

EL_KOMODITAS_ID = "filter_commodity_ids"
EL_PROVINSI_ID = "filter_province_ids"
EL_KABUPATEN_ID = "filter_regency_ids"
EL_PASAR_ID = "filter_market_ids"
EL_BUTTON_ID = "btnReport"
EL_TABLE_ID = "report"

# =================================================================
# FUNCTION DEFINITION
# =================================================================

def wait(web_opening_time=3):
	time.sleep(web_opening_time)

## load web driver for selenium : firefox
def web_driver_load():
	global driver
	options = Options()
	#options.set_headless(headless=True)
	driver = webdriver.Firefox(firefox_options=options, executable_path=r'geckodriver.exe')
	driver.implicitly_wait(20) # seconds

# quit web driver for selenium
def web_driver_quit():
	try :
		driver.quit()
	except Exception:
		pass
	finally:
		pass

def extract_select_ui(element_id,str_filter=None) :
	result = []
	try:
		filter_select_comodity = driver.find_element_by_xpath('//select[@id="'+element_id+'"]')
		options = [x for x in filter_select_comodity.find_elements_by_tag_name("option")]
		for element in options:
			content = []
			content.append(element.get_attribute("value"))
			content.append(element.text)
			if str_filter is not None :
				comp = element.get_attribute("value").find(str_filter)
				if comp == -1 :
					continue
			result.append(content)
	except Exception as e:
		print(e)
	finally:
		pass

	return result

def select_ui(element_id, select_text) :
	try:
		filter_select_comodity = driver.find_element_by_xpath('//select[@id="'+element_id+'"]')
		options = [x for x in filter_select_comodity.find_elements_by_tag_name("option")]
		for element in options:
			if(element.text == select_text):
				# menghilangkan select option
				select = Select(filter_select_comodity)
				select.deselect_all()
				element.click()
	except Exception as e:
		print(e)
	finally:
		pass

def button_ui(element_id):
	try:
		button_filter = driver.find_element_by_xpath('//button[@id="'+element_id+'"]')
		button_filter.click()
	except Exception as e:
		print(e)
	finally:
		pass

def table_ui(element_id) :

	data_tables = []
	# dapatkan TH value
	try:
		filter_select_date_comodity = driver.find_element_by_xpath('//table[@id="'+element_id+'"]')
		rows = [x for x in filter_select_date_comodity.find_elements_by_tag_name("th")]
		items = []
		for row in rows:
			items.append(row.text)
		
		data_tables.append(items)
	except Exception as e:
		print(e)
	finally:
		pass

	#dapatkan TD value
	try:
		filter_select_comodity = driver.find_element_by_xpath('//table[@id="'+element_id+'"]')
		rows = [x for x in filter_select_comodity.find_elements_by_tag_name("td")]
		items = []
		for row in rows:
			items.append(row.text)

		data_tables.append(items)
			
	except Exception as e:
		print(e)
	finally:
		pass

	return data_tables

# print array to file log data.json
def printToLog(data_list):
	try :
		print(data_list)
		with open('data.json', 'a') as outfile:
			outfile.write(json.dumps(data_list)+"\n")
	except Exception as e :
		print(e)

def process_non_auto_combobox(url=None,komoditas=None,provinsi=None,kabupaten=None,pasar=None):
	if url is not None :
		# go to url
		driver.get(url)
		# select combobox
		if komoditas is not None :
			select_ui(EL_KOMODITAS_ID,komoditas) 
		if provinsi is not None :
			select_ui(EL_PROVINSI_ID,provinsi) 
		if kabupaten is not None :
			select_ui(EL_KABUPATEN_ID,kabupaten) 
		if pasar is not None :
			select_ui(EL_PASAR_ID,pasar)
		# submit button form
		button_ui(EL_BUTTON_ID)
		# extract data table
		extract_table = table_ui(EL_TABLE_ID)
		
		if len(extract_table) > 0 :
			# print result output data.json
			# or change this code and save to database
			printToLog(extract_table)

def process_auto_combobox() :
	if len(URL_PIHPS) > 0 :
		for url in URL_PIHPS :
			driver.get(url)
			# iterasi komoditas
			# ambil semua text dari combobox semua	 komoditas
			kmdts_itr = extract_select_ui(EL_KOMODITAS_ID,"cat-")
			for i_kmdts in kmdts_itr :
				# iterasi provinsi
				# ambil semua text dari combobox semua provinsi
				prvs_itr = extract_select_ui(EL_PROVINSI_ID)
				for i_prvs in prvs_itr :
					# ambil proses robot di form dan masukkan database
					try :
						# select combobox
						select_ui(EL_KOMODITAS_ID,i_kmdts[1]) 
						select_ui(EL_PROVINSI_ID,i_prvs[1]) 
						# submit button form
						button_ui(EL_BUTTON_ID)
						# extract data table
						extract_table = table_ui(EL_TABLE_ID)

						result_dict = {
							"komoditas" : i_kmdts[1],
							"provinsi" : i_prvs[1],
							"data" : extract_table
						}
						printToLog(result_dict)
					except Exception as e :
						print(e)
	else :
		print("URL not found!")


# start scrap process
def scrap_start():
	process_auto_combobox()
	#driver.get("https://web.whatsapp.com/")

# =================================================================
# MAIN PROGRAM
# =================================================================
if __name__ == "__main__":
	# Load driver & Browser
	web_driver_load()
	# Waiting for login
	scrap_start()
	# quit from webdriver
	web_driver_quit()