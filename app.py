# Core Pkgs
import streamlit as st 
import altair as alt
import plotly.express as px 

# EDA Pkgs
import pandas as pd 
import numpy as np 
from datetime import datetime

# Utils
import joblib 
pipe_lr = joblib.load(open("/Users/hanno/end2end-nlp-project-main/models/emotion_classifier_pipe_lr_03_june_2021.pkl","rb"))


# Track Utils
from track_utils import add_prediction_details,view_all_prediction_details,create_emotionclf_table

# Fxn
def predict_emotions(docx):
	results = pipe_lr.predict([docx])
	return results[0]

def get_prediction_proba(docx):
	results = pipe_lr.predict_proba([docx])
	return results

emotions_emoji_dict = {"anger":"😠","disgust":"🤮", "fear":"😨😱", "happy":"🤗", "joy":"😂", "neutral":"😐", "sad":"😔", "sadness":"😔", "shame":"😳", "surprise":"😮"}

# Mail processing
import imaplib
import email
from multiprocessing.spawn import spawn_main

imap_server = "enter imap server of mailprovider"
email_adress = "enter mail adress"
password = "enter password for mailaccount"
POSTEINGANG = "TEST"

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_adress, password)

imap.select(POSTEINGANG)

# Find all emails in inbox https://www.devdungeon.com/content/read-and-send-email-python
_, message_numbers_raw = imap.search(None, 'ALL')
for message_number in message_numbers_raw[0].split():
    print(message_number)
    _, msg = imap.fetch(message_number, '(RFC822)')
    # Parse the raw email message in to a convenient object
    message = email.message_from_bytes(msg[0][1])
    #print('== Email message =====')
    # print(message)  # print FULL message
    #print('== Email details =====')
    customer = (f'From: {message["from"]}')
    print(customer)
    #print(f'Multipart?: {message.is_multipart()}')
    if message.is_multipart():
        print('Multipart types:')
        for part in message.walk():
            print(f'- {part.get_content_type()}')
        multipart_payload = message.get_payload()
        for sub_message in multipart_payload:
            # The actual text/HTML email contents, or attachment data
            print(f'{sub_message.get_payload()}')
    else:  # Not a multipart message, payload is simple string
        mail_input = (f'{message.get_payload()}')
        print(mail_input)
    # You could also use `message.iter_attachments()` to get attachments only
    if message_number == b'1':
        imap.store(message_number, '+FLAGS', '\Deleted')
        imap.expunge()
        print('eine Mail vorhanden und verarbeitet')
    else:
        print('waiting for mail')


# Main Application
def main():
	st.title("Emotion Classifier App")
	menu = ["Home","Monitor"]
	choice = st.sidebar.selectbox("Menu",menu)
	create_emotionclf_table()
	if choice == "Home":
		st.subheader("Home-Emotion In Text")

		with st.form(key='emotion_clf_form'):
			if message_number == b'1':
				raw_text = mail_input
			else:
				raw_text = 'waiting'
			#raw_text = st.text_area("Text Input")
			#submit_text = st.form_submit_button(label='Submit')

		with st.form(key='emotion_clf_form1'):
			if message_number == b'1':
				customer_text = customer
			else:
				customer_text = 'waiting'
				
			#submit_text = st.form_submit_button(label='Submit')

		if message_number == b'1':
			col1,col2  = st.columns(2)

			# Apply Fxn Here
			prediction = predict_emotions(raw_text)
			probability = get_prediction_proba(raw_text)
			
			
			add_prediction_details(customer_text,raw_text,prediction,np.max(probability),datetime.now())

			with col1:
				st.success("Original Text")
				st.write(raw_text)

				st.success("Prediction")
				emoji_icon = emotions_emoji_dict[prediction]
				st.write("{}:{}".format(prediction,emoji_icon))
				st.write("Confidence:{}".format(np.max(probability)))



			with col2:
				st.success("Prediction Probability")
				# st.write(probability)
				proba_df = pd.DataFrame(probability,columns=pipe_lr.classes_)
				# st.write(proba_df.T)
				proba_df_clean = proba_df.T.reset_index()
				proba_df_clean.columns = ["emotions","probability"]

				fig = alt.Chart(proba_df_clean).mark_bar().encode(x='emotions',y='probability',color='emotions')
				st.altair_chart(fig,use_container_width=True)



	elif choice == "Monitor":
		st.subheader("Monitor App")

		with st.container():
			st.write("Emotion Classifier Metrics")
            # You can call any Streamlit command, including custom components:
			df_emotions = pd.DataFrame(view_all_prediction_details(),columns=['Customer','Rawtext','Prediction','Probability','Time_of_Visit'])
			st.dataframe(df_emotions)

			prediction_count = df_emotions['Prediction'].value_counts().rename_axis('Prediction').reset_index(name='Counts')
			pc = alt.Chart(prediction_count).mark_bar().encode(x='Prediction',y='Counts',color='Prediction')
			st.altair_chart(pc,use_container_width=True)
				


if __name__ == '__main__':
	main()
