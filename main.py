import sqlite3

from aiogram import Dispatcher, Bot, executor, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton, CallbackQuery, user
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
import wallet
from finct import generate_excel

TOKEN = "1401709439:AAF1G1VbZKEWg8sVs3OcBQ8hL0GeAsePBuY"
conn = sqlite3.Connection("shop_originals.db", check_same_thread=False)

# DB connection
cursor = conn.cursor()
#
# Bot connection
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

cursor.execute(
    'CREATE TABLE IF NOT EXISTS codes(id integer primary key,product_id integer,code varchar)')

cursor.execute(
    'CREATE TABLE IF NOT EXISTS products(id integer primary key,product_id integer,category varchar,product_name varchar,price integer)')

cursor.execute(
    """CREATE TABLE IF NOT EXISTS orders(id integer primary key,product_id int,product_name varchar,price integer,buyer_id integer,username varchar)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS users(id integer primary key,username varchar,user_id integer)
""")
conn.commit()


class Add_procut(StatesGroup):
    name = State()
    category = State()
    product_id = State()
    price = State()
    codes = State()



products = CallbackData("products", "products")
category = CallbackData("cate", "category")
purchasing = CallbackData('product', 'id','quantity')
quantity = CallbackData('quan', 'id','quantity')
check_payments = CallbackData('payment','check','price','product_id','quantity')

async def menu_keyboard():
    markup = ReplyKeyboardMarkup()
    markup.add('Products🧺')
    markup.add('Support🧑‍💼')
    return markup

async def category_keyboard():
    cursor.execute("SELECT DISTINCT CATEGORY FROM PRODUCTS")
    results = cursor.fetchall()
    markup = InlineKeyboardMarkup()
    for i in results:
        markup.add(InlineKeyboardButton(text=i[0], callback_data=category.new(category=i[0])))
    return markup


async def products_keyboard(category):
    cursor.execute("SELECT  * FROM PRODUCTS WHERE CATEGORY=?",(category,))
    results = cursor.fetchall()
    markup = InlineKeyboardMarkup()
    for i in results:
        markup.add(InlineKeyboardButton(text=i[3], callback_data=products.new(products=i[1])))

    return markup


async def yes_or_no(id,quantity):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="Buy", callback_data=purchasing.new(id=id,quantity=quantity)))
    markup.add(InlineKeyboardButton(text="Back", callback_data="back"))
    return markup

async def check_payment(address,price_btc,products_id,quantity):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Check payment',callback_data=check_payments.new(check=address,price=price_btc,product_id = products_id,quantity=quantity)))
    return markup

async def quantity_keyboard(id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text="1", callback_data=purchasing.new(id=id,quantity=1)),InlineKeyboardButton(text="2", callback_data=purchasing.new(id=id,quantity=2)),InlineKeyboardButton(text="3", callback_data=purchasing.new(id=id,quantity=3)))
    markup.add(InlineKeyboardButton(text="4", callback_data=purchasing.new(id=id,quantity=4)),InlineKeyboardButton(text="5", callback_data=purchasing.new(id=id,quantity=5)),InlineKeyboardButton(text="6", callback_data=purchasing.new(id=id,quantity=6)))
    markup.add(InlineKeyboardButton(text="Back", callback_data="back"))
    return markup


@dp.message_handler(lambda message: message.text == "Cancel",state='*')
async def show_catalog(message: types.Message,state:FSMContext):
    await state.reset_state()
    await message.answer("Canceled")
    await message.answer("Welcome to our shop,{}".format(message.from_user.first_name),
                         reply_markup=await menu_keyboard())
@dp.message_handler(lambda message: message.text == "cancel",state='*')
async def show_catalog(message: types.Message,state:FSMContext):
    await state.reset_state()
    await message.answer("Canceled")
    await message.answer("Welcome to our shop,{}".format(message.from_user.first_name),
                         reply_markup=await menu_keyboard())

@dp.message_handler(commands=["start", "menu"], state='*')
async def start(message: types.Message):
    cursor.execute("INSERT INTO users(username,user_id) values (?,?)",
                   (message.from_user.first_name, message.from_user.id,))
    conn.commit()
    print(message)
    await message.answer("""WELCOME TO KIM and MASTER,<b>{}</b>!
Here you will find EVERYTHING you need to succeed‼️

🤝Here you can automatically buy what you need🤫
🤝If you have any problems - our support is online 24/7!
🤝Good Luck‼️""", reply_markup=await menu_keyboard())


@dp.message_handler(commands=["get_report"], state='*')
async def start(message: types.Message):
    excel = generate_excel()
    await message.answer_document(open(excel, 'rb'))


@dp.message_handler(lambda message: message.text == "Support🧑‍💼",state='*')
async def show_catalog(message: types.Message,state:FSMContext):
    await state.reset_state()
    await message.answer("Our support: {}".format('@domahdesiki'))

@dp.callback_query_handler(lambda c: c.data == 'back',state='*')
async def back(callback_query: types.CallbackQuery,state:FSMContext):
    await state.finish()
    await callback_query.message.answer("Welcome to our shop {}", reply_markup=await menu_keyboard())


@dp.message_handler(lambda message: message.text == 'Products🧺')
async def show_catalog(message: types.Message):
    await message.answer('Category', reply_markup=await category_keyboard())

