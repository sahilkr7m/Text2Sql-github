from typing import List
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

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

tokenizer = AutoTokenizer.from_pretrained("juierror/text-to-sql-with-table-schema")
model = AutoModelForSeq2SeqLM.from_pretrained("juierror/text-to-sql-with-table-schema")

def prepare_input(question: str, table: List[str]):
    table_prefix = "table:"
    question_prefix = "question:"
    join_table = ",".join(table)
    inputs = f"{question_prefix} {question} {table_prefix} {join_table}"
    input_ids = tokenizer(inputs, max_length=700, return_tensors="pt").input_ids
    return input_ids

def inference(question: str, table: List[str]) -> str:
    input_data = prepare_input(question=question, table=table)
    input_data = input_data.to(model.device)
    outputs = model.generate(inputs=input_data, num_beams=10, top_k=10, max_length=700)
    result = tokenizer.decode(token_ids=outputs[0], skip_special_tokens=True)
    return result


table = [
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



def replace_word(sentence, target_word, replacement_word):
    words = sentence.split()  
    
    
    replaced_words = [word if word != target_word else replacement_word for word in words]
    
    
    replaced_sentence = ' '.join(replaced_words)
    
    return replaced_sentence

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








print(inference(question="get people fullname with age equal 25 and email like sahil.kumar", table=table))

@app.route('/')
def home():
    return render_template('index.html', results=[])

@app.route('/query', methods=['POST'])
def process_query():
    # user_query = request.form['user_query']
    # user_query = user_query.lower()
    text_data = request.get_data(as_text=True)
    print(text_data)
    user_query = text_data

    sql_query = inference(question=user_query, table=table)
    replaced_sentence=replace_word(sql_query,"table","svoc_v2")
    print(replaced_sentence)
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
    modified_query = replace_column_names(replaced_sentence, columns_list, replacement_list)

    results = execute_query(modified_query)
    if results:
        print(results)
    else:
        results="Not a Proper query"
    
    # print(results)
    return str(results)
    # return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(host="localhost", port=8000, debug=True)

