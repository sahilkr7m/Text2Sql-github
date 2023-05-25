# import whisper
import spacy
import difflib
# from spacy.lang.en.stop_words import STOP_WORDS
from collections import deque

nlp = spacy.load("en_core_web_sm")

# sentence = "get all emails phone names age gender from database db2 where age is greater than 25 and phoneno is equal 10 order by name in ascending and gender equal to male and phone equal 20"
sentence = "get name email phoneno address where age greater than 30 and gender equal to male "
doc = nlp(sentence)

columns_present_in_DB = [
    "name",
    "age",
    "phone",
    "email",
    "address",
    "gender"
]


operator_mapping = {
    "greater" : ">",
    "less" : "<",
    "equal" : "=",
    "more" : ">",
    # "ascending" : "ASC",
    # "descending" : "DESC",
}

reserved_keywords = ["get","give","find","from","where","and", "order","group","having","count","ascending","descending"]

def map_column_with_db(text):
     for key in columns_present_in_DB:
                similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
                if(similarity_ratio>0.8):
                    return key


def map_input_column_array_with_db_columns(input_columns):
    mapped_array=[]
       
    for text in input_columns:
       if(map_column_with_db(text)):
            mapped_array.append(map_column_with_db(text))

    return mapped_array
    
# def operator_mapping_function(text):
#     for key,value in operator_mapping.items():
#             similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
#             if(similarity_ratio>0.8):
#                 return value

def filter_token(text, pos ):
    best_match = ""
    if(text in reserved_keywords):
        best_match = text
    elif(pos =="NOUN"):
        best_match = text

    elif(pos== "NUM"):
        best_match = text
    else:
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
        query+= "FROM DB"
        
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
    






        



            






print("extracting tokens.............")

filtered_tokens = []
for token in doc:
    # print(mapper_function(token.text, token.pos_))
    if(filter_token(token.text,token.pos_)!=""):
        filtered_tokens.append(filter_token(token.text,token.pos_))

    # print(token.text, token.pos_, token.dep_ )

print(filtered_tokens)
print(str(extracting_info(filtered_tokens)))
print(generate_query(extracting_info(filtered_tokens)))
# print("checking")
# print(difflib.SequenceMatcher(None, "gerater", "greater").ratio())