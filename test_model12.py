import joblib
import gc

print("Running garbage collection...")
gc.collect()

print("Loading model...")
model = joblib.load("college_model.pkl")

print("SUCCESS!")
print(type(model))
print("Trees:", len(model.estimators_))