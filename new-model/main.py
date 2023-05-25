# import whisper
import spacy
import difflib
# from spacy.lang.en.stop_words import STOP_WORDS
from collections import deque

nlp = spacy.load("en_core_web_sm")

# sentence = "get all emails phone names age gender from database db2 where age is greater than 25 and phoneno is equal 10 order by name in ascending and gender equal to male and phone equal 20"
sentence = "where age is more than 40 count name"
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
    "ascending" : "ASC",
    "descending" : "DESC",
}

reserved_keywords = ["get","give","find","from","where","and", "order","group","having","count"]



def filter_token(text, pos ):
    best_match = ""
    if(text in reserved_keywords):
        best_match = text
    elif(pos =="NOUN"):
        # for key in columns_present_in_DB:
        #     similarity_ratio = difflib.SequenceMatcher(None, key, text).ratio()
        #     if(similarity_ratio>0.8):
        #         best_match = key
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

            for it in range(i+1, i+4):
                where_clause.append(filtered_tokens[it])
            i=i+4
        elif(filtered_tokens[i]=="and"):
            if(filtered_tokens[i+1] in columns_present_in_DB):
                for it in range(i+1, i+4):
                    where_clause.append(filtered_tokens[it])
            i=i+4
        elif(filtered_tokens[i]=="order"):
            if(filtered_tokens[i+1] in columns_present_in_DB):
                for it in range(i+1, i+3):
                    orderby_clause.append(filtered_tokens[it])
            i=i+3




        else:
            i+=1

    
    return [selected_columns,
    from_database ,
    where_clause, orderby_clause, count]

        






        



            






print("extracting tokens.............")

filtered_tokens = []
for token in doc:
    # print(mapper_function(token.text, token.pos_))
    if(filter_token(token.text,token.pos_)!=""):
        filtered_tokens.append(filter_token(token.text,token.pos_))

    # print(token.text, token.pos_, token.dep_ )

print(filtered_tokens)
print(str(extracting_info(filtered_tokens)))
# print("checking")
# print(difflib.SequenceMatcher(None, "gerater", "greater").ratio())