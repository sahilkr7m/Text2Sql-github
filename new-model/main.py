from flask import Flask, render_template, request
import spacy
import difflib
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector
from itertools import combinations
from fuzzywuzzy import fuzz
sbert_model = SentenceTransformer("paraphrase-mpnet-base-v2")
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

reserved_keywords = ["get","from","where","and", "order","group","having","count","ascending","descending","min","max","distinct","starts_with","ends_with",">","<","="]



# def map_column_with_db(text):
#      for key in columns_present_in_DB:
#                 similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
#                 if(similarity_ratio>0.5):
#                     return key

# def map_input_column_array_with_db_columns(input_columns):
#     mapped_array=[]
       
#     for text in input_columns:
#        if(map_column_with_db(text)):
#             mapped_array.append(map_column_with_db(text))

#     return mapped_array
   


def map_column_with_db(text):
    if(len(text)==1 and text[0] in columns_present_in_DB):
        return (text,True)
    for key in columns_present_in_DB:
                similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
                if(similarity_ratio>0.5):  #changed here
                    return (key,True)
    
    return (text,False)

def generate_different_columns_permutations(my_array):
    # Generate all combinations
    combinations_list = []
    for r in range(1, len(my_array) + 1):
        combinations_list.extend(combinations(my_array, r))

    # Concatenate the combinations
    concatenated_combinations = []
    for combination in combinations_list:
        concatenated_combinations.append("_".join(combination))

    # for combination in concatenated_combinations:
    #     print(combination)

    return concatenated_combinations


def join_column_names(array):
    string=""
    for item in array:
        string+="_"+ item
    
    return string



def map_input_column_array_with_db_columns(input_columns):
    mapped_array=[]
    
    for text in input_columns:
            print("checking for text in DB :",text)
            if(len(text)==1):
                key, is_present = map_column_with_db(text)
                # print("map_column_with_db(text)",map_column_with_db(text))

                if(is_present):
                        input_columns.remove(text)
                        print("column appending in array ",key[0])
                        mapped_array.append(key[0])
                
            else:                   
                print("Text we got: ",text)
                print("join_column_names(text)",join_column_names(text))
                key, is_present = map_column_with_db(join_column_names(text))

                if(is_present):
                        input_columns.remove(text)
                        print("column appending in array ",key)
                        mapped_array.append(key)
                
                # generated_columns_combinations = generate_different_columns_permutations(text)
                # print("all combinations of columns.. which were not matched")
                # print(generated_columns_combinations)

                # for item in generated_columns_combinations:
                #     key, is_present = map_column_with_db(item)
                #     # print(map_column_with_db(item))
                #     if(is_present):
                #         if(key not in mapped_array):
                #             print("column appending in array ",key)
                #             mapped_array.append(key)
                            


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
        change=0
        for key,values in map_keywords.items():
            if(text in values):
                best_match = replace_keywords_if_present(text)
                change=1
      
            # print("in filter token fxn and printing all matched operators")
        for key,value in operator_mapping.items():
                similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
                    # print(key,text,difflib.SequenceMatcher(None, key, text).ratio())
                if(similarity_ratio>0.8):
                    best_match = value
                    change=1
        if(change==0):
            best_match = text

    return best_match
        


def next_token_index(index_start, filtered_tokens):
    if(index_start==len(filtered_tokens)):
        return index_start
    
    i = index_start+1
    while(i<len(filtered_tokens)):
        if (filtered_tokens[i] in reserved_keywords or i==len(filtered_tokens)):
            return i
        i+=1
        
    return len(filtered_tokens) #reached end of array



