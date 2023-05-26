# import whisper
from flask import Flask, render_template, request
import spacy
import difflib
# from spacy.lang.en.stop_words import STOP_WORDS
from collections import deque
import mysql.connector

nlp = spacy.load("en_core_web_sm")


mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'test_db'
}

def execute_query(query):
    try:
        connection = mysql.connector.connect(**mysql_config)
        cursor = connection.cursor()

        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        connection.close()

        return results
    except Exception as e:
        print(f"Error executing query: {e}")

    return []



columns_present_in_DB = [
   "emailid_f",
    "mobile_f",
    "title",
    "fullname",
    "bills",
    "seats",
    "ftd_issue_date",
    "ltd_issue_date",
    "bills_weekend",
    "bills_weekday",
    "percent_bills_weekend",
    "percent_bills_weekday",
    "city_town_bills_destination",
    "leisure_bills_destination",
    "city_town_bills_source",
    "leisure_bills_source",
    "percent_pax_1",
    "percent_pax_2",
    "percent_pax_3",
    "percent_pax_4",
    "percent_pax_gt4",
    "revenue",
    "age",
    "agent_tag",
    "favourite_bus_type",
    "recency",
    "active_churn",
    "asp",
    "percent_last_min_bills",
    "last_min_booking",
    "weekend_weekday_travellers",
    "percent_city_town_destination",
    "percent_leisure_destination",
    "percent_city_town_source",
    "percent_leisure_source",
    "valid_mob_tag",
    "valid_email_tag",
    "rt_feature",
    "fav_source",
    "fav_destination",
    "fav_weekend_destination",
    "home_traveller",
    "discount_seeker",
    "bills_discount",
    "discount_value",
    "age_bands",
    "atv",
    "atv_segments",
    "tenure",
    "tenure_bands",
    "first_trax_medium",
    "last_trax_medium",
    "city_leisure_destination_split",
    "city_leisure_source_split",
    "ac_trax_count",
    "active_days",
    "gender",
    "recency_band",
    "fav_booking_day",
    "fav_journey_day",
    "fav_booking_time",
    "active_days_1yr",
    "active_3months",
    "hf_base",
    "exclude_tags",
    "exclude_tags_churn",
    "dates_fav",
    "prev_camp_date_hyg",
    "camp_day_gap_hyg",
    "weekend_base",
    "religious_travellers",
    "leisure_travellers",
    "control",
    "waterfall_seg",
    "ftd_plus_12months",
    "premium_base",
    "no_of_disc_bills",
    "percent_disc_bills",
    "fav_medium",
    "student_home_tc_final",
    "student_others_tc_final",
    "start_date",
    "date_execution",
    "date_upload",
    "travel_month_gap",
    "_epoch",
    "_visid",
    "fav_journey_hour",
    "bus_cust",
    "percent_ac_bills",
    "percent_bills_discount",
    "distinct_operator",
    "distinct_bustype",
    "distinct_tranx_medium",
    "traveller_type",
    "source_tier_split",
    "single_group_tag",
    "traveller_type_v1",
    "migration_base_v1",
    "migration_base",
    "open_12",
    "open_24",
    "control_email",
    "ftd_present_diff",
    "last_route_travelled",
    "favourite_operator",
    "fav_route",
    "fav_journey_time",
    "last_journey_date",
    "fav_sourceid",
    "fav_destinationid",
    "fav_source_state",
    "fav_destination_state",
    "walletid",
    "wallet_status",
    "wallet_balance",
    "last_search_source",
    "last_search_destination",
    "last_search_medium",
    "sessions_app",
    "sessions_web",
    "sessiosns_ios",
    "pages_viewed",
    "noofsessions",
    "total_searches",
    "app_used",
    "last_page_viewed",
    "business_travellers",
    "last_search_date",
    "bills_desktop",
    "bills_app",
    "bills_web",
    "ftr_top_source1",
    "ftr_top_source2",
    "ftr_top_source3",
    "ftr_top_dest1",
    "ftr_top_dest2",
    "ftr_top_dest3",
    "paytm_presence",
    "app_used_6months",
    "ftd_phonepe",
    "last_min_bills_new"
]


operator_mapping = {
    "greater" : ">",
    "less" : "<",
    "equal" : "=",
    "more" : ">",
    # "ascending" : "ASC",
    # "descending" : "DESC",
}

reserved_keywords = ["get","from","where","and", "order","group","having","count","ascending","descending"]

def map_column_with_db(text):
     for key in columns_present_in_DB:
                similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
                if(similarity_ratio>0.5):
                    return key


def map_input_column_array_with_db_columns(input_columns):
    mapped_array=[]
       
    for text in input_columns:
       if(map_column_with_db(text)):
            mapped_array.append(map_column_with_db(text))

    return mapped_array
    

def filter_token(text, pos ):
    best_match = ""
    if(text in reserved_keywords):
        best_match = text
    elif(pos =="NOUN"):
        best_match = replace_keywords_if_present(text)

    elif(pos== "NUM"):
        best_match = text
    else:
        
        for key,values in map_keywords.items():
            if(text in values):
                best_match = replace_keywords_if_present(text)
        
        for key,value in operator_mapping.items():
                similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
                if(similarity_ratio>0.8):
                    best_match = value

    return best_match
        


def next_token_index(index_start, filtered_tokens):
    i = index_start+1
    while(i<len(filtered_tokens)):
        if (filtered_tokens[i] in reserved_keywords):
            return i
        i+=1
        
    return len(filtered_tokens) #reached end of array