@dp.callback_query_handler(category.filter())
async def show_products(call: types.CallbackQuery, callback_data: dict):
    category = callback_data.get("category")
    if category == 'Custom':
        await call.message.answer("Write your custom card here")
    else:
        await call.message.answer("Cards", reply_markup= await products_keyboard(category))


@dp.callback_query_handler(products.filter())
async def show_product(call: types.CallbackQuery, callback_data: dict):
    cursor.execute("SELECT * FROM products where product_id =?",(callback_data.get('products'),))
    res = cursor.fetchall()
    cursor.execute("Select * from codes where product_id=?",(callback_data.get('products'),))
    quantity = cursor.fetchall()
    print(quantity)
    await call.message.answer("Do you want buy a {} for {}$\n(available {} pcs)".format(res[0][2], res[0][3],len(quantity) ),
                              reply_markup=await quantity_keyboard(res[0][1]))

@dp.callback_query_handler(quantity.filter())
async def check_quantity(call: types.CallbackQuery, callback_data: dict):
    prod_id = callback_data.get('id')
    quantity = callback_data.get('quantity')
    cursor.execute("SELECT * FROM products where product_id=?",(prod_id))
    res = cursor.fetchone()
    await call.message.answer("Do you want buy a {} in {} quantity?".format(res[2],quantity),reply_markup=await yes_or_no(prod_id,quantity))


@dp.callback_query_handler(purchasing.filter())
async def show_products(call: types.CallbackQuery, callback_data: dict):
    product_id = callback_data.get('id')
    quantity = int(callback_data.get('quantity'))
    cursor.execute("SELECT * FROM codes WHERE product_id =?",(product_id,))
    res = cursor.fetchall()
    if res:
        cursor.execute("SELECT price FROM products WHERE product_id =?",product_id,)
        res = cursor.fetchall()
        price_btc = wallet.converter_btc(res[0][0]*quantity)
        wallet_btc = wallet.create_address()
        await call.message.answer('Sir send {} btc to address below'.format(price_btc))
        await call.message.answer(wallet_btc,reply_markup=await check_payment(wallet_btc,price_btc,product_id,quantity))
    else:
        await call.message.answer("Sorry sir this product is not available now",reply_markup=await menu_keyboard())

@dp.callback_query_handler(check_payments.filter())
async def checking_payment(call: types.CallbackQuery, callback_data: dict):
    address = callback_data.get('check')
    price = float(callback_data.get('price'))
    quantity = int(callback_data.get('quantity'))

    product_id = callback_data.get('product_id')
    balance = float(wallet.check_payment_btc(address))
    print(balance)
    if balance>(price*0.85):
    # if balance == 0:
        start = 1
        await call.message.answer("Payment was succesfull")
        while start<=quantity:
            cursor.execute("SELECT * FROM codes WHERE product_id=?",(product_id,))
            code = cursor.fetchone()
            cursor.execute("SELECT product_name,price FROM products WHERE product_id=?",(product_id,))
            product_name = cursor.fetchone()
            cursor.execute("DELETE FROM codes WHERE id=?",(code[0],))
            conn.commit()
            cursor.execute("INSERT INTO orders(product_id,product_name,price,buyer_id,username) VALUES (?,?,?,?,?) ",(product_id,product_name[0],product_name[1],call.from_user.id,call.from_user.first_name,))
            conn.commit()
            await call.message.answer("{}".format(code[2]))
            start+=1
        await bot.delete_message(call.from_user.id, call.message.message_id)
    else:
        await call.answer("Payment not yet received")







#######Admin part


@dp.message_handler(commands=["add_product"], state='*')
async def add_product(message: types.Message):
    await message.answer("Write name of product\n(PlayCard 25$)",reply_markup=ReplyKeyboardRemove())
    await Add_procut.name.set()

@dp.message_handler(state=Add_procut.name, content_types=types.ContentTypes.TEXT)
async def add_product(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Write category of product')
    await Add_procut.category.set()


@dp.message_handler(state=Add_procut.category, content_types=types.ContentTypes.TEXT)
async def add_product(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer('Write id of product ')
    await Add_procut.product_id.set()

@dp.message_handler(state=Add_procut.product_id, content_types=types.ContentTypes.TEXT)
async def add_product_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Write only digits")
        await Add_procut.product_id.set()
    else:
        cursor.execute("SELECT * FROM products WHERE product_id =?",(message.text.title(),))
        res = cursor.fetchall()
        if res:
            await message.answer("This id already exists, write another id")
            await Add_procut.product_id.set()
        else:
            await state.update_data(product_id = message.text)
            await message.answer("Write price of product $")
            await Add_procut.price.set()


@dp.message_handler(state=Add_procut.price, content_types=types.ContentTypes.TEXT)
async def add_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Write only digits")
        await Add_procut.price.set()#nuzhno sdelat chtobi prinimalo neskolko kodov
    else:
        res = await state.get_data()
        cursor.execute('''INSERT INTO products(product_id,product_name,category,price) VALUES (?,?,?,?) ''',(res['product_id'],res['name'],res['category'],message.text.title()))
        conn.commit()
        await message.answer("Write codes",reply_markup=await menu_keyboard())
        await Add_procut.codes.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
