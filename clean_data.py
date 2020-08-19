# Note: Manual setting ASIN col of Simulate sheet in clean_ASIN function
import json
import datetime
# from set_spreadsheet import set_spreadsheet, sheet_write, set_spreadsheet_o_o, set_spreadsheet_Research, add_many_list

##################################################
# Remove duplicate ItemLink
def clean_ItemLink():

	# Get column position from json
	with open('data_base_column_position.json', 'r', encoding='utf-8') as f:
		Column_dict = json.load(f)[0]
		ItemLink_col = Column_dict['ItemLink']	

	# Get sheet
	while True:
		try:
			eBay_Scraping = set_spreadsheet('eBay_Scraping')
			ItemLink = eBay_Scraping.col_values(ItemLink_col)
			break
		except:
			print('    clean_ItemLink error, sleep 60s and try again.')
			sleep(60)

	ItemLink.pop(0)

	# Clear duplicates
	Cleaned_ItemLink = list(dict.fromkeys(ItemLink))

	# Clear all col:
	clear = []
	for i in range(len(ItemLink)):
		clear.append('')
	sheet_write('eBay_Scraping', 2, ItemLink_col, len(clear)+1, ItemLink_col, clear)

	# Write data:
	w_data = ['ItemLink']
	w_data += Cleaned_ItemLink
	sheet_write('eBay_Scraping', 1, ItemLink_col, len(w_data), ItemLink_col, w_data)


##################################################
# Remove duplicate ASIN (Selling items)
def clean_ASIN():

	# Get selling ASIN in 〇_〇
	while True:
		try:
			Simulate = set_spreadsheet_o_o('Simulate')
			Selling = Simulate.col_values(5) # Manual setting
			ASIN_o_o = Simulate.col_values(6) # Manual setting
			break
		except:
			print('    clean_ASIN error 1, sleep 60s and try again.')
			sleep(60)

	Selling_ASIN_o_o = []
	for i in range(1, len(ASIN_o_o)):
		No_scrap_status = ['ー','●']
		if Selling[i] in No_scrap_status:
			Selling_ASIN_o_o.append(ASIN_o_o[i])


	# Get selling ASIN in o_o_Products Research
	while True:
		try:
			Simulate = set_spreadsheet_Research('Simulate')
			ASIN_Research = Simulate.col_values(5) # Manual setting
			break
		except:
			print('    clean_ASIN error 2, sleep 60s and try again.')
			sleep(60)

	# All ASIN
	Selling_ASIN = Selling_ASIN_o_o + ASIN_Research

	
	# Get Data of eBay scraping sheet:
	# Get column position from json
	with open('data_base_column_position.json', 'r', encoding='utf-8') as f:
		Column_dict = json.load(f)[0]
		NKV_col = Column_dict['NKV']
		ASIN_col = Column_dict['ASIN']
		ItemTitle_col = Column_dict['ItemTitle']

	while True:
		try:
			eBay_Scraping = set_spreadsheet('eBay_Scraping')
			data = eBay_Scraping.get_all_values()
			break
		except:
			print('    clean_ASIN error 2, sleep 60s and try again.')
			sleep(60)

	NKV = []
	ASIN = []
	ItemTitle = []
	for i in range(len(data)):
		NKV.append(data[i][NKV_col-1])
		ASIN.append(data[i][ASIN_col-1])
		ItemTitle.append(data[i][ItemTitle_col-1])

	#Check and remove duplicate:
	for i in range (1, len(ASIN) -1 ):

		if ASIN[i] in Selling_ASIN and ASIN[i] != '':
			print('    Selling ASIN removed: {}'.format(ASIN[i]))

			new_title = 'D_' + NKV[i] + '_' + ASIN[i] + '_' + ItemTitle[i] # Create new Title
			ItemTitle[i] = new_title
			NKV[i] = '' # Remove NKV
			ASIN[i] = '' # Remove ASIN

	# Write sheet:
	w_data = add_many_list([NKV, ASIN, ItemTitle])
	sheet_write('eBay_Scraping', 1, NKV_col, len(NKV), ItemTitle_col, w_data)

