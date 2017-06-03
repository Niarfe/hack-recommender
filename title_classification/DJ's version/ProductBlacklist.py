from django.utils.encoding import smart_str

class ProductBlacklist:
    def __init__(self, db):
        self.db = db
        self.product_ids = set()

    def add_products_with_tag_id(self, tag_id):
        """ create a product blacklist of products that are from the category of vertical market,
        it returns a dictionary with product id is key and the product name from the category of veritcal market as value"""
        # get urls
        c = self.db.cursor(buffered=True)
        query = ("""select p.name, pt.product_id from production.products p
                     join production.products_tags pt on p.id=pt.product_id
                     join production.tags t on pt.tag_id=t.id
                     where t.id={};""")
        query = query.format(tag_id)
        iterable = c.execute(query, multi=True)
        black_prod_dict = {}
        for item in iterable:
            for result in item.fetchall():
                product_name = result[0]
                product_id = result[1]
                if product_id not in black_prod_dict:
                    black_prod_dict[product_id] = product_name
        set.update(set(black_prod_dict.keys()))

    def add_old_products(self, min_last_date_verified, target_urls):
        """ filter products by last verification date,
                create a black list of products that is verified before most_recent_verified_date,
                it returns a dictionary with url as key and value is the product id of the outdated products."""
        clean_urls = [smart_str(url) for url in target_urls]
        str_urls = map(str, clean_urls)
        # print str_urls
        c = self.db.cursor(buffered=True)
        if len(str_urls) > 1:
            query = ("""SELECT url, product_id, last_verified_at
                                 FROM matcher.url_mrf_global_hits
                                 WHERE url IN {} and last_verified_at < '{}';""")
            query = query.format(tuple(str_urls), min_last_date_verified)
        else:
            query = ("""SELECT url, product_id, last_verified_at
                                 FROM matcher.url_mrf_global_hits
                                 WHERE url = '{}' and last_verified_at < '{}';""")
            element = ' '.join(str(x) for x in str_urls)
            query = query.format(element, min_last_date_verified)
        # print query
        iterable = c.execute(query, multi=True)
        black_dict = {}
        for item in iterable:
            for result in item.fetchall():
                url = result[0]
                product_id = result[1]
                if url not in black_dict:
                    black_dict[url] = []
                    if product_id not in black_dict[url]:
                        black_dict[url].append(product_id)
        # print 'black dictionary', black_dict
        set.update(set(black_dict.keys()))