def extracting_info(filtered_tokens):
    selected_columns =[]
    from_database =[]
    where_clause = []
    orderby_clause =[]
 
    aggregrator_functions = ["get", "count", "min","max","distinct"]
    agg_function_used =""

    i=0

    not_allowed = ["with","the","is","like","me","all","than","then","to"]
    updated_filtered_tokens=[]
    for item in filtered_tokens:
        # print("item is : ",item)
        if(item not in not_allowed):
            updated_filtered_tokens.append(item)

    if("get" not in filtered_tokens):
        updated_filtered_tokens = ["get"] + updated_filtered_tokens

    filtered_tokens = updated_filtered_tokens
    print("pre-processing the tokens")
    print(filtered_tokens)
    
    while(i<len(filtered_tokens)):
        if(filtered_tokens[i] in aggregrator_functions):
            agg_function_used = filtered_tokens[i]
            end_index = next_token_index(i, filtered_tokens)

            column_select=[]
            for it in range(i+1, end_index):
                    column_select.append(filtered_tokens[it])  
            i=end_index
            if(map_input_column_array_with_db_columns([column_select])):
                got_column =map_input_column_array_with_db_columns([column_select])[0]
                print("got_column in GET Function : ",got_column)
                

                if(got_column in columns_present_in_DB):
                        selected_columns.append([got_column])
      
            # print("in get fxn column_insert",column_insert, " endindex", i)

        elif(filtered_tokens[i]=="from"):
            end_index = next_token_index(i, filtered_tokens)

            for it in range(i+1, end_index):
                from_database.append(filtered_tokens[it])
            i=end_index

        elif(filtered_tokens[i]=="where"):
            # print("in where fxn")
            end_index = next_token_index(i, filtered_tokens)

            column_select=[]
            for it in range(i+1, end_index):
                column_select.append(filtered_tokens[it])  
            i=end_index

            # print("column_select",column_select)
            if(len(map_input_column_array_with_db_columns([column_select]))!=0):
                got_column=""
                if(len(column_select)==1):
                    got_column = map_input_column_array_with_db_columns([column_select])[0]
                else:
                    got_column= map_input_column_array_with_db_columns([column_select])[0][0]

            # print("got_column",got_column)

            if(i+1<len(filtered_tokens) and got_column in columns_present_in_DB):
                # print("here in if condtn")
                obj = {
                "col": got_column,
                "op": filtered_tokens[i],
                "val": filtered_tokens[i+1],
                }
                where_clause.append(obj )
                i=i+2
        elif(filtered_tokens[i]=="and"):

            # print("in and fxn")
            
            if(filtered_tokens[i+1] in [">","<","="] and len(where_clause)!=0):
                obj = {
                    "col": where_clause[-1]["col"],
                    "op": filtered_tokens[i+1],
                    "val": filtered_tokens[i+2],
                    }
                where_clause.append(obj )
                i=i+3
            else: 
                end_index = next_token_index(i, filtered_tokens)
            
                column_select=[]
                for it in range(i+1, end_index):
                    column_select.append(filtered_tokens[it])  
                i=end_index

                got_column=""
                if(len(map_input_column_array_with_db_columns([column_select]))!=0):
                    got_column = map_input_column_array_with_db_columns([column_select])[0]
                    print("got_column in AND Function : ",got_column)
               
                if(got_column in columns_present_in_DB):
                    
                    if(i !=len(filtered_tokens) and filtered_tokens[i] in [">","<","=","starts_with","ends_with"]):              
                            obj = {
                            "col": map_input_column_array_with_db_columns([column_select])[0],
                            "op": filtered_tokens[i],
                            "val": filtered_tokens[i+1],
                            }
                            where_clause.append(obj )
                            i=i+2
                    else:
                            print("got_column appending in select array",got_column)
                            selected_columns.append([got_column])
        

                        
                        

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
        # elif(filtered_tokens[i]=="like")
        else:
            # print("in else fxn")
            i+=1

    print("seperated values....")
    print([ selected_columns,
    from_database ,
    where_clause, orderby_clause, agg_function_used])

    return [(selected_columns),
    from_database ,
    where_clause, orderby_clause, agg_function_used]

        