##################################################
# Copy to Scraped_Links
def copy_history():

	# Get column position from json
	with open('data_base_column_position.json', 'r', encoding='utf-8') as f:
		Column_dict = json.load(f)[0]
		ItemLink_col = Column_dict['ItemLink']
		NKV_col = Column_dict['NKV']
		ASIN_col = Column_dict['ASIN']
		Seller_col = Column_dict['Seller']
		Profit_Percent_col = Column_dict['Profit_Percent']
		Profit_col = Column_dict['Profit']

	# eBay_Scraping Sheet
	while True:
		try:
			eBay_Scraping = set_spreadsheet('eBay_Scraping')
			ItemLink = eBay_Scraping.col_values(ItemLink_col)
			NKV = eBay_Scraping.col_values(NKV_col)
			ASIN = eBay_Scraping.col_values(ASIN_col)
			Seller = eBay_Scraping.col_values(Seller_col)
			Profit_Percent = eBay_Scraping.col_values(Profit_Percent_col)
			Profit = eBay_Scraping.col_values(Profit_col)

			Scraped = set_spreadsheet('Scraped')
			Scraped_data = Scraped.get_all_values()
			break
		except:
			print('    copy_history error, sleep 60s and try again.')
			sleep(60)

	Scraped_Link = []
	Scraped_NKV = []
	Scraped_ASIN = []
	Scraped_Seller = []
	Scraped_Profit_Percent = []
	Scraped_Profit = []
	Day = []

	for i in range(1, len(ItemLink)):
		Scraped_Link.append(ItemLink[i])
		if i in range(len(NKV)):
			Scraped_NKV.append(NKV[i])
		else:
			Scraped_NKV.append('')
		if i in range(len(ASIN)):
			Scraped_ASIN.append(ASIN[i])
		else:
			Scraped_ASIN.append('')
		if i in range(len(Seller)):
			Scraped_Seller.append(Seller[i])
		else:
			Scraped_Seller.append('')
		if i in range(len(Profit_Percent)):
			Scraped_Profit_Percent.append(Profit_Percent[i])
		else:
			Scraped_Profit_Percent.append('')
		if i in range(len(Profit)):
			Scraped_Profit.append(Profit[i])
		else:
			Scraped_Profit.append('')
		Day.append(datetime.datetime.now().isoformat())

	# Write Scraped sheet
	w_data = add_many_list([Scraped_Link, Scraped_NKV, Scraped_ASIN, Scraped_Seller, 
		                    Scraped_Profit_Percent, Scraped_Profit, Day])
	# Create blank row to avoid errors the next time
	for i in range(7):
		w_data.append('')
	sheet_write('Scraped', len(Scraped_data)+1, 1, len(Scraped_data)+len(Scraped_Link)+1, 7, w_data)


##################################################
# Get next row = last row + 1 of colum in  Products Research
# spreadsheet = 'Products Research' > okie
# spreadsheet = ''o_o'' > Need setting Get column_position
def get_next_row(spreadsheet ,sheet, col, row):

	# Get column_position
	with open('data_base_column_position.json', 'r', encoding='utf-8') as f:
		Column_dict = json.load(f)[0]
		col = Column_dict[col]

	# Get sheet
	while True:
		try:
			if spreadsheet == 'Products Research':
				eBay_Scraping = set_spreadsheet(sheet)
			elif spreadsheet == 'o_o':
				eBay_Scraping = set_spreadsheet_o_o(sheet)

			col_data = eBay_Scraping.col_values(col)
			break
		except:
			print('    get_next_row error, sleep 60s and try again.')
			sleep(60)

	# Get row:
	if row == '':
		row = len(col_data) + 1
	if row < 2:
		row = 2

	return row


##################################################
# Ex: 37.74/ea > 37.74
# Convert str_ to float
def to_float(str_):

	if type(str_) in [float,int] or str_ == '':
		return str_
	else:
		res = ''
		for i in str_:
			if i.isdigit() or i in ['.']:
				res += i
		try:
			res = float(res)
		except:
			res = ''
			print('   to_float error. Can not convert to fload')
		return res

##################################################
if __name__ == '__main__':
	print('    Have not main function.')
	# row = get_next_row(spreadsheet= 'Products Research',sheet='eBay_Scraping', col='Lower_Price_1', row ='')
	# print(type(row))
	# copy_history()
	# print(to_float('123'))
	clean_ASIN()

