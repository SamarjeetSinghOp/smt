from flask import Flask, request, jsonify
import pandas as pd
from fuzzywuzzy import process

# Load the exercise data from the Excel file
exercise_data = pd.read_excel('exercise_dataset_revised.xlsx')

app = Flask(__name__)

def calculate_calories(data):
    weight = data['weight']
    duration = data['duration']
    
    if 'exercise_id' in data:
        exercise_id = data['exercise_id']
        # Find the exercise details from the dataset using the ID
        exercise = exercise_data[exercise_data['ID'] == exercise_id]
        if exercise.empty:
            raise ValueError("No match found for the exercise ID.")
        exercise = exercise.iloc[0]
    elif 'exercise_name' in data:
        exercise_name = data['exercise_name']
        # Find the closest exercise name from the dataset using fuzzywuzzy
        exercise_names = exercise_data['Activity, Exercise or Sport (1 hour)'].tolist()
        closest_match, score = process.extractOne(exercise_name, exercise_names, score_cutoff=60)
        if not closest_match:
            raise ValueError("No close match found for the exercise name.")
        exercise = exercise_data[exercise_data['Activity, Exercise or Sport (1 hour)'] == closest_match].iloc[0]
    else:
        raise ValueError("Either exercise_id or exercise_name must be provided.")
    
    # Calculate calories burnt
    avg_calories_per_minute_per_kg = exercise['Average Calories per Minute per Kg']
    calories_burnt = avg_calories_per_minute_per_kg * weight * duration
    
    # Prepare the output
    output = {
        'name': exercise['Activity, Exercise or Sport (1 hour)'],
        'calories_burnt': calories_burnt
    }
    
    return output

@app.route('/calculate_calories', methods=['POST'])
def calculate_calories_endpoint():
    try:
        data = request.get_json()
        result = calculate_calories(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(port=1363, debug=True)



# import statement for fuzzywuzzzy 
# pip install fuzzywuzzy python-Levenshtein

# input sample for this
# with name 
# {
#   "weight": 70,
#   "exercise_name": "pushups",
#   "duration": 60
# }
# with id
# {
#   "weight": 70,
#   "exercise_id": 1,
#   "duration": 60
# }

# sample url
# url : http://127.0.0.1:1363/calculate_calories




