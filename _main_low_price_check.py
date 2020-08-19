from ebaysdk.finding import Connection
import json
import urllib.parse
from datetime import datetime
import pytz
import sqlite3
import re
import decimal

# Custom function
from sql_postgresql import postgresql_local, postgresql_local_get_list
from clean_data import to_float
from sql_sqlite3 import sqlite, sqlite_get_list
from set_spreadsheet import set_spreadsheet_o_o
from set_spreadsheet import sheet_write_eBay_getPrices_2
from set_spreadsheet import clean_eBay_getPrice_2

# from set_spreadsheet import set_spreadsheet_eBay_getPrices_2


######################################################################################
# Return: {'Price': [low1, low2, low3], 'Error': []}
# https://gist.github.com/davidtsadler/6993747
# Limit: https://developer.ebay.com/support/api-call-limits
# Limit 5,000 API calls per day
def get_low_price(nkv):

	# Get setting from json file
    with open('data_base_eBayDevelopers.json', 'r', encoding='utf-8') as f:
    	Developers_dict = json.load(f)[0]
    	AppID = Developers_dict['AppID']
    	SiteId = Developers_dict['SiteId']
    	ItemLocation = Developers_dict['ItemLocation']
    	GetPriceQuantity = Developers_dict['GetPriceQuantity'] #Get only n lower price

    res_dic = {}
    price_list = []

    if nkv == '':
        return {}
    else:

        try:
            api = Connection(siteid=SiteId, appid=AppID, config_file=None)
            api.execute('findItemsAdvanced', {
                'keywords': nkv,
                'itemFilter': [
                    {'name': 'Condition', 'value': 'New'},
                    {'name': 'listingType', 'value': 'FixedPrice'} ],
                'paginationInput': {
                    'entriesPerPage': '25', #Get max 25 items information
                    'pageNumber': '1'},
                'sortOrder': 'CurrentPriceLowest'
            })

            dictstr = api.response.dict()

            i = 1
            for item in dictstr['searchResult']['item']:
            	if item['location'] == ItemLocation:
            		Price = float(item['sellingStatus']['convertedCurrentPrice']['value'])
            		ShippingCost = float(item['shippingInfo']['shippingServiceCost']['value'])
            		price_list.append( round(Price+ShippingCost, 2))
            		i += 1

            price_list = sorted(price_list)
            price_list = price_list[:GetPriceQuantity]
            res_dic['Error'] = ['']

        except:
            price_list = []
            res_dic['Error'] = ['Not found']

        if len(price_list) < GetPriceQuantity:
            for i in range(GetPriceQuantity - len(price_list)):
                price_list.append(None)
        res_dic['Price'] = price_list

    return res_dic
        	

###############################################################
# Confirm API call limit of eBay Develope
def finding_limit_count():

    pst = pytz.timezone('America/Los_Angeles') # https://www.journaldev.com/23270/python-current-date-time
    now_pts_date = "{0:%Y-%m-%d}".format(datetime.now(pst)) # https://www.sejuku.net/blog/70314
    now_pts_datetime = "{0:%Y-%m-%d %H:%M:%S}".format(datetime.now(pst))
    
    try: # Get count value until now and Update new count value
        command_1 = "SELECT count FROM count_limit WHERE day = '%s' " % now_pts_date
        count = sqlite_get_list(command_1)[0][0]
        count += 1

        command_2 = """
            UPDATE count_limit SET (count, last_update) = ('%s', '%s') WHERE day = '%s'
            """ % (count, now_pts_datetime, now_pts_date)
        sqlite(command_2)

    except: # Insert the first value
        command_2 = """
            INSERT INTO count_limit(day, count, last_update) VALUES ('%s', 1, '%s')
            """ % (now_pts_date, now_pts_datetime)
        sqlite(command_2)
        count = 1

    return(count) 


###############################################################
# Get nkv from check link
def get_nkv(checkLink):

    checkLink = urllib.parse.unquote(checkLink) # Get nkv
    replace_list_1 = ['nkw=', '&', ': +', ' +', '   +'] # Replace to ''
    replace_list_2 = ['+'] # Replace to ' '
    try: 
        nkv = re.search(r'nkw=.*?&', checkLink).group(0)
        for r1 in replace_list_1:
            try:
                nkv = nkv.replace(r1, '')
            except:
                pass
        for r2 in replace_list_2:
            try:
                nkv = nkv.replace(r2, ' ')
            except:
                pass
        nkv = nkv.strip() # Remove Spaces
    except:
        nkv = ''

    if len(nkv) > 15:   # Get error_nkv
            error_nkv = 'NKV too long'
    elif len(nkv) == 0:
        error_nkv = 'Please add nkv'
    else:
         error_nkv = ''

    return {'nkv':nkv, 'error_nkv':error_nkv}


