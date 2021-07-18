from flask import Flask, render_template, request, session,url_for,redirect,current_app,flash
from datetime import timedelta
import re
import os
import secrets
import mysql.connector
#import numpy as np
#import keras.models
import sys
import base64
#from keras.preprocessing import image
#import numpy as np
#import keras.models
#from keras.models import model_from_json
#import tensorflow as tf
#sys.path.append(os.path.abspath("./model_saved"))

app = Flask(__name__)

app.secret_key = 'your secret key'
app.permanent_session_lifetime = timedelta(minutes=5)

def save_images(photo):
    hash_photo=secrets.token_urlsafe(10)
    _, file_extension=os.path.splitext(photo.filename)
    photo_name=hash_photo+file_extension
    file_path=os.path.join(current_app.root_path,'static/images',photo_name)
    photo.save(file_path)
    return photo_name

#####################################################################   pranjal    ##########################################################################################################

def getmodel():
    json_file = open('model_saved.json','r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
	#load weights into new model
    loaded_model.load_weights("model_saved.h5")
    print("Loaded Model from disk")

	#compile and evaluate loaded model
    loaded_model.compile(loss ='binary_crossentropy',optimizer ='rmsprop',metrics =['accuracy'])
	#loss,accuracy = model.evaluate(X_test,y_test)
	#print('loss:', loss)
	#print('accuracy:', accuracy)
	#graph = tf.get_default_graph()
    return loaded_model

def read_image(filename):
    img = keras.preprocessing.image.load_img(filename, target_size=(224,224))
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)
    return img_array

@app.route("/predict",methods=['POST'])
def predict():
    model=getmodel()
    if request.method =='POST':
        file =request.files['photo']
        if file :
            filename=file.filename
            file.save(filename)
            img_array= read_image(filename)
            #prediction
            predictions = model.predict(img_array)
            score = predictions[0]
            if score==0:
                return redirect('/blousedisp')
            else:
                return redirect('/kurtidisp')
    return redirect("/custdash")
#####################################################################   pranjal    ##########################################################################################################



@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
    session.permanent = True
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        #password="",
        database="kaarigarkiduniya"
    )
    mycursor = mydb.cursor(dictionary=True)
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        typo=request.form['typo']
        #print(typo)
        if typo=='seller':
            mycursor.execute("SELECT * FROM loginreg WHERE username = '"+username+"' AND password = '"+password+"'")
            account = mycursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['seller_id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return redirect('/sellerdash')
            else:
                msg = 'Incorrect username / password !'
            return render_template('login.html', msg = msg)
        else:
            mycursor.execute("SELECT * FROM logincust WHERE username = '"+username+"' AND password = '"+password+"'")
            account = mycursor.fetchone()
            if account:
                session['loggedin'] = True
                session['id'] = account['cust_id']
                session['username'] = account['username']
                msg = 'Logged in successfully !'
                return redirect('/custdash')
            else:
                msg = 'Incorrect username / password !'
                return render_template('login.html', msg = msg)
    return render_template('login.html', msg = msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))



@app.route('/register', methods =['GET', 'POST'])
def register():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        #password="",
        database="kaarigarkiduniya"
    )
    msg = ''
    mycursor = mydb.cursor(dictionary=True)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        dob = request.form['dob']
        l_name = request.form['l_name']
        f_name = request.form['f_name']
        phone = request.form['phone']
        city = request.form['city']
        state = request.form['state']
        typo=request.form['typo']

        if typo=='seller':
            mycursor.execute("SELECT * FROM loginreg WHERE username = '"+username+"'")
            account = mycursor.fetchone()
            if account:
                msg = 'Account already exists !'
                return render_template('register.html', msg = msg)
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
                return render_template('register.html', msg = msg)
            elif not username or not password:
                msg = 'Please fill out the form !'
                return render_template('register.html', msg = msg)
            else:
                mycursor.execute("INSERT INTO loginreg (f_name, l_name, username, password, phone, city,state,dob) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(f_name,l_name,username,password,phone,city,state,dob))
                mydb.commit()
                mycursor.close()
                msg = 'You have successfully registered !'
                return redirect('/login')
        else:
            mycursor.execute("SELECT * FROM logincust WHERE username = '"+username+"'")
            account = mycursor.fetchone()
            if account:
                msg = 'Account already exists !'
                return render_template('register.html', msg = msg)
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers !'
                return render_template('register.html', msg = msg)
            elif not username or not password:
                msg = 'Please fill out the form !'
                return render_template('register.html', msg = msg)
            else:
                mycursor.execute("INSERT INTO logincust (f_name, l_name, username, password, phone, city,state,dob) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",(f_name,l_name,username,password,phone,city,state,dob))
                mydb.commit()
                mycursor.close()
                msg = 'You have successfully registered !'
                return redirect('/login')
        
    else:
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

#####login with otp#######
@app.route('/loginwithotp', methods =['GET', 'POST'])
def loginwithotp():
    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        #password="",
        database="kaarigarkiduniya"
    )
    mycursor = mydb.cursor(dictionary=True)
    msg = ''
    if request.method == 'POST' and 'phonenumber' in request.form:
        print("qwerty")
        phonenumber = request.form['phonenumber']
        print(phonenumber)
        mycursor.execute("SELECT * FROM loginreg WHERE phone = '"+phonenumber+"'")
        account = mycursor.fetchone()
        if account:
                session['loggedin'] = True
                session['id'] = account['seller_id']
                session['username'] = account['username']
                #####generate otp#########
                val=getOTPApi(phonenumber)
                if val:
                    return render_template('validateotp.html')
        else:
                msg = 'Incorrect OTP!'
                return redirect('/register')
    return render_template('loginwithotp.html')

