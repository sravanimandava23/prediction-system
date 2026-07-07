from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib
import os
import traceback

app = Flask(__name__)

# ==========================================================
# STARTUP DEBUG
# ==========================================================
print("=" * 70)
print("🚀 RUNNING FLASK SERVER")
print("=" * 70)

print("📂 Current Working Directory:")
print(os.getcwd())

# ==========================================================
# MODEL PATH CHECK
# ==========================================================
model_path = os.path.abspath("college_model.pkl")
print("📦 Model Path:", model_path)

if not os.path.exists(model_path):
    print("❌ Model NOT Found!")
    exit()

print("✅ Model Exists")
print("📏 Model Size:", round(os.path.getsize(model_path) / (1024 * 1024), 2), "MB")

# ==========================================================
# LOAD MODEL
# ==========================================================
print("\n🔄 Loading Model...")

try:
    model = joblib.load(model_path)
    print("✅ Model Loaded Successfully")
except Exception as e:
    print("❌ Model Loading Failed")
    traceback.print_exc()
    exit()

# ==========================================================
# LOAD ENCODERS
# ==========================================================
print("\n🔄 Loading Encoders...")

try:
    category_encoder = joblib.load("category_encoder.pkl")
    gender_encoder = joblib.load("gender_encoder.pkl")
    branch_encoder = joblib.load("branch_encoder.pkl")
    college_encoder = joblib.load("college_encoder.pkl")

    print("✅ Encoders Loaded Successfully")

    print("📌 Category Classes:", list(category_encoder.classes_))
    print("📌 Gender Classes:", list(gender_encoder.classes_))
    print("📌 Branch Classes:", list(branch_encoder.classes_))
    print("📌 Total Colleges:", len(college_encoder.classes_))

except Exception as e:
    print("❌ Encoder Loading Failed")
    traceback.print_exc()
    exit()

print("=" * 70)
print("🎯 FLASK READY")
print("=" * 70)

# ==========================================================
# LOAD COLLEGE WEBSITE DATA
# ==========================================================
try:
    college_df = pd.read_csv("college_prediction_cleaned.csv.xls")

    website_map = dict(zip(
        college_df["NAME OF THE INSTITUTION"].astype(str).str.strip(),
        college_df["COLLEGE_Website"].astype(str).str.strip()
    ))

    print("✅ Website data loaded")
    print("📌 Total websites:", len(website_map))

except Exception as e:
    print("❌ Failed to load website data")
    traceback.print_exc()
    website_map = {}

# ==========================================================
# HOME PAGE
# ==========================================================
@app.route("/")
def home():
    print("\n🏠 HOME PAGE OPENED")
    return render_template("index.html")


# ==========================================================
# PREDICT API
# ==========================================================
@app.route("/predict", methods=["POST"])
def predict():

    try:
        print("\n" + "=" * 70)
        print("📥 NEW PREDICTION REQUEST")
        print("=" * 70)

        # ---------------- RAW DATA ----------------
        form_data = dict(request.form)
        print("📨 Raw Form Data:", form_data)

        # ---------------- INPUT FETCH ----------------
        name = request.form.get("name", "Unknown")
        rank = request.form.get("rank", "0")
        category = request.form.get("category")
        gender = request.form.get("gender")
        branch = request.form.get("branch")
        

        # Convert rank safely
        try:
            rank = int(rank)
        except:
            rank = 0

        print("\n📌 INPUT VALUES")
        print("Name     :", name)
        print("Rank     :", rank)
        print("Category :", category)
        print("Gender   :", gender)
        print("Branch   :", branch)

        # ---------------- VALIDATION ----------------
        if None in [category, gender, branch]:
            return jsonify({
                "error": "Missing form fields"
            }), 400

        # ---------------- ENCODING ----------------
        print("\n🔄 Encoding Inputs...")

        try:
            cat = category_encoder.transform([category])[0]
            gen = gender_encoder.transform([gender])[0]
            br = branch_encoder.transform([branch])[0]
        except Exception as e:
            print("❌ Encoding Error")
            traceback.print_exc()
            return jsonify({
                "error": "Invalid category/gender/branch value",
                "details": str(e)
            }), 400

        print("✅ Encoded Category:", cat)
        print("✅ Encoded Gender  :", gen)
        print("✅ Encoded Branch  :", br)

        # ---------------- INPUT DF ----------------
        input_data = pd.DataFrame(
            [[rank, cat, gen, br]],
            columns=["Rank", "Category", "Gender", "Branch"]
        )

        print("\n📊 Input DataFrame:")
        print(input_data)

        # ---------------- PREDICTION ----------------
        print("\n🤖 Running Model Prediction...")

        try:
            probs = model.predict_proba(input_data)[0]
            print("Number of probabilities:", len(probs))
            print("Number of colleges:", len(college_encoder.classes_))
            print("Top 10 probabilities:", sorted(probs, reverse=True)[:10])

        except Exception as e:
            print("❌ Model Prediction Failed")
            traceback.print_exc()
            return jsonify({
                "error": "Model prediction failed",
                "details": str(e)
            }), 500

        print("✅ Prediction Done")
        print("📊 Prob Sample:", probs[:5])

        # ---------------- RESULTS ----------------
        # ---------------- RESULTS ----------------
        colleges = college_encoder.classes_

        results = []

        for i in range(min(len(colleges), len(probs))):

                college_name = str(colleges[i]).strip()

                # Find matching row in CSV
                match = college_df[
                    college_df["NAME OF THE INSTITUTION"].astype(str).str.strip() == college_name
                ]

                if not match.empty:
                    website = str(match.iloc[0]["COLLEGE_Website"])
                else:
                    website = ""

                print(f"College : {college_name}")
                print(f"Website : {website}")

                results.append({
                    "college": college_name,
                    "probability": round(float(probs[i] * 100), 2),
                    "website": website
                })


        results.sort(key=lambda x: x["probability"], reverse=True)

        print("\n🏆 TOP 10 RESULTS")
        for i in range(min(10, len(results))):
            print(i + 1, results[i]["college"], results[i]["probability"], "%")

        print("=" * 70)
        print("📤 Returning JSON Response")
        print("=" * 70)

        return jsonify({
            "name": name,
            "results": results[:10]
        })

    except Exception as e:
        print("\n❌ UNEXPECTED ERROR")
        traceback.print_exc()

        return jsonify({
            "error": "Unexpected server error",
            "details": str(e)
        }), 500


# ==========================================================
# RUN APP
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)