from flask import Flask, render_template,url_for,request,session,redirect, make_response,jsonify
from nsetools import Nse
import os
import time
import multiprocessing 
from joblib import Parallel, delayed
from flask import Response
import json
import urllib
import pymongo,re
from datetime import datetime
from bson import json_util
client = pymongo.MongoClient("127.0.0.1",27017)
db = client.stocks

nse=Nse()
app=Flask(__name__)
app.config['SECRET_KEY']=b'N\x83Y\x99\x04\xc9\xcfI\xb7\xfc\xce\xd1\xcf\x01\xa8\xccr\xbb&\x1b\x11\xac\xc7V'
app.config['MAX_CONTENT_PATH']=1024
values_list=['open','dayHigh','dayLow','previousClose','lastPrice','change','pChange','quantityTraded','totalTradedValue','high52','low52']
company_list=['ADANIPORTS','BPCL','COALINDIA','NTPC','SUNPHARMA','HINDALCO','RELIANCE','TATASTEEL','GAIL','NESTLEIND','SBILIFE','GRASIM','TCS','DIVISLAB','IOC','WIPRO','TATAMOTORS','ITC','TECHM','HDFCLIFE','SBIN','ONGC','UPL','HCLTECH','M&M','JSWSTEEL','POWERGRID','SHREECEM','LT','HDFCBANK','ULTRACEMCO','AXISBANK','INDUSINDBK','HDFC','ASIANPAINT','CIPLA','TITAN','DRREDDY','BAJAJFINSV','INFY','BAJAJ-AUTO','BRITANNIA','ICICIBANK','KOTAKBANK','HINDUNILVR','BAJFINANCE','EICHERMOT','MARUTI','HEROMOTOCO','BHARATIARTL']

def get_clean_quote(c_name):
    result=nse.get_quote(i)
    temp={}
    for itera in values_list:
        temp[itera]=result[itera]
    return temp

@app.route('/index',methods=['GET'])
def index():
    return Response(json_util.dumps("Api Is Working"),mimetype='application/json')

#"peace"

@app.route('/api/GetTopGainers',methods=['GET'])
def GetTopGainers():
    nse=Nse()
    values_list=['open','dayHigh','dayLow','previousClose','lastPrice','change','pChange','quantityTraded','totalTradedValue','high52','low52']
    a=['ADANIPORTS','BPCL','COALINDIA','NTPC','SUNPHARMA','HINDALCO','RELIANCE','TATASTEEL','GAIL','NESTLEIND','SBILIFE','GRASIM','TCS','DIVISLAB','IOC','WIPRO','TATAMOTORS','ITC','TECHM','HDFCLIFE','SBIN','ONGC','UPL','HCLTECH','M&M','JSWSTEEL','POWERGRID','SHREECEM','LT','HDFCBANK','ULTRACEMCO','AXISBANK','INDUSINDBK','HDFC','ASIANPAINT','CIPLA','TITAN','DRREDDY','BAJAJFINSV','INFY','BAJAJ-AUTO','BRITANNIA','ICICIBANK','KOTAKBANK','HINDUNILVR','BAJFINANCE','EICHERMOT','MARUTI','HEROMOTOCO','BHARTIARTL']
    print(len(a))
    company_data=[]
    start=time.time()
    for i in a:
        tempstart=time.time()
        result=nse.get_quote(i)
        temp={}
        for itera in values_list:
            temp[itera]=result[itera]
        end=time.time()
        print(end-start,end-tempstart,i,)
        data={}
        data[i]=temp
        company_data.append(data)
    return Response(json.dumps(company_data[2]),mimetype='application/json')

@app.route('/api/GetCompanyData',methods=['GET'])
def GetCompanyData():
    company_name=request.args.get("name")
    print(company_name)
    data=list(db.CompanyData.find({"symbol":company_name}))
    return Response(json_util.dumps(data),mimetype='application/json')
@app.route('/Chart')
def Chart():
    return render_template('index.html')

