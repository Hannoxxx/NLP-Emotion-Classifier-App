# Load Database Pkg
import sqlite3
conn = sqlite3.connect('data.db', check_same_thread=False)
c = conn.cursor()


# Track Input & Prediction
def create_emotionclf_table():
	c.execute('CREATE TABLE IF NOT EXISTS emotionclfTable(customer TEXT,rawtext TEXT,prediction TEXT,probability NUMBER,timeOfvisit TIMESTAMP)')

def add_prediction_details(customer,rawtext,prediction,probability,timeOfvisit):
	c.execute('INSERT INTO emotionclfTable(customer,rawtext,prediction,probability,timeOfvisit) VALUES(?,?,?,?,?)',(customer,rawtext,prediction,probability,timeOfvisit))
	conn.commit()

def view_all_prediction_details():
	c.execute('SELECT * FROM emotionclfTable')
	data = c.fetchall()
	return data