def generateOTP():
    return random.randrange(10000,99999)

def getOTPApi(number):
    account_sid='ACfe2fc6b005aeed7848400e0ac97720e3'
    auth_token ='03ba0e19ee646f6e77f30e2b875da552'
    client=Client(account_sid, auth_token)
    otp=generateOTP()
    body= 'Your OTP is'+str(otp)
    session['response']=str(otp)
    #message=client.messages.create(from_= +442033223576,body=body,to=number)
    message = client.messages.create(
         body=body,
         from_='+12013654806',
         to=('+91'+str(number))
     ) 
    if message.sid:
        return True
    else:
        return False

@app.route("/validateotp" , methods =['GET', 'POST'])
def validateotp():
    otp=request.form['otp']
    if 'response' in session:
        s=session['response']
        session.pop('response',None)
        if s ==otp:
            return render_template('sellerdash.html')
        else:
            return render_template('login.html')
    return render_template('validateotp.html')


"""@app.route("/home")
def home():
    if 'loggedin' in session:
        print('heloooo')
        name='rohan'
        return render_template('index.html',name1=name)
    return redirect('/login')"""





######################################################################   Seller DAshboard and stuff   ###########################################################################


@app.route("/sellerdash")
def sellerdash():
    if 'loggedin' in session:
        return render_template('sellerdash.html')
    return redirect('/login')



@app.route("/prevup", methods=['GET'])
def prevup():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        msg = ''
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("SELECT * FROM prev_sold WHERE seller_id = %s",(session['id'],))
        account = mycursor.fetchall()
        #print(account)
        if account:
            msg='got values!'
            data=[]
            for i in account:
                #print("i= ",i)
                mycursor.execute("SELECT * FROM pro_table_seller WHERE product_id = %s",(i['product_id'],))
                dat=mycursor.fetchone()
                data.append(dat)
                #print(img1)             
            return render_template('prevup.html',data=data)
        else:
            msg='NO PRODUCTS UPLOADED YET!'
        return redirect('/sellerdash')
    return redirect('/login')
    



@app.route("/uploadpic")
def uploadpic():
    if 'loggedin' in session:
        return render_template('uploadpic.html')
    return redirect('/login')

