from base import authenticate
import email
import base64
from dateutil import parser
import psycopg2

def db_connect():
     conn = psycopg2.connect(
     host="localhost",
     database="happyfox",
     user="postgres",
     password="postgres")
     cur = conn.cursor()
     return conn,cur

def post_to_db(service,user_id,message_ids_list):
    try:
        db_records_dict=[]
        for i in message_ids_list:
            message_raw=service.users().messages().get(userId=user_id,id=i,format='raw').execute()
            message_bytes=base64.urlsafe_b64decode(message_raw['raw'].encode('ASCII'))
            final_msg=email.message_from_bytes(message_bytes)
            record_dict={}
            record_dict['msg_id']=i
            record_dict['from_string']=final_msg['From']
            q=str(final_msg['From'])
            from_email=q[q.index("<")+1:q.index(">")]
            record_dict['from_email']=from_email
            record_dict['to_email']=final_msg['To']
            record_dict['email_date'] = parser.parse(final_msg['Date']).date()
            record_dict['email_time']=parser.parse(final_msg['Date']).time()
            record_dict['subject']=final_msg['Subject']
            db_records_dict.append(record_dict)
        #print(db_records_dict)
        conn,cur=db_connect()
        cur.executemany("INSERT INTO gmail (msg_id,from_string,from_email,to_email,email_date,email_time,subject) VALUES (%(msg_id)s,%(from_string)s,%(from_email)s,%(to_email)s,%(email_date)s,%(email_time)s,%(subject)s) ON CONFLICT (msg_id) DO UPDATE SET from_string = %(from_string)s ,from_email = %(from_email)s,to_email=%(to_email)s,email_date=%(email_date)s,email_time=%(email_time)s,subject=%(subject)s;;",db_records_dict)
        conn.commit()
        print("Database Updated with records")
    except Exception as e:
        print(str(e))    

def get_all_message_ids(service,user_id,query):
    try:
        pageToken= None
        message_ids_list=[]
        message_ids=service.users().messages().list(userId=user_id,q=query).execute()
        message_ids_list+=[i['id'] for i in message_ids['messages']]
        while 'nextPageToken' in message_ids.keys():
           Token=message_ids['nextPageToken']
           message_ids=service.users().messages().list(userId=user_id,q=query,pageToken=Token).execute()
           message_ids_list+=[i['id'] for i in message_ids['messages']]
        post_to_db(service,user_id,message_ids_list)

    except Exception as e:
        print(e)


            







if __name__ == '__main__':
    service=authenticate()
    print(service)
    if service:
        user_id='me'
        query="subject:HappyFox"
        get_all_message_ids(service,user_id,query)
