from flask import Flask, render_template, url_for, request,session,redirect,flash
import os
from models import *

app = Flask(__name__)

app.secret_key=os.urandom(24)

def get_current_user():
    store_code =session.get('store_code')
    password = session.get('password')
    print(f"store_code: {store_code}, password: {password}")

    this_user = (store_code,password)

    if this_user[0]==0:
        return Admin(store_code = this_user[0],password=this_user[1])

    else:
        return Store(store_code = this_user[0],password=this_user[1])




@app.route('/',methods=['GET','POST'])

def login():

    if request.method=='POST':

        store_code = int(request.form.get("store_code"))
        password = request.form.get("password")

        session['store_code'] = store_code
        session['password'] = password
        

        login_credentials = (store_code,password)

        stores = Admin(0,"warehouse1").view_stores()
        store_name=User(0,"warehouse1").get_store_name(session['store_code'])
        

        if store_name:

            session['store_name'] = store_name[0]
            verified = False

            for i in range(0,len(stores)):
        
                store=(stores[i][1],stores[i][3])
                
                if login_credentials==store:

                    verified=True
                    break
                
            if verified and store_code==0:

                return redirect(url_for('home'))
            
            elif verified:
                return redirect(url_for('store_home'))
            
            else:
                
                flash("Invalid login details. Please try again or Contact Admin.")
                            
        else:
            flash("Invalid login details. Please try again or Contact Admin.")




    return render_template(template_name_or_list='login.html')


@app.route('/home',methods=['GET','POST'])

def home():

    if get_current_user().store_code==None:   #redirected to login page if not user
        
        return redirect(url_for('login'))
    
    transfers = get_current_user().view_all_authcodes()

    if request.method=="POST":
        action = request.form.get("action")

        if action=="search_auth_code":
                
            from_store = request.form.get("from_store")
            to_store = request.form.get("to_store")
            auth_code = request.form.get("auth_code")
            date_issued = request.form.get("date_issued")

            from_store=from_store if from_store else None
            to_store=to_store if to_store else None
            auth_code=auth_code if auth_code else None
            date_issued=date_issued if date_issued else None

            transfers = get_current_user().search_auth_code(from_store, to_store, date_issued, auth_code)

            
            return render_template(template_name_or_list='home.html',transfers=transfers)
        
        elif action=="generate_auth_code":

            code_letters = request.form.get("code_letters")
            max_count = int(request.form.get("max_count"))
            result = get_current_user().generate_new_authcodes(code_letters,max_count)

            if result["status"] == "error":
                flash(result["message"], "error")

            elif result["status"] == "success":
                flash(result["message"], "success")
                return redirect(url_for('home'))


    return render_template(template_name_or_list='home.html',transfers=transfers)


@app.route('/products',methods=['GET','POST'])

def products():
    if get_current_user().store_code==None:   #redirected to login page if not user
        
        return redirect(url_for('login'))
    
    products = get_current_user().view_products()

    if request.method=="POST":
        file = request.files.get("products_csv")
        get_current_user().add_products(file)

        return redirect(url_for('products'))

    return render_template(template_name_or_list='products.html',products=products)


@app.route("/stores",methods =['GET','POST'])

def stores():
    if get_current_user().store_code==None:   #redirected to login page if not user
        
        return redirect(url_for('login'))
    
    stores = get_current_user().view_stores()

    if request.method=='POST':

        new_store_code = request.form.get('new_store_code')
        new_store_name = request.form.get('new_store_name')
        new_store_password = request.form.get('new_store_password')

        get_current_user().add_stores(new_store_code,new_store_name,new_store_password) 
        return redirect(url_for('stores'))

    return render_template(template_name_or_list='stores.html', stores=stores)



@app.route('/store_home',methods=['GET','POST'])

def store_home():
    if get_current_user().store_code==None:   #redirected to login page if not user
        
        return redirect(url_for('login'))
    
    transfers = get_current_user().view_my_codes()

    return render_template(template_name_or_list='store_home.html',transfers=transfers)


@app.route('/auth_code',methods=['GET','POST'])
def auth_code():

    if get_current_user().store_code==None:   #redirected to login page if not user
        
        return redirect(url_for('login'))
    
    if 'to_store' not in session:
        session['to_store'] = None

    if 'cart' not in session:
        session['cart'] = []

    cart = session['cart'] 
    to_store = session['to_store']
    
    if request.method=="POST":
        action = request.form.get('action')
        

        if action =='add_to_cart':

            if not to_store:
                to_store = request.form.get('to_store')
                session['to_store'] = to_store
                to_store_name =User(0,"admin").get_store_name(int(session['to_store']))
                session['to_store_name']=to_store_name[0]
        
            pdt_code = request.form.get('pdt_code').upper()

            pdt_name =get_current_user().search_pdt(pdt_code)

            if pdt_name is None:
                pdt_name = "?"

            size_fit = request.form.get('size_fit')
            qty = request.form.get('qty')

            cart.append([pdt_code,pdt_name[0],size_fit,qty])

            session['cart'] = cart

        if action=="clear_transfer_list":
            session['cart'] = []
            session['to_store'] = None
            return redirect(url_for("auth_code"))
        
        if action =='get_auth_code':

            if to_store:

                all_items = []
                for i in range(0,len(cart)):
    
                    pdt_code_item = cart[i][0]
                    size_fit_item = cart[i][2]
                    qty_item=cart[i][3]
                    item = get_current_user().item_to_transfer(pdt_code_item,size_fit_item,qty_item)
                    all_items.append(item)




                auth_code = get_current_user().get_auth_code(to_store, all_items)
                flash(f"Your Auth Code for Transaction with {session['to_store_name'][0]} is {auth_code[0][0]}")
                session['cart'] = []
                session['to_store'] = None

            else:
                flash("Please select a store before generating an auth code.")


    return render_template(template_name_or_list='auth_code.html', cart =cart, to_store=to_store)




################################################## Run App #########################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0',port = 5555,debug = True)