@app.route("/upload", methods=['POST'])
def upload():
    if 'loggedin' in session:
        if request.method=='POST':
            name=request.form.get('name')
            description=request.form.get('description')
            cost_price=request.form.get('cost_price')
            shipping=request.form.get('shipping')
            brand=request.form.get('brand')
            category=request.form.get('category')
            size=request.form.get('size')
            colour=request.form.get('colour')
            material=request.form.get('material')
            product_type=request.form.get('product_type')

            photo=save_images(request.files.get('photo'))

            mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                #password="",
                database="kaarigarkiduniya"
            )
            msg = ''
            total_sale='0'
            selling_price=0
            import csv
            f=open('spdata.csv','r')
            reader=csv.reader(f)
            l=[]
            for row in reader:
                l.append(row)
            print(l)
            for i in range(1,11):
                print(l[i][0])
                print(cost_price)
                if((l[i][1])==cost_price):
                    selling_price=(l[i][2])
                    break
            if selling_price==0:
                selling_price=float(cost_price)*(1.3)
            print(selling_price)
            profit=float(selling_price)-float(cost_price)
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("INSERT INTO pro_table_seller (name,description,cost_price,shipping,brand,category,size,colour,material,product_type,total_sale,sell_price,image) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(name,description,cost_price,shipping,brand,category,size,colour,material,product_type,total_sale,selling_price,photo))
            mydb.commit()
            mycursor.execute("SELECT product_id FROM pro_table_seller WHERE name= %s",(name,))
            dat=mycursor.fetchone()
            print(dat)
            mycursor.execute("INSERT INTO prev_sold (seller_id,product_id) VALUES (%s,%s)",(session['id'],dat['product_id']))
            mydb.commit()
            msg = 'You have successfully inserted !'
            return render_template('success.html',name=name,selling_price=selling_price,cost_price=cost_price,profit=profit,photo=photo)
        msg='error occured'
        return render_template('uploadpic.html',msg=msg)
    return redirect('/login')


######################################################################   customer DAshboard and stuff   ###########################################################################
@app.route("/custdash")
def custdash():
    if 'loggedin' in session:
        return render_template('custdash.html')
    return redirect('/login')



@app.route("/checkcart")
def checkcart():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select product_id from cart where cust_id=%s",(session['id'],))
        account = mycursor.fetchall()
        print(account)
        if account:
            dat=[]
            for i in account:
                mycursor.execute("SELECT * FROM pro_table_seller WHERE product_id = %s",(i['product_id'],))
                data=mycursor.fetchone()
                dat.append(data)
                #print(img1)             
            return render_template('cart.html',dat=dat)
        return redirect('/custdash')
    return redirect('/login')


@app.route("/checkwish")
def checkwish():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select product_id from wishlist where cust_id=%s",(session['id'],))
        account = mycursor.fetchall()
        #print(account)
        if account:
            dat=[]
            for i in account:
                mycursor.execute("SELECT * FROM pro_table_seller WHERE product_id = %s",(i['product_id'],))
                data=mycursor.fetchone()
                dat.append(data)
                #print(img1)             
            return render_template('wishlist.html',dat=dat)
        return redirect('/custdash')
    return redirect('/login')


@app.route("/wishlist",methods=['GET','POST'])
def wishlist():
    if 'loggedin' in session:
        if request.method=='POST':
            calling=request.form.get('calling')
            product_id=request.form.get('wishlist')
            mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                #password="",
                database="kaarigarkiduniya"
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("Select * from wishlist where product_id=%s and cust_id=%s",(product_id,session['id']))
            dat=mycursor.fetchall()
            if dat:
                return redirect(calling)
            mycursor.execute("insert into wishlist values (%s,%s)",(session['id'],product_id))
            mydb.commit()
        return redirect(calling)
    return redirect('/login')

@app.route("/cart",methods=['GET','POST'])
def cart():
    if 'loggedin' in session:
        if request.method=='POST':
            calling=request.form.get('calling')
            product_id=request.form.get('cart')
            mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                #password="",
                database="kaarigarkiduniya"
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("insert into cart values (%s,%s)",(session['id'],product_id))
            mydb.commit()
        return redirect(calling)
    return redirect('/login')

@app.route("/markbask",methods=['GET','POST'])
def markbask():
    if 'loggedin' in session:
        if request.method=='POST':
            calling=request.form.get('calling')
            product_id=request.form.get('markbask')
            mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                #password="",
                database="kaarigarkiduniya"
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("select * from pro_table_seller where product_id=%s",(product_id,))
            act=mycursor.fetchone()
            mycursor.execute("select product_type from pro_table_seller where product_id=%s",(product_id,))
            dat=mycursor.fetchone()
            if dat['product_type']=='kurti':
                mycursor.execute("Select product_id,name,cost_price,image from pro_table_seller where product_type='shawl' or product_type='plazzo'")
                data=mycursor.fetchall()
                return render_template('markbask.html',data=data,act=act)
            elif dat['product_type']=='saree':
                mycursor.execute("Select product_id,name,cost_price,image from pro_table_seller where product_type='blouse'")
                data=mycursor.fetchall()
                return render_template('markbask.html',data=data,act=act)
            elif dat['product_type']=='blouse':
                mycursor.execute("Select product_id,name,cost_price,image from pro_table_seller where product_type='saree'")
                data=mycursor.fetchall()
                return render_template('markbask.html',data=data,act=act)
            elif dat['product_type']=='shawl':
                mycursor.execute("Select product_id,name,cost_price,image from pro_table_seller where product_type='kurti'")
                data=mycursor.fetchall()
                return render_template('markbask.html',data=data,act=act)
            else:
                mycursor.execute("Select product_id,name,cost_price,image from pro_table_seller where product_type='kurti'")
                data=mycursor.fetchall()
                return render_template('markbask.html',data=data,act=act)
        return redirect(calling)
    return redirect('/login')



@app.route("/payment",methods=['POST'])
def payment():
    if 'loggedin' in session:
        if request.method=='POST':
            mydb=mysql.connector.connect(
                host="localhost",
                user="root",
                #password="",
                database="kaarigarkiduniya"
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("select product_id from cart where cust_id=%s",(session['id'],))
            data=mycursor.fetchall()
            suma=0
            for i in data:
                mycursor.execute("SELECT sell_price FROM pro_table_seller WHERE product_id = %s",(i['product_id'],))
                data=mycursor.fetchone()
                suma=suma+int(data['sell_price'])
                mycursor.execute("update pro_table_seller set total_sale=total_sale+1 where product_id=%s",(i['product_id'],))
                mydb.commit()
            return render_template('payment.html',suma=suma)
    return redirect('/login')




@app.route("/kurtidisp",methods=['GET'])
def kurtidisp():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        x='kurti'
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select * from pro_table_seller where product_type=%s",(x,))
        dat=mycursor.fetchall()
        #print(dat)
        return render_template('kurtidisp.html',dat=dat)
    return redirect('/login')



@app.route("/shawldisp")
def shawldisp():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        x='shawl'
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select * from pro_table_seller where product_type=%s",(x,))
        dat=mycursor.fetchall()
        #print(dat)
        return render_template('shawldisp.html',dat=dat)
    return redirect('/login')

@app.route("/sareedisp")
def sareedisp():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        x='saree'
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select * from pro_table_seller where product_type=%s",(x,))
        dat=mycursor.fetchall()
        #print(dat)
        return render_template('sareedisp.html',dat=dat)
    return redirect('/login')

@app.route("/plazzodisp")
def plazzodisp():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            #password="",
            database="kaarigarkiduniya"
        )
        x='plazzo'
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select * from pro_table_seller where product_type=%s",(x,))
        dat=mycursor.fetchall()
        #print(dat)
        return render_template('plazzodisp.html',dat=dat)
    return redirect('/login')

@app.route("/blousedisp")
def blousedisp():
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            database="kaarigarkiduniya"
        )
        x='blouse'
        mycursor = mydb.cursor(dictionary=True)
        mycursor.execute("Select * from pro_table_seller where product_type=%s",(x,))
        dat=mycursor.fetchall()
        return render_template('blousedisp.html',dat=dat)
    return redirect('/login')