def generate_query(query_array):
    selected_columns =query_array[0]
    from_database = query_array[1]
    where_clause = query_array[2]
    orderby_clause =query_array[3]
    agg_funtion_used =query_array[4]

    query = "SELECT "

    if(selected_columns==[]):
        return "ERROR in Input by User" 


    comma_count=0
    comma_count_max = len(selected_columns)-1
    if(agg_funtion_used=="count"):
        query+="COUNT("
        for i in selected_columns:
            query+= i[0]
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+=")"
        
        query+= " "
    elif(agg_funtion_used=="get"):
        print("in making query fxn - selected_columns",selected_columns)
        if(len(selected_columns)!=0):
            for i in selected_columns:
                query+=i[0]
                if(comma_count<comma_count_max):
                    query+=","
                    comma_count+=1
        # else:
        #     query+="*"
        
        query+= " "
    elif(agg_funtion_used=="min"):
        query+="MIN("
        for i in selected_columns:
            query+= i
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+=")"
        
        query+= " "
    elif(agg_funtion_used=="max"):
        query+="MAX("
        for i in selected_columns:
            query+= i
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+=")"
        
        query+= " "
    elif(agg_funtion_used=="distinct"):
        query+="DISTINCT("
        for i in selected_columns:
            query+= i
            if(comma_count<comma_count_max):
                query+=","
                comma_count+=1
        
        query+=")"
        
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
            if(item["op"]=="starts_with"):
               query+= item["col"] + " " + "LIKE" + " " + "'"+ item["val"] +"%'"+ " "
               if(and_count<and_count_max):
                    query+="AND"
                    and_count+=1 
            elif(item["op"]=="ends_with"):
               query+= item["col"] + " " + "LIKE" + " " + "'%"+ item["val"] +"'"+ " "
               if(and_count<and_count_max):
                    query+="AND"
                    and_count+=1 
            else:
                query+= item["col"] + " " + item["op"] + " '" + item["val"]+ "' "
                if(and_count<and_count_max):
                    query+="AND"
                    and_count+=1
            
            query+= " "

    if(len(orderby_clause)!=0):
        query+="ORDER BY " + orderby_clause[0]+ " "+ orderby_clause[1]
    
    return query
    
map_keywords = {
    "get" : ['show', 'retrieve', 'display', 'list', 'fetch', 'view', 'select', 'show',"search","find","yet","give"],
    "where" : ["whose","were", "filter","condition","limit","narrow","include","restrict","match","constraints","bear","their"],
    "max": ["maximum","largest","maxi"],
    "min": ["minimum","smallest","mini"],
    "distinct" : ["unique","different"],
    "starts_with" : ["start", "starts"],
    "ends_with" : ["ends","end"],
    "less" : ["below"],
    "greater" : ["above"]
}    

def replace_keywords_if_present(token):

    for key,values in map_keywords.items():
        if(token in values):
            return key 
        
    return token

            
###############################################################################################
#FOR DEBUGGINGGG---------


# sentence = "age and email id"
# # sentence = "where age is more than 50 show yet give find email id "
# doc = nlp(sentence)

# print("sentence..........")
# print(sentence)

# filtered_tokens = []
# for token in doc:
#     # print((token.text, token.pos_))
#     if(filter_token(token.text,token.pos_)!=""):
#         filtered_tokens.append(filter_token(token.text,token.pos_))

# print("extracting tokens.............")
# print(filtered_tokens)
# # print("seperating them in different arrays...")
# # print(str(extracting_info(filtered_tokens)))
# # print("query generated....")
# print(generate_query(extracting_info(filtered_tokens)))

# print("executing query on SQL")
# sqlQuery=generate_query(extracting_info(filtered_tokens))
# results=execute_query(sqlQuery)

# print(results)

################################################################################################

#Integrated logic , if the user gets an empty response  ===>