###############################################################
def get_check_data():   # Get check data from o_o

	# Get column_position
    with open('data_base_column_position_o_o.json', 'r', encoding='utf-8') as f:
        Column_dict_1 = json.load(f)[0]
        SellPriceCheck_col = Column_dict_1['SellPriceCheck']
        ASIN_col = Column_dict_1['ASIN']
        eBayCheckLink_col = Column_dict_1['eBayCheckLink']
        StartPrice_col = Column_dict_1['StartPrice']

    # Get All List ASIN...
    o_o = set_spreadsheet_o_o('Simulate')
    data = o_o.get_all_values()

    SellPriceCheck = []
    ASIN = []
    eBayCheckLink = []
    StartPrice = []
    for i in range(len(data)):
        SellPriceCheck.append(data[i][SellPriceCheck_col-1])
        ASIN.append(data[i][ASIN_col-1])
        eBayCheckLink.append(data[i][eBayCheckLink_col-1])
        StartPrice.append(data[i][StartPrice_col-1])
    
    result = {}
    for i in range(1, len(SellPriceCheck)): 
        if SellPriceCheck[i] == '✔' and ASIN[i]!= '':
            res = get_nkv(eBayCheckLink[i])
            result[ASIN[i]] = (ASIN[i], res['nkv'], eBayCheckLink[i], to_float(str_= StartPrice[i]), res['error_nkv'])
            
    return result


###############################################################
# Get exits data on  ebaygetprice Not updated within *** 12 hours ***
def get_exits_data(col_name):

    res = []
    command = """SELECT {} FROM ebaygetprice
        WHERE ((CURRENT_TIMESTAMP - INTERVAL '12 HOURS') > update_time) OR (update_time IS NULL)
        """.format(col_name)
    for i in postgresql_local_get_list(command):
        res += i
    return res


###############################################################
# Copy data from ebaygetprice database to eBay_getPrices_2 google spreadsheet
def copy_data():

    f_row = ['CheckBox','No','ASIN','eBayCheckLink','NKV','StartPrice','Manual check',
                'Lower_Price_1','Lower_Price_2','Lower_Price_3', 'Error_NKV', 'Error_Price', 'Update_Time']
    sheet_write_eBay_getPrices_2('eBay_getPrices_2',1,1,1,len(f_row), f_row)

    clean_eBay_getPrice_2('eBay_getPrices_2')

    res = []
    command = """SELECT asin, ebay_check_link, nkv, start_price, manual_check, low_price_1,
            low_price_2, low_price_3, error_nkv, error_price, update_time FROM ebaygetprice """
    list_of_list = postgresql_local_get_list(command)
    for i in list_of_list:
        res += i

    # Change data type
    res_convert = []
    for j in res:
        if type(j) is decimal.Decimal:
            res_convert.append(float(j))
        elif type(j) is datetime:
            res_convert.append(str(j))
        elif j is None:
            res_convert.append('')
        else:
            res_convert.append(j)

    # Write to sheet
    sheet_write_eBay_getPrices_2('eBay_getPrices_2',
        2,3,len( list_of_list)+1, len(list_of_list[0])+2, res_convert)


###############################################################
# Delete all record of ebaygetprice and update new
def main_update_data_all():

    # Delete all record in ebaygetprice table
    print('    Start update, please wait')
    postgresql_local( "DELETE FROM ebaygetprice" ) 

    check_data = get_check_data()   # Update new data
    for asin in check_data:
        print('    Update, asin: {}'.format(asin))
        (asin, nkv, ebay_check_link, start_price, error_nkv) = check_data[asin]

        command = """ INSERT INTO ebaygetprice(asin, nkv, ebay_check_link, start_price, error_nkv)
                VALUES ('{}','{}','{}',{},'{}')""".format(asin, nkv, ebay_check_link, start_price, error_nkv)
        postgresql_local(command)

    print('    Data updated')


