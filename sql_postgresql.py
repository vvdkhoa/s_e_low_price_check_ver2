import psycopg2
import datetime


######################################################################################
# Desktop
# http://www.postgresqltutorial.com/postgresql-python/connect/
def postgresql_local(command):
	conn = None
	try:
		conn = psycopg2.connect(
			database = '',
			user = '',
			password = '',
			host = '')
		cur = conn.cursor()
		cur.execute(command)
		cur.close()
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
	    print(error)
	finally:
	    if conn is not None:
	        conn.close()

######################################################################################
# Desktop
# https://stackoverflow.com/questions/14835852/convert-sql-result-to-list-python
def postgresql_local_get_list(command):
	conn = None
	try:
		conn = psycopg2.connect(
			database = '',
			user = '',
			password = '',
			host = '') 	# No port need
		cur = conn.cursor()
		cur.execute(command) 		# sample: "SELECT asin, start_price FROM ebaygetprice"
		return [list(i) for i in cur.fetchall()]
		cur.close()
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
	    print(error)
	finally:
	    if conn is not None:
	        conn.close()

######################################################################################
# https://stackabuse.com/working-with-postgresql-in-python/
# https://stackoverflow.com/questions/902408/how-to-use-variables-in-sql-statement-in-python
# Heroku PostgreSQL run command postgresql-sinuous-65226
def postgresql_heroku(command):
	conn = None
	try:
		conn = psycopg2.connect(
			database = '',
			user = '',
			password = '',
			host = '',
			port=''
			)
		cur = conn.cursor()
		cur.execute(command)
		cur.close()
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
	    print(error)
	finally:
	    if conn is not None:
	        conn.close()

######################################################################################
# RDB PostgreSQL run command
def postgresql_rds(command):
	conn = None
	try:
		conn = psycopg2.connect(
			database = '',
			user = '',
			password = ' ',
			host = '',
			port=''
			)
		cur = conn.cursor()
		cur.execute(command)
		cur.close()
		conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
	    print(error)
	finally:
	    if conn is not None:
	        conn.close()

######################################################################################
if __name__ == '__main__':

	print('postgresql')

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
