# ==========================================================
# IMPORTS
# ==========================================================
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# ==========================================================
# LOAD DATA
# ==========================================================
import pandas as pd

df = pd.read_csv("college_prediction_cleaned.csv.xls")

print("✅ CSV file created successfully")
rank_columns = [
    'OC_BOYS','OC_GIRLS',
    'SC_BOYS','SC_GIRLS',
    'ST_BOYS','ST_GIRLS',
    'BCA_BOYS','BCA_GIRLS',
    'BCB_BOYS','BCB_GIRLS',
    'BCC_BOYS','BCC_GIRLS',
    'BCD_BOYS','BCD_GIRLS',
    'BCE_BOYS','BCE_GIRLS',
    'OC_EWS_BOYS','OC_EWS_GIRLS'
]

# ==========================================================
# TRANSFORM DATA
# ==========================================================
rows = []

for _, row in df.iterrows():
    for col in rank_columns:
        rank = row[col]

        if pd.notna(rank) and rank > 0:
            category, gender = col.rsplit('_', 1)

            rows.append([
                rank,
                category,
                gender,
                row['branch_code'],
                row['NAME OF THE INSTITUTION'],
                row['COLLEGE_Website']
            ])

ml_df = pd.DataFrame(rows, columns=[
    'Rank', 'Category', 'Gender', 'Branch', 'College','Website'
])

# ==========================================================
# ENCODING
# ==========================================================
category_encoder = LabelEncoder()
gender_encoder = LabelEncoder()
branch_encoder = LabelEncoder()
college_encoder = LabelEncoder()


ml_df['Category'] = category_encoder.fit_transform(ml_df['Category'])
ml_df['Gender'] = gender_encoder.fit_transform(ml_df['Gender'])
ml_df['Branch'] = branch_encoder.fit_transform(ml_df['Branch'])
ml_df['College'] = college_encoder.fit_transform(ml_df['College'])

# ==========================================================
# TRAIN TEST SPLIT
# ==========================================================
X = ml_df[['Rank', 'Category', 'Gender', 'Branch']]
y = ml_df['College']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ==========================================================
# MODEL TRAINING
# ==========================================================
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

print("✅ Model Training Completed")

# ==========================================================
# SAVE MODEL + ENCODERS
# ==========================================================
print("\n💾 Saving model and encoders...")

joblib.dump(model, "college_model.pkl", compress=3)
joblib.dump(category_encoder, "category_encoder.pkl")
joblib.dump(gender_encoder, "gender_encoder.pkl")
joblib.dump(branch_encoder, "branch_encoder.pkl")
joblib.dump(college_encoder, "college_encoder.pkl")


print("✅ All files saved successfully!")
# ==========================================================
# LOAD COLLEGE WEBSITE DATA
# ==========================================================
college_data = pd.read_csv("college_prediction_cleaned.csv.xls")

# Keep only College Name and Website
college_data = college_data[
    ["NAME OF THE INSTITUTION", "COLLEGE_Website"]
].drop_duplicates()

# Create a dictionary: College Name -> Website
website_map = dict(zip(
    college_data["NAME OF THE INSTITUTION"],
    college_data["COLLEGE_Website"]
))