def extract_column_from_query(query):
    doc = nlp(query)
    column = None

    for token in doc:
        if token.pos_ == "NOUN" and token.text in columns_present_in_DB:
            column = token.text
            break

    return column

def generate_prompt(column_name, operator=None, value=None, select_clause="*", from_clause=None, group_by_clause=None, having_clause=None, order_by_clause=None, limit_clause=None, like_value=None, insert_clause=None, update_clause=None):
    prompt = column_name.replace("_", " ").title()

    conditions = []
    if operator and value:
        conditions.append(f"{column_name} {operator} {value}")
    if group_by_clause:
        conditions.append(f"GROUP BY {group_by_clause}")
    if having_clause:
        conditions.append(f"HAVING {having_clause}")
    if order_by_clause:
        conditions.append(f"ORDER BY {order_by_clause}")
    if limit_clause:
        conditions.append(f"LIMIT {limit_clause}")
    if like_value:
        conditions.append(f"{column_name} LIKE '{like_value}'")
    if insert_clause:
        conditions.append(f"INSERT INTO table {insert_clause}")
    if update_clause:
        conditions.append(f"UPDATE table SET {update_clause}")

    where_clause = " AND ".join(conditions)
    prompt = f"What is the {prompt} where {where_clause}?"

    return prompt



prompts = []


for i in range(1000):
    column = columns_present_in_DB[i % len(columns_present_in_DB)]

    
    select_clause = columns_present_in_DB[i % len(columns_present_in_DB)]
    prompt = generate_prompt(column, select_clause=select_clause)
    prompts.append(prompt)

    
    


def generate_query_2(column_name, table_name, where_clause=None, select_clause="*", from_clause=None,
                   group_by_clause=None, having_clause=None, order_by_clause=None, limit_clause=None,
                   like_value=None, insert_clause=None, update_clause=None, delete_clause=None):
    queries = []

    

    if not any([insert_clause, update_clause, delete_clause]):
        query = f"SELECT {select_clause} FROM {table_name}"
        if from_clause:
            query += f" {from_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"
        if group_by_clause:
            query += f" GROUP BY {group_by_clause}"
        if having_clause:
            query += f" HAVING {having_clause}"
        if order_by_clause:
            query += f" ORDER BY {order_by_clause}"
        if limit_clause:
            query += f" LIMIT {limit_clause}"
        if like_value:
            query += f" AND {column_name} LIKE '{like_value}%'"

        queries.append(query)

        second_query = query.replace(f"SELECT {select_clause}", f"SELECT {select_clause}")
        queries.append(second_query)

        if "and" in table_name:
            tables = table_name.split(" and ")
            for t in tables:
                q = query.replace(table_name, t)
                queries.append(q)

    return queries


queries = []


for prompt in prompts:
    column = prompt.split(" ")[3].lower()  
    operator = prompt.split(" ")[5]  
    value = prompt.split(" ")[-1]  
    select_clause = prompt.split(" ")[2]  
    from_clause = "svoc_v2"
    group_by_clause = "some_column" if "GROUP BY" in prompt else None
    having_clause = "some_condition" if "HAVING" in prompt else None
    order_by_clause = "some_column" if "ORDER BY" in prompt else None
    limit_clause = "some_limit" if "LIMIT" in prompt else None
    like_value = prompt.split("'")[1] if "LIKE" in prompt else None

    query = generate_query_2(column, "svoc_v2", where_clause=f"{column} {operator} '{value}'", select_clause=select_clause, from_clause=from_clause, group_by_clause=group_by_clause, having_clause=having_clause, order_by_clause=order_by_clause, limit_clause=limit_clause, like_value=like_value)
    queries.extend(query)

