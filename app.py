from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import pymongo
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

def review_insert(url,pages,collection,reviews_list,product_details,Product_Version):
    for i in range(1, 11):
        reviews_links = url + '&page=' + str(i)
        reviews_linkurl = requests.get(reviews_links)
        reviews_linkurl.encoding = 'utf-8'
        reviews_select = bs(reviews_linkurl.text, "html.parser")
        commentboxes = reviews_select.find_all('div', {'class': "_1AtVbE col-12-12"})  # _16PBlm
        j=len(commentboxes)
        print(i)
        for commentbox in commentboxes[4:j-1]:
            try:
                # name.encode(encoding='utf-8')
                name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

            except:
                name = 'No Name'

            try:
                # rating.encode(encoding='utf-8')
                rating = commentbox.div.div.div.div.text


            except:
                rating = 'No Rating'

            try:
                # commentHead.encode(encoding='utf-8')
                commentHead = commentbox.div.div.div.p.text

            except:
                commentHead = 'No Comment Heading'
            try:
                comtag = commentbox.div.div.find_all('div', {'class': ''})
                # custComment.encode(encoding='utf-8')
                custComment = comtag[0].div.text
            except Exception as e:
                comtag = ''
                custComment = ''
                print("Exception while creating dictionary: ", e)

            mydict = {"Name": name, "Rating": rating, "CommentHead": commentHead,
                      "Comment": custComment, "Product_id": product_details, "Product": Product_Version}
            reviews_list.append(mydict)
        collection.insert_one(mydict)


@app.route('/reviews/<search>/<product_details>/',methods=['GET'])
@cross_origin()
def reviews(search,product_details):
    connectstring = pymongo.MongoClient(
        'mongodb+srv://Ram:Qwerty123@clusterlearning.shxr2.mongodb.net/TrainingDB?retryWrites=true&w=majority')
    DB = connectstring['TrainingDB']
    collection_naamamu=search+'Reviews'

    collection1= DB[search]
    reviews_link = collection1.find_one({'_id':ObjectId(product_details)},{'reviews_url','total_pages_count','Product_Version'})
    try:
        url=reviews_link['reviews_url']
        pages=reviews_link['total_pages_count']
        Product_Version=reviews_link['Product_Version']
    except:
        url=''
        pages=''
        return render_template('results.html',reviews_section=False)
    reviews_list = []
    if collection_naamamu not in DB.list_collection_names():
        collection = DB[collection_naamamu]

        review_insert(url,pages,collection,reviews_list,product_details,Product_Version)

    else:
        collection = DB[collection_naamamu]
        if collection.find({'product': product_details}).count()>0:
            for i in collection.find({"Product_id":product_details}):
                reviews_list.append(i)
        else:
            review_insert(url,pages,collection,reviews_list,product_details,Product_Version)

    return render_template('results.html',reviews=reviews_list)


@app.route('/product',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            connectstring= pymongo.MongoClient('mongodb+srv://Ram:Qwerty123@clusterlearning.shxr2.mongodb.net/TrainingDB?retryWrites=true&w=majority')
            DB=connectstring['TrainingDB']

            products_list = []
            if searchString not in DB.list_collection_names():
                flipkart_url = "https://www.flipkart.com/search?q=" + searchString
                uClient = urlopen(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage, "html.parser")
                #try:
                bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
                if len(bigboxes)<4:
                    return render_template("res.html",products_catalog=False)
                #except:
                #   return render_template("res.html", products_catalog=False)
                del bigboxes[0:3]
                j = len(bigboxes)
                if j>6:
                    j=6
                for i in range(0,j):
                    box = bigboxes[i]
                    try:
                        productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                    except:
                        continue
                    prodRes = requests.get(productLink)
                    prodRes.encoding='utf-8'
                    prod_html = bs(prodRes.text, "html.parser")
                    #print(prod_html)
                    try:
                        product_version = prod_html.find_all('span', {'class': 'B_NuCI'})[0].text
                    except:
                        product_version = 'Unable to fetch product details'
                    try:
                        Price = prod_html.find_all('div',{'class':'_30jeq3 _16Jk6d'})[0].text
                    except:
                        Price = 'NA'
                    try:
                        Offers=prod_html.find_all('div',{'class':'WT_FyS'})[0].text
                    except:
                        Offers='NA'
                    try:
                        Highlights=prod_html.find_all('div',{'class':'_2418kt'})[0].text
                    except:
                        Highlights='NA'
                    try:
                        Description=prod_html.find_all('div',{'class':'_2o-xpa'})[0].text
                    except:
                        Description='NA'
                    try:
                        total_prod_descriptions = len(prod_html.find_all('div',{'class':'_3qWObK'}))
                        for i in range(total_prod_descriptions):
                            Product_Description =Product_Description+' '+prod_html.find_all('div',{'class':'_3qWObK'})[i].text# #'Impressive Performance'
                    except:
                        Product_Description=''
                    review_link = prod_html.find_all('div',{'class':'col JOpGWq'})
                    revs2=review_link[0].contents[5]['href']
                    reviews_link='https://www.flipkart.com'+revs2

                    print(reviews_link)
                    reviews_url=requests.get(reviews_link)
                    reviews_url.encoding='utf-8'
                    reviews_read=bs(reviews_url.text,"html.parser")
                    get_total_pages=reviews_read.find('div',{'class':'_2MImiq _1Qnn1K'})
                    get_total_count=get_total_pages.find('span').text
                    total_count=int(get_total_count.split('of ')[1].replace(',',''))
                    if total_count>50:
                        total_count=50

                    product_details={'Product_Version':product_version,'Offers':Offers,'Highlights':Highlights,
                                     'Description':Description,'Product_Description':Product_Description,'reviews_url':reviews_link,
                                     'total_pages_count':total_count,'search_string':searchString}
                    collection = DB[searchString]
                    collection.insert_one(product_details)
            else:
                collection = DB[searchString]
            products=collection.find({'search_string':searchString})
            print(products.count())
            for i in products:
                products_list.append(i)
            #return render_template('results.html', reviews=reviews[0:(len(reviews)-1)],product=product_details) ,data=product['Product_Version']
            return render_template('res.html', product=products_list)
        except Exception as e:
            print('The Exception message is: ',e)
            return str("Some exception while processing the request, please contact admin or app team")
    # return render_template('results.html')

    else:
        return render_template('index.html')

if __name__ == "__main__":
    #app.run(host='127.0.0.1', port=8001, debug=True)
	app.run(debug=True)