@app.route('/api/ValidateUser',methods=['GET','POST'])
def ValidateUser():
    try:
        if (request.method == "POST" )& (request.is_json):
            post_data=request.get_json()
            if((post_data["email"]=="" and post_data["phone"]=="" )or post_data["pass"]=="" ):
                responsedata={}
                responsedata["message"]="Please Enter All Details With Email or Phone Number"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(list(db.Users.find({"email":post_data["email"]}))[0]['pass']==post_data['pass']):
                responsedata={}
                responsedata["message"]="Validation sucessfull"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(list(db.Users.find({"phone":post_data["phone"]}))[0]['pass']==post_data['pass']):
                responsedata={}
                responsedata["message"]="Validation sucessfull"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            else:
                responsedata={}
                responsedata["message"]="Validation unsucessfull"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
        else:
            responsedata={}
            responsedata["message"]="Use Proper method"
            responsedata["received_data"]=post_data
            return Response(json_util.dumps(responsedata),mimetype='application/json')
    except Exception as e:
        responsedata={}
        responsedata["message"]=str(type(e))+"errormsg:"+str(e)
        responsedata["received_data"]=post_data
        return Response(json_util.dumps(responsedata),mimetype='application/json')    
@app.route('/api/AddUser',methods=['GET','POST'])
def AddUser():
    try:
        if (request.method == "POST" )& (request.is_json):
            post_data=request.get_json()
            if(post_data["name"]=="" or (post_data["email"]=="" and post_data["phone"]=="" )or post_data["pass"]=="" ):
                responsedata={}
                responsedata["message"]="Please Enter All Details With Email or Phone Number"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(re.findall('[^A-Za-z ]',post_data['name'])):
                responsedata={}
                responsedata["message"]="Name Cannot have Numbers or special characters or space"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(not(re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$',post_data['email']))):
                responsedata={}
                responsedata["message"]="Email is not in proper Format"
                responsedata["received_data"]=post_data
                print(db.Users.find({"email":post_data['email']})["email"])
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(len(post_data["phone"]) != 10 or not(post_data["phone"].isnumeric())):
                responsedata={}
                responsedata["message"]="Phone number must be 10 digits"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(len(list(db.Users.find({"email":post_data['email']})))>0):
                    responsedata={}
                    responsedata["message"]="Email alredy exists"
                    responsedata["received_data"]=post_data
                    return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(len(list(db.Users.find({"phone":post_data['phone']})))>0):
                    responsedata={}
                    responsedata["message"]="Phone alredy exists"
                    responsedata["received_data"]=post_data
                    return Response(json_util.dumps(responsedata),mimetype='application/json')        
            userobj={}
            userobj["name"]=post_data["name"]
            userobj["email"]=post_data["email"]
            userobj["phone"]=post_data["phone"]
            userobj["pass"]=post_data["pass"]
            userobj["balance"]=post_data["balance"]
            userobj["holdings"]={}
            db.Users.insert_one(userobj)
            userobj['message']="Sucessfully Registered"
        return Response(json_util.dumps(userobj),mimetype='application/json')
    except KeyError as e:
        responsedata={}
        responsedata["message"]="Key not provided:"+str(e)
        responsedata["received_data"]=post_data
        return Response(json_util.dumps(responsedata),mimetype='application/json')
    except Exception as e:
        responsedata={}
        responsedata["message"]=str(type(e))+"errormsg:"+str(e)
        responsedata["received_data"]=post_data
        return Response(json_util.dumps(responsedata),mimetype='application/json')
@app.route('/api/AddTransaction',methods=['GET','POST'])
def AddTransaction():
    try:
        if (request.method == "POST" )& (request.is_json):
            post_data=request.get_json()
            if(post_data["buysell"]=="" or (post_data["email"]=="" and post_data["phone"]=="" )or post_data["quantity"]=="" ):
                responsedata={}
                responsedata["message"]="Please Enter All Details With Email or Phone Number"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(post_data["buysell"]!='buy' and post_data["buysell"]!="sell"):
                responsedata={}
                responsedata["message"]="Please select buy or sell"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(int(post_data["quantity"])<0):
                responsedata={}
                responsedata["message"]="Quantity must be greater than zero"
                responsedata["received_data"]=post_data
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(post_data['email']!=''):
                if(post_data['buysell']=='buy'):
                    if(int(list(db.Users.find({"email":post_data["email"]}))[0]['balance'])>=(int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])):
                        newbalance=(int(list(db.Users.find({"email":post_data["email"]}))[0]['balance'])-int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                        symbol='-'
                        if(post_data['symbol'] not in list(db.Users.find({'email':post_data['email']}))[0]['holdings'].keys()):    
                            db.Users.update_one({'email':post_data['email']},{'$set':{'holdings.'+post_data['symbol']:post_data['quantity']}})
                        else:
                            db.Users.update_one({'email':post_data['email']},{'$set':{'holdings.'+post_data['symbol']:int(list(db.Users.find({'email':post_data['email']}))[0]['holdings'][post_data['symbol']])+int(post_data['quantity'])}})
                    else:
                        responsedata={}
                        responsedata["message"]="Not enough Funds add funds to contine XD(watch ads)"
                        responsedata["received_data"]=post_data
                        return Response(json_util.dumps(responsedata),mimetype='application/json')
                else:
                    if(post_data['symbol'] in list(db.Users.find({'email':post_data['email']}))[0]['holdings'].keys()):
                        if(int(list(db.Users.find({'email':post_data['email']}))[0]['holdings'][post_data['symbol']])>=post_data['quantity']):
                            newbalance=(int(list(db.Users.find({"email":post_data["email"]}))[0]['balance'])+int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                            symbol='+'
                            db.Users.update_one({'email':post_data['email']},{'$set':{'holdings.'+post_data['symbol']:int(list(db.Users.find({'email':post_data['email']}))[0]['holdings'][post_data['symbol']])-int(post_data['quantity'])}})
                        else:
                            responsedata={}
                            responsedata["message"]="You own only "+str(list(db.Users.find({'email':post_data['email']}))[0]['holdings'][post_data['symbol']])+ " Shares."
                            responsedata["received_data"]=post_data
                            return Response(json_util.dumps(responsedata),mimetype='application/json')
                    else:
                        responsedata={}
                        responsedata["message"]="You Dont own Shares of that company try buying it"
                        responsedata["received_data"]=post_data
                        return Response(json_util.dumps(responsedata),mimetype='application/json')
                db.Users.update_one({'email':post_data['email']},{'$set':{'balance':newbalance}})
                transactiondata={}
                transactiondata['email']=post_data['email']
                transactiondata['phone']=(list(db.Users.find({"email":post_data["email"]}))[0]['phone'])
                transactiondata['symbol']=post_data['symbol']
                transactiondata['timestamp']=str(datetime.datetime.now())
                transactiondata['quantity']=post_data['quantity']
                transactiondata['buysell']=post_data['buysell']
                transactiondata['cost']=symbol+str(int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                db.Transactions.insert_one(transactiondata)
                responsedata={}
                responsedata["message"]="Transaction sucessfull"
                responsedata["transactiondetails"]=transactiondata
                return Response(json_util.dumps(responsedata),mimetype='application/json')
            elif(post_data['phone']!=''):
                if(post_data['buysell']=='buy'):
                    if(int(list(db.Users.find({"phone":post_data["phone"]}))[0]['balance'])>=(int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])):
                        newbalance=(int(list(db.Users.find({"phone":post_data["phone"]}))[0]['balance'])-int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                        symbol='-'
                        if(post_data['symbol'] not in list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'].keys()):    
                            db.Users.update_one({'phone':post_data['phone']},{'$set':{'holdings.'+post_data['symbol']:post_data['quantity']}})
                        else:
                            db.Users.update_one({'phone':post_data['phone']},{'$set':{'holdings.'+post_data['symbol']:int(list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'][post_data['symbol']])+int(post_data['quantity'])}})
                    else:
                        responsedata={}
                        responsedata["message"]="Not enough Funds add funds to contine XD(watch ads)"
                        responsedata["received_data"]=post_data
                        return Response(json_util.dumps(responsedata),mimetype='application/json')
                else:
                    if(post_data['symbol'] in list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'].keys()):
                        if(int(list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'][post_data['symbol']])>=post_data['quantity']):
                            newbalance=(int(list(db.Users.find({"phone":post_data["phone"]}))[0]['balance'])+int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                            symbol='+'
                            db.Users.update_one({'phone':post_data['phone']},{'$set':{'holdings.'+post_data['symbol']:int(list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'][post_data['symbol']])-int(post_data['quantity'])}})
                        else:
                            responsedata={}
                            responsedata["message"]="You own only "+str(list(db.Users.find({'phone':post_data['phone']}))[0]['holdings'][post_data['symbol']])+ " Shares."
                            responsedata["received_data"]=post_data
                            return Response(json_util.dumps(responsedata),mimetype='application/json')
                    else:
                        responsedata={}
                        responsedata["message"]="You Dont own Shares of that company try buying it"
                        responsedata["received_data"]=post_data
                        return Response(json_util.dumps(responsedata),mimetype='application/json')
                db.Users.update_one({'phone':post_data['phone']},{'$set':{'balance':newbalance}})
                transactiondata={}
                transactiondata['email']=(list(db.Users.find({"phone":post_data["phone"]}))[0]['email'])
                transactiondata['phone']=post_data['phone']
                transactiondata['symbol']=post_data['symbol']
                transactiondata['timestamp']=str(datetime.datetime.now())
                transactiondata['quantity']=post_data['quantity']
                transactiondata['buysell']=post_data['buysell']
                transactiondata['cost']=symbol+str(int(list(db.CompanyData.find({'symbol':post_data['symbol']}))[0]['lastPrice'][-1])*post_data["quantity"])
                db.Transactions.insert_one(transactiondata)
                responsedata={}
                responsedata["message"]="Transaction sucessfull"
                responsedata["transactiondetails"]=transactiondata
                return Response(json_util.dumps(responsedata),mimetype='application/json')
                    
    except KeyError as e:
        responsedata={}
        responsedata["message"]="Key not provided:"+str(e)
        responsedata["received_data"]=post_data
        return Response(json_util.dumps(responsedata),mimetype='application/json')
    except Exception as e:
        responsedata={}
        responsedata["message"]=str(type(e))+"errormsg:"+str(e)
        responsedata["received_data"]=post_data
        return Response(json_util.dumps(responsedata),mimetype='application/json')
@app.route('/api/GetDataForChart',methods=['GET','POST'])
def GetDataForChart():
    company_name=request.args.get("name")
    print(company_name)
    data=list(db.CompanyData.find({"symbol":company_name}))
    resultdata=[]
    a=[]
    for i in range(len(data[0]['lastPrice'])):
        b={}
        date_time_str = (data[0]['timestamp'][i])[:19]
        date_time_obj = datetime.strptime(date_time_str,'%Y-%m-%d %H:%M:%S')
        b['time']=int(datetime.timestamp(date_time_obj))+194198-1560
        b['value']=data[0]['lastPrice'][i]
        a.append(b)
    b={}
    b['time']=1606511909
    b['value']=1000
    #a.append(b)
    return Response(json_util.dumps(a),mimetype='application/json')
@app.route('/Xygraph',methods=['GET','POST'])
def GetChart():
    return render_template('index.html')
if __name__=='__main__':
    values_list=['open','dayHigh','dayLow','previousClose','lastPrice','change','pChange','quantityTraded','totalTradedValue','high52','low52']
    company_list=['ADANIPORTS','BPCL','COALINDIA','NTPC','SUNPHARMA','HINDALCO','RELIANCE','TATASTEEL','GAIL','NESTLEIND','SBILIFE','GRASIM','TCS','DIVISLAB','IOC','WIPRO','TATAMOTORS','ITC','TECHM','HDFCLIFE','SBIN','ONGC','UPL','HCLTECH','M&M','JSWSTEEL','POWERGRID','SHREECEM','LT','HDFCBANK','ULTRACEMCO','AXISBANK','INDUSINDBK','HDFC','ASIANPAINT','CIPLA','TITAN','DRREDDY','BAJAJFINSV','INFY','BAJAJ-AUTO','BRITANNIA','ICICIBANK','KOTAKBANK','HINDUNILVR','BAJFINANCE','EICHERMOT','MARUTI','HEROMOTOCO','BHARATIARTL']
    def get_clean_quote(c_name):
        result=nse.get_quote(c_name)
        temp={}
        print(result)
        for itera in values_list:
            temp[itera]=result[itera]
        return temp
    app.run(debug=True)