@app.route("/search",methods =['GET', 'POST'])
def search():
    if 'loggedin' in session:
        if request.method == 'POST':
            kapda=request.form['kapda']
            if kapda=='kurti':
                return redirect('/kurtidisp')
            elif kapda=='saree':
                return redirect('/sareedisp')
            elif kapda=='blouse':
                return redirect('/blousedisp')
            elif kapda=='shawl':
                return redirect('/shawldisp')
            else:
                return redirect('/plazzodisp')
        return redirect('/custdash')
    return redirect('/login')

@app.route("/keyword_search",methods =['GET', 'POST'])
def keyword_search():
    arr=[]
    dat=[]
    if 'loggedin' in session:
        mydb=mysql.connector.connect(
            host="localhost",
            user="root",
            database="kaarigarkiduniya"
        )
        if request.method == 'POST':
            word=request.form['keyword_search']
            #print(word)
            word=word.split()
            print(word)
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("Select product_id,description,name from pro_table_seller")
            dol=mycursor.fetchall()
            #print(dol[0]['name'].split())
            #print(dat[0]['product_id'])
            for i in range(len(dol)):
                for j in word:
                    if j in dol[i]['name'].split() or j in dol[i]['description'].split() or j[0].upper()+j[1:] in dol[i]['name'].split() or j[0].upper()+j[1:] in dol[i]['description'].split() or j[0].lower()+j[1:] in dol[i]['name'].split() or j[0].lower()+j[1:] in dol[i]['description'].split():
                        arr.append(dol[i]['product_id'])
            for i in arr:
                mycursor.execute("Select * from pro_table_seller where product_id = %s",(i,))
                data=mycursor.fetchall()
                dat.append(data)
            return render_template('keyword_result.html',dat=dat,length=len(dat))
        return redirect('/custdash')
    return redirect('/login')    


@app.route("/contact")
def contact():
    if 'loggedin' in session:
        return render_template('contact.html')
    return redirect('/login')


@app.route("/aboutus")
def aboutus():
    if 'loggedin' in session:
        return render_template('aboutus.html')
    return redirect('/login')



if __name__=='__main__':
    app.run(debug=True)
