import sqlite3

################################################################
# Read command # http://osanai.org/61/
def sqlite(command):

	DATABASE = 'price_manager.db'
	conn = None
	try:
		conn = sqlite3.connect(DATABASE)
		conn.execute(command)
		conn.commit()
		conn.close()
	except(Exception) as error:
		print(error)
	finally:
		if conn is not None:
			conn.close()

################################################################
# Get data
def sqlite_get_list(command):

	DATABASE = 'price_manager.db'
	conn = None
	try:
		conn = sqlite3.connect(DATABASE)
		cur = conn.execute(command)
		return [list(i) for i in cur.fetchall()]
		conn.commit()
		conn.close()
	except (Exception) as error:
	    print(error)
	finally:
	    if conn is not None:
	        conn.close()

################################################################
if __name__ == '__main__':

	# sqlite('DELETE FROM count_limit')
	print(sqlite_get_list('SELECT * from count_limit'))




# Create count_limit table #
# command = """
# 	CREATE TABLE IF NOT EXISTS count_limit
# 	(day DATE PRIMARY KEY,
# 	count INTEGER,
# 	last_update TIMESTAMP WITH TIME ZONE
# 	)"""