#참고 블로그
#https://niceman.tistory.com/193?category=1009824
#https://aidenlim.dev/19
import time
import json
import os
import ssl
import urllib.request
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3 as sql
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/home/')
def sample():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    
    cur.execute("select distinct CATEGORY from olist_products")

    rows = cur.fetchall()
    return render_template('home.html', rows = rows)    

@app.route('/products/', methods=['POST'])
def searchProducts():
    data = request.form['categoryName']
    print("########################"+data)
    con = sql.connect("database.db")
    con.row_factory=sql.Row
    cur= con.cursor()
    cur.execute("select product_id from olist_products where category = '" + data + "'")
  
    datas = cur.fetchall()
    print(type(datas))

    #print(jsonify(datas))
    datass = []
    for row in datas:
        datass.append([x for x in row])
    datass= np.squeeze(datass,axis=1).tolist()

    con.close()
    # return json.dumps(datass)
    #return redirect(datas)
    return jsonify(datass)
    #return jsonify({'datas' : datas})   
    #return render_template('home.html', datas=datas)


@app.route('/addrec/', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        #입력값을 받는다.
        customer_lat = request.form['lat']
        customer_lng = request.form['lng']
        seller_lat = request.form['lat_seller']
        seller_lng  = request.form['lng_seller']
        product_size_x = request.form['product_size_x']
        product_size_y = request.form['product_size_y']
        product_size_z = request.form['product_size_z']
        product_g = request.form['product_g']
        #걸리는 시간을 구글에 검색
        origin          = customer_lat+","+customer_lng
        destination     = seller_lat+","+seller_lng
        mode            = "driving"
        departure_time  = "now"
        key='키값'

        url = "https://maps.googleapis.com/maps/api/directions/json?origin="+ origin \
            + "&destination=" + destination \
            + "&mode=" + mode \
            + "&departure_time=" + departure_time\
            + "&language=ko" \
            + "&key=" + key
        print(url)
        
        request1         = urllib.request.Request(url)
        context         = ssl._create_unverified_context()
        response        = urllib.request.urlopen(request1, context=context)
        responseText    = response.read().decode('utf-8')
        responseJson    = json.loads(responseText)

        with open("./Agent_Transit_Directions.json","w") as rltStream :
            json.dump(responseJson,rltStream)
        #검색 받은 값을 정리
        wholeDict = None
        with open("./Agent_Transit_Directions.json","r") as transitJson :
            wholeDict = dict(json.load(transitJson))
        print(wholeDict)
        path            = wholeDict["routes"][0]["legs"][0]
        duration_sec    = path["distance"]["text"]

        #----------------------------------------------
        result=customer_lat+" "+customer_lng+" "+seller_lat+" "+seller_lng+", 거리:"+duration_sec
        print(result)
        return render_template('result.html', msg=result)

if __name__ == '__main__':
    app.run(debug=True)