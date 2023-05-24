from flask import Flask, render_template, request
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import mysql.connector
import json
from fuzzywuzzy import fuzz



app = Flask(__name__)

mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'test_db'
}


nlp = spacy.load("en_core_web_sm")
columns = [
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


sbert_model = SentenceTransformer("paraphrase-mpnet-base-v2")

def extract_column_from_query(query):
    doc = nlp(query)
    column = None

    for token in doc:
        if token.pos_ == "NOUN" and token.text in columns:
            column = token.text
            break

    return column

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


for i in range(100):
    column = columns[i % len(columns)]

    
    select_clause = columns[i % len(columns)]
    prompt = generate_prompt(column, select_clause=select_clause)
    prompts.append(prompt)

    
    insert_clause = f"({column}) VALUES ('value_{i}')"
    prompt = generate_prompt(column, insert_clause=insert_clause)
    prompts.append(prompt)

    
    update_clause = f"{column} = 'new_value_{i}'"
    prompt = generate_prompt(column, update_clause=update_clause)
    prompts.append(prompt)


print(prompts)
# Print the generated prompts
for prompt in prompts:
    print(prompt)

def generate_query(column_name, table_name, where_clause=None, select_clause="*", from_clause=None,
                   group_by_clause=None, having_clause=None, order_by_clause=None, limit_clause=None,
                   like_value=None, insert_clause=None, update_clause=None, delete_clause=None):
    queries = []

    if insert_clause:
        query = f"INSERT INTO {table_name} {insert_clause}"
        queries.append(query)

    if update_clause:
        query = f"UPDATE {table_name} SET {update_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"
        queries.append(query)

    if delete_clause:
        query = f"DELETE FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        queries.append(query)

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

# Generate queries based on the prompts
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

    query = generate_query(column, "svoc_v2", where_clause=f"{column} {operator} '{value}'", select_clause=select_clause, from_clause=from_clause, group_by_clause=group_by_clause, having_clause=having_clause, order_by_clause=order_by_clause, limit_clause=limit_clause, like_value=like_value)
    queries.extend(query)

# Print the generated queries
for query in queries:
    print(query)

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
        if token.text in columns:
            column_matches.append(token.text)
        elif token.text in operator_mapping:
            operator = operator_mapping[token.text]
        elif operator and token.pos_ in ["NUM", "NOUN"]:
            value = token.text
    
    sql_prompts = []
    sql_queries = []

    if column_matches and operator and value:
        for column_match in column_matches:
            prompt = generate_prompt(column_match, operator, value)
            query = generate_query(column_match, "svoc_v2", where_clause=f"{column_match} {operator} '{value}'", select_clause=column_match)
            sql_prompts.append(prompt)
            sql_queries.append(query)
    elif column_matches:
        for column_match in column_matches:
            prompt = generate_prompt(column_match)
            query = generate_query(column_match, "svoc_v2", select_clause=column_match)
            sql_prompts.append(prompt)
            sql_queries.append(query)
    else:
        for column in columns:
            prompt = generate_prompt(column)
            query = generate_query(column, "svoc_v2")
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
    # Tokenize the user query using spaCy
    doc = nlp(user_query)

    detected_columns = []

    # Iterate over the tokens and perform fuzzy matching with the column names
    for token in doc:
        best_match_score = 0
        best_match_column = None
        
        for column in columns_list:
            # Calculate the fuzzy matching score
            match_score = fuzz.ratio(token.text.lower(), column.lower())
            
            # Update the best match if the current score is higher
            if match_score > best_match_score:
                best_match_score = match_score
                best_match_column = column
        
        # Adjust the threshold as per your requirement
        if best_match_score > 80:  # Consider a match if the score is above 80
            detected_columns.append(best_match_column)
    
    return detected_columns


def replace_column_names(user_query, columns_list, replacement_list):
    # Detect the column names in the user query
    detected_columns = detect_column_names(user_query, columns_list)

    # Replace the detected column names with the provided replacement list
    for column in detected_columns:
        replacement = replacement_list.get(column)
        if replacement:
            user_query = user_query.replace(column, replacement)

    return user_query



@app.route('/')
def home():
    return render_template('index.html', results=[])

@app.route('/query', methods=['POST'])
def process_query():
<<<<<<< HEAD
    user_query = request.form['user_query']
    user_query = user_query.lower()
    print(user_query)
    
    
    
    
=======
    # user_query = request.form['user_query']
    # user_query = user_query.lower()
    # print(user_query)

    text_data = request.get_data(as_text=True)
    print(text_data)
    user_query = text_data

>>>>>>> 5e0c0c228cf92887d7251fb4e3c702fb4f4fce6c
    columns_list = ['email', 'mobile', 'name', 'age', 'gender','mails','mail']
    replacement_list = {
        'email': 'emailid_f',
        'mobile': 'mobile_f',
        'name': 'fullname',
        'age': 'age',
        'gender': 'gender',
        'mail':'emailid_f',
        'mails':'emailid_f',
        'emails':'emailid_f',
    }

    modified_query = replace_column_names(user_query, columns_list, replacement_list)
    sql_query = generate_query_from_user_query(modified_query)
    print(sql_query)
    results = execute_query(sql_query[0])
    # print(results)
    # results = sql_query[0]
    print(results)

<<<<<<< HEAD
    return render_template('index.html', results=results)
=======
    return str(results)
    # return render_template('index.html', results=results)
>>>>>>> 5e0c0c228cf92887d7251fb4e3c702fb4f4fce6c

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)