###############################################################
# Update data for ebaygetprice
def main_update_data():

    print('Update data')

    # Get data from o_o
    new_data = get_check_data() # {asin: (asin, nkv, ebay_check_link, start_price, error_nkv), ...}

    # Get data from ebaygetprice table
    command_1 = """ 
        SELECT asin, nkv, ebay_check_link, start_price, error_nkv FROM ebaygetprice
        """
    old_data = {}
    data = postgresql_local_get_list(command_1)
    for record in data:

        if type(record[3]) is decimal.Decimal:
            start_price = float(record[3])
        elif type(record[3]) is None:
            start_price = ''
        else:
            start_price = ''

        old_data[record[0]] = (record[0], record[1], record[2], start_price, record[4]) # {asin: (asin, nkv, ebay_check_link, start_price, error_nkv), ...}

    # Compare and search new record:
    new_record = []
    for asin in new_data:
        if asin not in old_data:
            new_record.append(asin)
            print('Insert new record, ASIN: %s' % asin)
            command_2 = """
                INSERT INTO ebaygetprice (asin, nkv, ebay_check_link, start_price, error_nkv)
                VALUES ( '%s', '%s', '%s', %s, '%s')
                """ %( asin, new_data[asin][1], new_data[asin][2], new_data[asin][3], new_data[asin][4])
            postgresql_local(command_2)
    
    # Compare and search remove no neet to check record:
    remove_record = []
    for asin in old_data:
        if asin not in new_data:
            remove_record.append(asin)
            print('Remove record, ASIN: %s' % asin)
            command_3 = "DELETE FROM ebaygetprice WHERE asin = '%s'" % asin
            postgresql_local(command_3)

    # Compare and search changed record:
    update_record = list(new_data)
    sub = new_record + remove_record 
    update_record = [item for item in update_record if item not in sub]

    for asin in update_record:
        if new_data[asin] != old_data[asin]:
            print('Update record, ASIN: %s' % asin)
            command_4 = """
                UPDATE ebaygetprice SET (asin, nkv, ebay_check_link, start_price, error_nkv) = ('%s','%s','%s',%s,'%s')
                WHERE asin = '%s'
                """ %( asin, new_data[asin][1], new_data[asin][2], new_data[asin][3], new_data[asin][4], asin)
            postgresql_local(command_4)      

    print('Data updated successfully')
    print('-------------------------')

###############################################################
# Get nkv list from database => scrapt => write database
def main_scrapt_low_price():

	print('Scrap low price.')

	all_nkv = get_exits_data('nkv')
	all_nkv = list( dict.fromkeys(all_nkv) )    # Remove Duplicates
	try:
	    all_nkv.remove('')                      # Remove ''
	except:
	    pass

	i = 1
	for nkv in all_nkv:

	    # Confirm limit
	    count = finding_limit_count()
	    if count > 5000: # eBay API Limit
	        print('    Has reached 5000 API limits today, Please continue on tomorrow (PTS time)')
	        copy_data()
	        break

	    res = get_low_price(nkv) # {'Price': [low1, low2, low3], 'Error': []}
	    print('    Remaining: {} / API limit: {} / nkv: {} / {} '.format(len(all_nkv)-i, 5000-count, nkv, res) )
	    i += 1

	    low1 = res['Price'][0]
	    low2 = res['Price'][1]
	    low3 = res['Price'][2]
	    error = res['Error'][0]

	    command = """
	        BEGIN TRANSACTION;
	        --
	        UPDATE ebaygetprice SET low_price_1 = CAST(NULLIF('{}', 'None') AS NUMERIC)
	        WHERE nkv = '{}';
	        --
	        UPDATE ebaygetprice SET low_price_2 = CAST(NULLIF('{}', 'None') AS NUMERIC)
	        WHERE nkv = '{}';
	        --
	        UPDATE ebaygetprice SET low_price_3 = CAST(NULLIF('{}', 'None') AS NUMERIC)
	        WHERE nkv = '{}';
	        --
	        UPDATE ebaygetprice SET error_price = '{}'
	        WHERE nkv = '{}';
	        --
	        UPDATE ebaygetprice SET update_time = (SELECT CURRENT_TIMESTAMP)
	        WHERE nkv = '{}';
	        --
	        COMMIT;
	        """.format(low1, nkv, low2, nkv, low3, nkv, error, nkv, nkv)

	    postgresql_local(command)


###############################################################
if __name__ == '__main__':

    main_update_data()
    main_scrapt_low_price()
    copy_data()

    # Use when reset, Delete all record of ebaygetprice and update new
    # main_update_data_all():
    #-----------#





###############################################################
# CREATE ebaygetprice Table
"""
    CREATE TABLE ebayGetPrice
    (asin VARCHAR NOT NULL,
    nkv VARCHAR,
    ebay_check_link VARCHAR,
    start_price DECIMAL,
    low_price_1 DECIMAL,
    low_price_2 DECIMAL,
    low_price_3 DECIMAL,
    Lowest_price DECIMAL,
    error_price VARCHAR,
    error_nkv VARCHAR,
    manual_check VARCHAR,
    update_time TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (asin));
"""