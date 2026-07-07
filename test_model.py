import joblib

print("Loading model...")

model = joblib.load("college_model.pkl")

print("SUCCESS!")
print(type(model))
print("Number of Trees:", len(model.estimators_))