# import pandas as pd
# import numpy as np
# from sklearn.linear_model import LinearRegression

# file_path = "exercise_dataset_revised.xlsx"
# df = pd.read_excel(file_path)

# def lbs_to_kg(weight_lbs):
#     return weight_lbs * 0.453592

# weights_lbs = [col for col in df.columns if 'lb' in col]
# weights_kg = lbs_to_kg(np.array([int(weight.split(' ')[0]) for weight in weights_lbs]))


# X = weights_kg.reshape(-1, 1)

# model = LinearRegression()

# average_calories_per_minute_per_kg = []

# for exercise in df.index:
#     y = df.loc[exercise, weights_lbs].values.flatten()
#     if len(y) == 0:
#         average_calories_per_minute_per_kg.append(np.nan)
#         continue
#     model.fit(X, y)
#     average_calories_per_minute_per_kg.append(model.coef_[0] / 60)

# df['Average Calories per Minute per Kg'] = average_calories_per_minute_per_kg

# output_file_path = "exercise_dataset_revised.xlsx"
# df.to_excel(output_file_path, index=False)

# print(f"Updated Excel file saved to {output_file_path}")
