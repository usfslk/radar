from flask import Flask, render_template, request
import json, indicoio, sqlite3
from newsapi import *

app = Flask(__name__, static_url_path="/static")

indicoio.config.api_key = '43751098d41ba733826cc75dd3173717'
newsapi = NewsApiClient(api_key='b71d9eefeca94a1487e7fc9bf9964af8')

@app.route('/')
def main():	
	conn = sqlite3.connect("homepage.db")
	cursor = conn.cursor()
	keyword= 'Cryptocurrencies'
	cursor.execute(""" 
	CREATE TABLE IF NOT EXISTS main(
		Title TEXT,
		Description TEXT,
		URL TEXT,
		IMGLink TEXT,
		Score INTEGER,
		sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
	); 
	""")

	data = newsapi.get_everything(q=keyword,
	                              language='en',
	                              sources='techcrunch,crypto-coins-news,the-verge',
								  sort_by='publishedAt',
	                              )

	load = data['articles']
	resultslist = []
	scorelist = []
	index = 0
	limit = 20

	for index, post in zip(range(limit), load):
		title = post['title']
		if len(cursor.execute("SELECT Title FROM main WHERE Title = ?", (title,)).fetchall())  > 0:
			pass
		else:
			description = post['description']
			url = post['url']
			imglink = post['urlToImage']
			datetime = post['publishedAt']
			scoredesc = indicoio.sentiment(title) * 1.5
			calc = (scoredesc*100)
			verg = calc / 2
			score = ("%.0f" % verg)
			scorelist.append(float(score))
			nline = title, description, url, imglink, score
			cursor.execute('INSERT INTO main (Title, Description, URL, IMGLink, Score) VALUES (?, ?, ?, ?, ?)', (nline))
			conn.commit()

	for row in cursor.execute("SELECT Title, Description, URL, IMGLink, Score, sqltime FROM main ORDER BY Score DESC, sqltime DESC LIMIT 15"):
		resultslist.append(row)

	return render_template('main.html', resultslist=resultslist, keyword=keyword)


###

@app.route('/analysis', methods=['GET','POST'])
def results():

	keyword = str(request.args.get( "keyword" , None ))
	conn = sqlite3.connect(":memory:")
	cursor = conn.cursor()
	cursor.execute(""" 
	CREATE TABLE IF NOT EXISTS main(
		Keyword TEXT,
		Title TEXT,
		Description TEXT,
		URL TEXT,
		IMGLink TEXT,
		Score INTEGER,
		sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
	); 
	""")

	resultslist = []
	scorelist = []

	pagenum = 1
	num_pages = 3


	for pagenum in range(2, num_pages + 1):
		data = newsapi.get_everything(    q=keyword,
										  sources='crypto-coin-news',
		                                  language='en',
		                                  sort_by='publishedAt',
		                                  page=pagenum,
									 )
		load = data['articles']

		for post in load:
			title = post['title']
			description = post['description']
			url = post['url']
			imglink = post['urlToImage']
			scoredesc = indicoio.sentiment(title)
			calc = (scoredesc*100)
			score = ("%.2f" % calc)
			scorelist.append(float(score))
			nline = keyword, title, description, url, imglink, score
			cursor.execute('INSERT INTO main (Keyword, Title, Description, URL, IMGLink, Score)  VALUES (?, ?, ?, ?, ?, ?)', (nline))
			conn.commit()

	for row in cursor.execute("SELECT Title, Description, URL, IMGLink, Score, sqltime FROM main ORDER BY Score DESC LIMIT 16"):
		resultslist.append(row)

	# for row in cursor.execute("SELECT Score FROM main ORDER BY sqltime DESC LIMIT 20"):
	# 	scorelist.append(row[0]) 
	# sumlist = (sum(scorelist))
	# lenght_list = (len(scorelist))
	# before = (sumlist/lenght_list)
	# average = float("%.0f" % before)

	return render_template('analysis.html', resultslist=resultslist, keyword=keyword)


@app.route('/analytics')
def analytics():
	return render_template('analytics.html')

@app.route('/about')
def about():
	return render_template('about.html')

if __name__ == "__main__":
    app.run(debug=True)
