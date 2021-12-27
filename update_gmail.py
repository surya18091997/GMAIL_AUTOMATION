from base import authenticate
import json,sys


def frame_search_query(data):
    try:
        q=""
        if "condition" in data:
            for i in data["rule"]:
                if "field_name" in i:
                    if i["predicate"]=="contains":
                        if q!="":
                            if data["condition"]=="all":
                                q+=" "
                            elif data["condition"]=="any":
                                q+=" OR "
                        q+=i["field_name"]+":"
                        q+=i["value"]
                    elif i["predicate"]=="not equals":
                        if q!="":
                            if data["condition"]=="all":
                                q+=" "
                            elif data["condition"]=="any":
                                q+=" OR "
                        q+="-"+i["field_name"]+":"+i["value"]
                    elif i["predicate"]=="less than":
                        if q!="":
                            if data["condition"]=="all":
                                q+=" "
                            elif data["condition"]=="any":
                                q+=" OR "
                        q+="before:"+i["value"]
                    elif i["predicate"]=="greater than":
                        if q!="":
                            if data["condition"]=="all":
                                q+=" "
                            elif data["condition"]=="any":
                                q+=" OR "
                        q+="after:"+i["value"]

        return q
    except :
        print("Input json is wrong")


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
        return (message_ids_list)

    except Exception as e:
        print(str(e))

def perform_action(service,user_id,message_ids_list,data):
    try:
        if data["action"]["mail_action"]=="Mark as Read":
            
            for i in message_ids_list:
                action=service.users().messages().modify(userId=user_id,id=i,body={'removeLabelIds': ['UNREAD']}).execute()
        elif data["action"]["mail_action"]=="Move Message":
            if "current" in data["action"] and "to" in data["action"]:
                body={
                    'removeLabelIds': [data["action"]["current"]],
                    'addLabelIds':[data['action']['to']]
                }
                for i in message_ids_list:
                    action=service.users().messages().modify(userId=user_id,id=i,body=body).execute()

    except Exception as e:
        print(e)




if __name__ == '__main__':
    path=sys.argv[1]
    js=open(path,'r')
    data = json.load(js)
    query=frame_search_query(data)
    print(query)
    #service=authenticate()
    #if service:
        #user_id='me'
        #msg_ids=get_all_message_ids(service,user_id,query)
        #perform_action(service,user_id,msg_ids,data)