def generate_query_from_user_query(user_query):
    doc = nlp(user_query)
    column_matches = []
    operator = None
    value = None

    operator_mapping = {
        "equal": "=",
        "equals": "=",
        "is equal to": "=",
        "less": "<",
        "less than": "<",
        "lesser than": "<",
        "greater": ">",
        "greater than": ">",
        "more than": ">",
    }

    for token in doc:
        if token.text in columns_present_in_DB:
            column_matches.append(token.text)
        elif token.text in operator_mapping:
            operator = operator_mapping[token.text]
        elif operator and token.pos_ in ["NUM", "NOUN"]:
            value = token.text
    
    sql_prompts = []
    sql_queries = []

    if column_matches and operator and value:
        where_clause = " AND ".join([f"{column} {operator} '{value}'" for column in column_matches])
        select_clause = ", ".join(column_matches)
        query = generate_query_2(None, "svoc_v2", where_clause=where_clause, select_clause=select_clause)
        sql_prompts.append(user_query)
        sql_queries.append(query)
    elif column_matches:
        for column_match in column_matches:
            prompt = generate_prompt(column_match)
            query = generate_query_2(column_match, "svoc_v2", select_clause=column_match)
            sql_prompts.append(prompt)
            sql_queries.append(query)
    else:
        for column in columns_present_in_DB:
            prompt = generate_prompt(column)
            query = generate_query_2(column, "svoc_v2")
            sql_prompts.append(prompt)
            sql_queries.append(query)

    user_query_embedding = sbert_model.encode([user_query])
    sql_prompt_embeddings = sbert_model.encode(sql_prompts)

    similarity_scores = cosine_similarity(user_query_embedding, sql_prompt_embeddings)[0]

    best_match_index = similarity_scores.argmax()
    best_match_sql_prompt = sql_prompts[best_match_index]

    best_match_index = sql_prompts.index(best_match_sql_prompt)
    sql_query = sql_queries[best_match_index]
    print("Generated SQL Query:")
    print(sql_query)

    return sql_query



def detect_column_names(user_query, columns_list):
    
    doc = nlp(user_query)

    detected_columns = []

    
    for token in doc:
        best_match_score = 0
        best_match_column = None
        
        for column in columns_list:
            
            match_score = fuzz.ratio(token.text.lower(), column.lower())
            
            
            if match_score > best_match_score:
                best_match_score = match_score
                best_match_column = column
        
        
        if best_match_score > 80:  
            detected_columns.append(best_match_column)
    
    return detected_columns


def replace_column_names(user_query, columns_list, replacement_list):
    
    detected_columns = detect_column_names(user_query, columns_list)

    
    for column in detected_columns:
        replacement = replacement_list.get(column)
        if replacement:
            user_query = user_query.replace(column, replacement)

    return user_query


############################################################################################


#FLASK APP

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


    sqlQuery1=generate_query(extracting_info(filtered_tokens))
    print("query generated: ", sqlQuery1)
    print("executing query on SQL")
    results=execute_query(sqlQuery1)
    print(results)
    if(len(results)==0):
            columns_list = ['email','mobile','number','numbers','name', 'age', 'gender','mails','mail','emails']
            replacement_list = {
                    'email': 'emailid_f',
                    'mobile': 'mobile_f',
                    'number':'mobile_f',
                    'numbers':'mobile_f',
                    'name': 'fullname',
                    'age': 'age',
                    'gender': 'gender',
                    'mail':'emailid_f',
                    'mails':'emailid_f',
                    'emails':'emailid_f',
                }
    
            modified_query = replace_column_names(text_data, columns_list, replacement_list)
            print("modified query is")
            print(modified_query)
            sql_query2 = generate_query_from_user_query(modified_query)
            print(sql_query2)
            results2=execute_query(sql_query2[0])
            if(sql_query2[0]=="SELECT * FROM svoc_v2"):
                results = "NOT-A-PROPER-QUERY"
            else:
                results=execute_query(sql_query2[0])
    

    # print(results)

    if(len(results)==0):
    
        return [sql_query2[0],results2]
    
    else:
        return [sqlQuery1,results]

    

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)



