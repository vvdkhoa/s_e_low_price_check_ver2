# ebay_low_price_check_ver2
# 2019/12
# Scrapt low price on eBay > save to database Postgre SQL > read database and save to google sheet:

# CREATE Database Postgre SQL
# Service 

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