def extracting_info(filtered_tokens):
    selected_columns =[]
    from_database =[]
    where_clause = []
    orderby_clause =[]
    count =0

    i=0
    
    while(i<len(filtered_tokens)):
        if(filtered_tokens[i]=="get" or filtered_tokens[i]=="count"):
            if(filtered_tokens[i]=="count"):
                count=1
            end_index = next_token_index(i, filtered_tokens)
       
            for it in range(i+1, end_index):
                selected_columns.append(filtered_tokens[it])
            i=end_index
        elif(filtered_tokens[i]=="from"):
            end_index = next_token_index(i, filtered_tokens)

            for it in range(i+1, end_index):
                from_database.append(filtered_tokens[it])
            i=end_index
        elif(filtered_tokens[i]=="where"):
            obj = {
                "col": map_column_with_db(filtered_tokens[i+1]),
                "op": filtered_tokens[i+2],
                "val": filtered_tokens[i+3],
            }
            where_clause.append(obj )
            
            # for it in range(i+1, i+4):                
            #     where_clause.append(filtered_tokens[it])
            i=i+4
        elif(filtered_tokens[i]=="and"):

            if(filtered_tokens[i+1] in columns_present_in_DB):
                obj = {
                "col": map_column_with_db(filtered_tokens[i+1]),
                "op": filtered_tokens[i+2],
                "val": filtered_tokens[i+3],
                }
                where_clause.append(obj )
            
            i=i+4

        elif(filtered_tokens[i]=="order"):
            if(filtered_tokens[i+1] in columns_present_in_DB):

                orderby_clause.append(map_column_with_db(filtered_tokens[i+1]))
                orderby = ""
                if(difflib.SequenceMatcher(None, filtered_tokens[i+2], "ascending").ratio()>0.8):
                    orderby="ASC"
                elif(difflib.SequenceMatcher(None, filtered_tokens[i+2], "descending").ratio()>0.8):
                    orderby="DESC"
                orderby_clause.append(orderby)
                # for it in range(i+1, i+3):
                #     orderby_clause.append(filtered_tokens[it])
            i=i+3
        else:
            i+=1



    return [ map_input_column_array_with_db_columns(selected_columns),
    from_database ,
    where_clause, orderby_clause, count]

        

def generate_query(query_array):
    selected_columns =query_array[0]
    from_database = query_array[1]
    where_clause = query_array[2]
    orderby_clause =query_array[3]
    count =query_array[4]

    query = ""
    comma_count=0
    comma_count_max = len(selected_columns)-1
    if(count==1):
        query+="SELECT COUNT("
        for i in selected_columns:
            query+= i
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+=")"
        
        query+= " "
    else:

        query+="SELECT "
        for i in selected_columns:
            query+=i
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+= " "

    if(len(from_database)==0):
        query+= "FROM svoc_v2"
        
        query+= " "
    else:
        query+= "FROM "+ from_database[0]
        
        query+= " "


    if(len(where_clause)!=0):    
        and_count_max = len(where_clause) -1
        and_count=0

        query+= "WHERE "
        for item in where_clause:
            query+= item["col"] + " " + item["op"] + " " + item["val"]+ " "
            if(and_count<and_count_max):
                query+="AND"
                and_count+=1
            
            query+= " "

    if(len(orderby_clause)!=0):
        query+="ORDER BY " + orderby_clause[0]+ " "+ orderby_clause[1]
    
    return query
    
map_keywords = {
    "get" : ['show', 'retrieve', 'display', 'list', 'fetch', 'view', 'select', 'show',"search","find","yet"],
    "where" : ["whose","were", "filter","condition","limit","narrow","include","restrict","match","constraints"]
}    

def replace_keywords_if_present(token):

    for key,values in map_keywords.items():
        if(token in values):
            return key 
        
    return token

            

#FOR DEBUGGINGGG---------

# sentence = "yet all emails phone names from database db2 were age is greater than 25 and fav_destination_state is equal 10"
# # sentence = "where age is more than 50 show yet give find emails "
# doc = nlp(sentence)

# filtered_tokens = []
# for token in doc:
#     # print(mapper_function(token.text, token.pos_))
#     if(filter_token(token.text,token.pos_)!=""):
#         filtered_tokens.append(filter_token(token.text,token.pos_))


# print("extracting tokens.............")
# print(filtered_tokens)
# print("seperating them in different arrays...")
# print(str(extracting_info(filtered_tokens)))
# print("query generated....")
# print(generate_query(extracting_info(filtered_tokens)))

# print("executing query on SQL")
# sqlQuery=generate_query(extracting_info(filtered_tokens))
# results=execute_query(sqlQuery)

# print(results)












app = Flask(__name__)



@app.route('/')
def home():
    return render_template('Text2Sql-github\templates\index.html', results=[])

@app.route('/query', methods=['POST'])
def process_query():

    text_data = request.get_data(as_text=True)
    print(text_data)

    sentence = text_data
    doc = nlp(sentence)

    filtered_tokens = []
    for token in doc:
        # print(mapper_function(token.text, token.pos_))
        if(filter_token(token.text,token.pos_)!=""):
            filtered_tokens.append(filter_token(token.text,token.pos_))


    print("extracting tokens.............")
    print(filtered_tokens)
    print("seperating them in different arrays...")
    print(str(extracting_info(filtered_tokens)))
    print("query generated....")
    print(generate_query(extracting_info(filtered_tokens)))

    print("executing query on SQL")
    sqlQuery=generate_query(extracting_info(filtered_tokens))
    results=execute_query(sqlQuery)

    # print(results)


    return str(results)
    # return render_template('Text2Sql-github\templates\index.html', results=results)

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)
