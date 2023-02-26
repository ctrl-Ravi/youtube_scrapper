import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from chromedriver_py import binary_path
service_object = Service(binary_path)
import logging
from flask import Flask, render_template, request,jsonify
from flask import Flask, send_file
import time
from bs4 import BeautifulSoup as bs
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)
# import pymongo

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            driver = webdriver.Chrome(service=service_object)
            driver.maximize_window()
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            # main_link = driver.get(f"https://www.youtube.com/@PW-Foundation/videos")
            main_link = driver.get(f"https://www.youtube.com/@{searchString}/videos")
            time.sleep(4)
            for i in range(900,2000):
                driver.execute_script(f"window.scrollTo(0, {i});")
            main_html= bs(driver.page_source, "html.parser")
            

            video_link=[]
            thumbnail_link=[]
            video_titles=[]
            views=[]
            times =[]
            video_title=main_html.find_all("a",{"class":"yt-simple-endpoint focus-on-expand style-scope ytd-rich-grid-media"})
            video_detail = main_html.find_all("a",{"class":"yt-simple-endpoint inline-block style-scope ytd-thumbnail"})
            views_time = main_html.find_all("div",{"id":"metadata-line"})
            del video_detail[0]
            for i in range(0,10):
                try:
                    link = "https://www.youtube.com/"+ video_detail[i]["href"]
                except Exception as e:
                    logging.info(e)
                try:
                    video_link.append(link)
                    thumbnail = video_detail[i].img["src"]
                    thumbnail_link.append(thumbnail)
                    title = video_title[i].text
                    video_titles.append(title)
                    view = views_time[i].find_all("span")[0].text
                    views.append(view)
                    uplcaded_time = views_time[i].find_all("span")[1].text
                    times.append(uplcaded_time)
                except Exception as e:
                    logging.info(e)

            driver.quit()
            df = pd.DataFrame({"title":video_titles,"Views":views,"Uploaded_time":times,"video_link":video_link,"thumbnail_link":thumbnail_link})
            df.to_csv("video_detail.csv")
            return render_template('result.html')
            
        except Exception as e:
            logging.info(e)
            return "Please Enter valid username of channel"

df = pd.read_csv('video_detail.csv')

@app.route('/download', methods =['GET', 'POST'])
def download_csv():
    return send_file('video_detail.csv', mimetype='text/csv', as_attachment=True)

if __name__=="__main__":
    app.run(host="0.0.0.0")