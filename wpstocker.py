"""Classes and functions to operate Google Spreadsheets via API
and MySQL DB using ORM
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# DB stuff
echo = False
engine = create_engine('mysql+pymysql://bari:6q16f%5D2%3FIqm0%3DSx22x%23m@localhost/bari', echo=echo)
Base = declarative_base(engine)


class Posts(Base):
    """Posts table ORModel"""
    __tablename__ = 'wp_posts'
    __table_args__ = {'autoload':True}


class Postmeta(Base):
    """Postmeta table ORModel"""
    __tablename__ = 'wp_postmeta'
    __table_args__ = {'autoload':True}
 

def loadSession():
    """Connect to WP MySQL"""
    metadata = Base.metadata
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_meta_value(post_id, meta_key, session):
    """Get meta_value of meta_key for particular product by it's id"""
    return session.query(Postmeta).filter_by(post_id=post_id, meta_key=meta_key).first().meta_value


def get_all_products():
    """Return list containing list of product info"""
    session = loadSession()
    products = []
    posts = session.query(Posts).filter_by(post_type="product")
    for post in posts:
        sku = get_meta_value(post.ID, "_sku", session=session)
        price = get_meta_value(post.ID, "_price", session=session)
        stock = get_meta_value(post.ID, "_stock", session=session)
        if not stock:
            stock = '--'
        # print(f"ID: {post.ID}, Product: {post.post_title}, SKU: {sku}, Price: {price}, Stock: {stock}")
        products.append([post.ID, post.post_title, sku, price, stock])
        
    return products

def update_products(rows):
    """"""
    session = loadSession()

    for row in rows:
        # TODO: make it try block if spreadsheet scheme is corrupted
        product_id = row[0]
        product_title = row[1]
        sku_value = row[2]
        price_value = row[3]
        stock_value = row[4]
        # get product meta_keyS
        sku = session.query(Postmeta).filter_by(post_id=product_id, meta_key="_sku").first()
        price = session.query(Postmeta).filter_by(post_id=product_id, meta_key="_price").first()
        stock = session.query(Postmeta).filter_by(post_id=product_id, meta_key="_stock").first()
        try:
            manage = session.query(Postmeta).filter_by(post_id=product_id, meta_key="_manage_stock").first()
            if stock_value != "--":
                int(stock_value)
                manage.meta_value = "yes"
            elif stock_value == "--":
                manage.meta_value = "no"
        except:
            pass

        # assign new values
        sku.meta_value = sku_value
        price.meta_value = price_value
        stock.meta_value = stock_value
    session.commit()

# Spreadsheets stuff
scope = ["https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
        ]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open("bari_wordpress").sheet1


def export_products():
    """Export all products from DB to spreadsheet, rewrite all rows except header"""
    sheet.resize(rows=1) # reset sheet by resizing it to only 1 row with headers
    for product in get_all_products():
        sheet.append_row(product)


def get_list_of_rows():
    """"""
    rows = []
    data = sheet.get_all_records()
    for dick in data:
        rows.append(list(dick.values()))
    return rows
