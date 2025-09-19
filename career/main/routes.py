from datetime import datetime, time
from mailbox import Message
from flask_cors import CORS
from flask import Response, abort, current_app, render_template, request, Blueprint, jsonify, send_file, send_from_directory, url_for
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from career.models import User 
import groq
import json
import json5
import os
import requests
from career import db, main, mail
from serpapi import GoogleSearch

main = Blueprint('main', __name__)

client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
SERPAPI_KEY1 = os.getenv("SERPAPI_KEY1")

@main.route("/")
@main.route("/home")
@login_required
def home():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template('home.html', title='', image_file=image_file)


COLLEGE_JSON_FILE = os.path.join(os.getcwd(), "static", "college.json")

@main.route("/college", methods=["GET"])
@login_required
def college():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template("college.html", title='College Recommendations', image_file=image_file)

@main.route("/course", methods=["GET"])
@login_required
def course():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template('course.html', title='Course', image_file=image_file)


@main.route("/onboarding")
@login_required
def onboarding():
    return render_template('onboarding.html')

react_build_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build")

@main.route("/data", methods=["GET"])
def get_data():
    # Ensure interests is a list
    interests = current_user.field_of_interest
    if isinstance(interests, str):
        # Split by comma if multiple interests are stored as string
        interests = [i.strip() for i in interests.split(',') if i.strip()]
    
    all_data = []

    for field in interests:
        ebooks = []
        courses = []

        # Fetch Ebooks
        try:
            ebook_resp = requests.get(
                f"https://www.googleapis.com/books/v1/volumes?q={field}&maxResults=5",
                timeout=5
            )
            ebook_resp.raise_for_status()
            ebook_data = ebook_resp.json()

            ebooks = [{
                "title": item["volumeInfo"].get("title", "Unknown Title"),
                "authors": item["volumeInfo"].get("authors", []),
                "link": item["volumeInfo"].get("previewLink", "#")
            } for item in ebook_data.get("items", [])]
        except Exception:
            ebooks = [{"title": "Failed to fetch ebooks", "authors": [], "link": "#"}]

        # Fetch Courses
        try:
            api_key = os.getenv(SERPAPI_KEY1)
            course_resp = requests.get(
                f"https://serpapi.com/search.json?q={field}+online+course&engine=google&api_key={api_key}&num=5",
                timeout=5
            )
            course_resp.raise_for_status()
            course_data = course_resp.json()

            courses = [{
                "title": item.get("title", "Unknown Course"),
                "link": item.get("link", "#"),
                "snippet": item.get("snippet", "")
            } for item in course_data.get("organic_results", [])]
        except Exception:
            courses = [{"title": "Failed to fetch courses", "link": "#", "snippet": ""}]

        all_data.append({
            "field_of_interest": field,
            "ebooks": ebooks,
            "courses": courses
        })

    return jsonify(all_data)

@main.route("/college.json")
@login_required
def college_json():
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'static'),
        'college.json'
    )

@main.route('/career.json')
def career_json():
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), '..', 'static'),
        'career.json'
    )


@main.route("/career_path", methods=["GET"])
@login_required
def career():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    # Call JSON generator every time page is loaded
    generate_career_json()
    return render_template("career.html", title='career path', image_file = image_file)

@main.route('/broadcast')
@login_required
def broadcast_email():
    if not current_user.is_admin:
        abort(403)

    recipients = get_all_emails()
    if not recipients:
        return "No users to send emails to."

    msg = Message('Broadcast Message',
                  sender=os.environ.get('EMAIL_USER'),
                  bcc=recipients)
    msg.body = 'This is an important update for all users.'

    mail.send(msg)
    return f"Emails sent to {len(recipients)} users!"

def get_all_emails():
    admin_email = os.environ.get('EMAIL_USER')
    users = User.query.all()
    return [user.email for user in users if user.email and user.email != admin_email]

LOCAL_FILE = "groq_responses.json"

def call_groq_sync(prompt, model="llama-3.1-8b-instant"):
    """
    Call the groq client in-process and return the final answer string.
    Reuses save_locally() to persist the prompt+answer like your streaming endpoint.
    """
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            # chunk structure may vary; try both attribute and dict access
            delta = None
            try:
                delta = chunk.choices[0].delta.content
            except Exception:
                try:
                    delta = chunk.choices[0].delta.get("content")
                except Exception:
                    delta = None

            if delta:
                answer += delta

        # persist same as your API endpoint
        try:
            save_locally(prompt, answer)
        except Exception:
            current_app.logger.exception("Failed to save groq response locally")

        return answer

    except Exception as e:
        current_app.logger.exception("Groq sync call failed")
        raise

@main.route("/api/groq", methods=["POST"])
def groq_api():
    data = request.get_json() or {}
    prompt = data.get("prompt", "Hello Groq AI!")

    try:
        answer = call_groq_sync(prompt)
        return jsonify({"prompt": prompt, "answer": answer})
    except Exception as e:
        current_app.logger.exception("groq_api error")
        return jsonify({"error": str(e)}), 500
    
def save_locally(prompt, answer):
    entry = {"prompt": prompt, "answer": answer, "createdAt": datetime.now().isoformat()}
    if not os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE, "w") as f:
            json.dump([], f)
    with open(LOCAL_FILE, "r") as f:
        data = json.load(f)
    data.append(entry)
    with open(LOCAL_FILE, "w") as f:
        json.dump(data, f, indent=2)

STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')
   
@main.route("/save_profile", methods=["POST"])
@login_required
def save_profile():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    # ✅ Update user in DB
    user = User.query.get(current_user.id)
    if user:
        user.age = data.get("age")
        user.qualification = data.get("stream")  # stream as qualification
        user.goal = data.get("goal")
        user.field_of_interest = ",".join(data.get("interests", []))
        user.preferred_location = data.get("studyLocation")
        db.session.commit()

    # ✅ Append to career.json
    career_file = os.path.join(os.path.dirname(__file__), "static", "user.json")

    if not os.path.exists(career_file):
        with open(career_file, "w") as f:
            json.dump([], f)  # create empty list

    with open(career_file, "r+") as f:
        try:
            careers = json.load(f)
        except json.JSONDecodeError:
            careers = []

        careers.append(data)
        f.seek(0)
        json.dump(careers, f, indent=2)

    return jsonify({"status": "success", "message": "Profile saved!"})

@main.route('/generate_career_json', methods=['POST'])
@login_required
def generate_career_json():
    try:
        # --- Safe handling of location/state ---
        location = current_user.preferred_location or "New Delhi"
        state = (current_user.preferred_location.split()[-1]
                 if current_user.preferred_location else "Delhi")

        # --- Build AI prompt ---
        prompt = f"""
You are an expert career counselor. Based on the following student profile, generate a personalized career path.

STUDENT PROFILE:
- Name: {current_user.username}
- Current Class: {getattr(current_user, 'current_class', 12)}
- Interests: {', '.join(getattr(current_user, 'field_of_interest', ['Finance', 'Economics']))}

REQUIREMENTS:
Return ONLY valid JSON in this format with no extra text, no explanations, no markdown:

{{
  "student": {{
    "name": "{current_user.username}",
    "current_class": {getattr(current_user, 'current_class', 12)},
    "interests": {json.dumps(getattr(current_user, 'field_of_interest', ['Finance', 'Economics']))}
  }},
  "career_path": {{
    "undergraduate_degree": ["<degree1>", "<degree2>"],
    "relevant_courses": ["<course1>", "<course2>", "..."],
    "skills": ["<skill1>", "<skill2>", "..."],
    "internships_and_experience": ["<exp1>", "<exp2>", "..."],
    "certifications": ["<cert1>", "<cert2>", "..."],
    "future_roles": ["<role1>", "<role2>", "..."]
  }}
}}
Do not include any text outside JSON.
        """

        # --- Call Groq directly ---
        try:
            answer = call_groq_sync(prompt)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Groq call failed: {e}"}), 500

        # --- Clean JSON string (remove accidental markdown fences) ---
        inner_json_str = answer.strip()
        if inner_json_str.startswith("```"):
            inner_json_str = inner_json_str.strip("`")
            inner_json_str = inner_json_str.replace("json", "", 1).strip()

        # --- Parse JSON safely ---
        try:
            parsed = json.loads(inner_json_str)
        except json.JSONDecodeError:
            try:
                parsed = json5.loads(inner_json_str)  # more forgiving parser
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid JSON from AI (after repair attempt): {str(e)}",
                    "raw": inner_json_str
                }), 500

        # --- File path for storage ---
        file_path = os.path.join(current_app.static_folder, "career1.json")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
        # --- Load existing file ---
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    all_data = json.load(f)
                except json.JSONDecodeError:
                    all_data = []
        else:
            all_data = []

        if not isinstance(all_data, list):
            all_data = []

        # --- Update or create entry for current user ---
        user_entry = next((u for u in all_data if u.get("user_id") == current_user.id), None)

        if user_entry:
            if "career" not in user_entry or not isinstance(user_entry["career"], list):
                user_entry["career"] = []
            user_entry["career"].append(parsed)
        else:
            all_data.append({
                "user_id": current_user.id,
                "username": current_user.username,
                "career": [parsed]
            })

        # --- Save updated data back ---
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "message": "Career JSON updated successfully!"})

    except Exception as e:
        current_app.logger.exception("generate_career_json failed")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@main.route('/generate_college_json', methods=['POST'])
@login_required
def generate_college_json():        
    try:
        # --- Safe handling of location/state ---
        location = current_user.preferred_location or "New Delhi"
        state = (current_user.preferred_location.split()[-1]
                 if current_user.preferred_location else "Delhi")

        # --- Build AI prompt ---
        prompt = f"""
        You are an expert career and education advisor. Based on the following student profile, generate a detailed comparison of engineering colleges in {location}, {state}.

STUDENT PROFILE:
- Academic Stream/Field: {current_user.qualification}
- Preferred City: {location}
- Preferred State: {state}
- Budget Range: No budget constraint
- Qualifications: {current_user.qualification}
- Field_of_Interest: {current_user.field_of_interest}
- Top Priority: {current_user.goal}
- Additional Requirement: Strong culture

REQUIREMENTS:
Return ONLY valid JSON. The JSON should be an array of colleges with the following format for each college:

[
  {{
    "collegeName": "<College Name>",
    "location": "<City, State>",
    "jamesScoreCutoff": "<JEE Mains cutoff score range>",
    "placementPercentage": "<Placement %>",
    "culturalEvents": "<Major cultural events>",
    "fees": "<Approximate fees>",
    "specialisations": "<Key fields of study or specialisations>"
  }},
  ...
]

Do NOT include any extra text, explanations, or markdown. Return strictly JSON.
        """

        # --- Call Groq directly ---
        try:
            answer = call_groq_sync(prompt)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Groq call failed: {e}"}), 500

        # --- Clean JSON string (remove accidental markdown fences) ---
        inner_json_str = answer.strip()
        if inner_json_str.startswith("```"):
            inner_json_str = inner_json_str.strip("`")
            inner_json_str = inner_json_str.replace("json", "", 1).strip()

        file_path = os.path.join(current_app.static_folder, "college.json")
        # --- Parse JSON safely ---
        try:
            parsed = json5.loads(inner_json_str)
        except json5.JSONDecodeError as e:
            return jsonify({        
        "status": "error",
        "message": f"Invalid JSON5 from AI: {str(e)}",
        "raw": inner_json_str
            }), 500
        # --- Load existing file ---
        if os.path.exists(file_path):       
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    all_data = json5.load(f)
                except json5.JSONDecodeError:
                    all_data = []
        else:
            all_data = []

        # --- File path for storage ---
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

        if not isinstance(all_data, list):
            all_data = []

        # --- Update or create entry for current user ---
        user_entry = next((u for u in all_data if u.get("user_id") == current_user.id), None)

        if user_entry:
            if "college" not in user_entry or not isinstance(user_entry["college"], list):
                user_entry["college"] = []
            user_entry["college"].append(parsed)
        else:
            all_data.append({
                "user_id": current_user.id,
                "username": current_user.username,
                "college": [parsed]
            })

        # --- Save updated data back ---
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "message": "College JSON updated successfully!"})

    except Exception as e:
        current_app.logger.exception("generate_college_json failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@main.route("/compare", methods=["GET"])
@login_required
def compare():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template("comparison.html", title='Degree comparisons', image_file=image_file)

@main.route('/compare_careers', methods=['POST'])
@login_required
def compare_careers():
    try:
        data = request.get_json()
        career1 = data.get("career1")
        career2 = data.get("career2")

        if not career1 or not career2:
            return jsonify({"status": "error", "message": "Both career1 and career2 are required"}), 400

        # --- Build AI prompt ---
        prompt = f"""
You are an expert career counselor. Compare the following two career paths:

CAREERS TO COMPARE:
1. {career1}
2. {career2}

REQUIREMENTS:
Return ONLY valid JSON in this format with no extra text, no explanations, no markdown:

{{
  "comparison": {{
    "career1": "{career1}",
    "career2": "{career2}",
    "duration_of_study": {{
      "{career1}": "<text>",
      "{career2}": "<text>"
    }},
    "entrance_exams": {{
      "{career1}": ["<exam1>", "<exam2>"],
      "{career2}": ["<exam1>", "<exam2>"]
    }},
    "skills_required": {{
      "{career1}": ["<skill1>", "<skill2>"],
      "{career2}": ["<skill1>", "<skill2>"]
    }},
    "common_job_roles": {{
      "{career1}": ["<role1>", "<role2>"],
      "{career2}": ["<role1>", "<role2>"]
    }},
    "average_salary_india": {{
      "{career1}": "<range>",
      "{career2}": "<range>"
    }},
    "higher_education_opportunities": {{
      "{career1}": ["<option1>", "<option2>"],
      "{career2}": ["<option1>", "<option2>"]
    }},
    "future_scope": {{
      "{career1}": "<text>",
      "{career2}": "<text>"
    }}
  }}
}}
Do not include any text outside JSON.
        """

        # --- Call Groq directly ---
        try:
            answer = call_groq_sync(prompt)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Groq call failed: {e}"}), 500

        # --- Clean JSON string (remove accidental markdown fences) ---
        inner_json_str = answer.strip()
        if inner_json_str.startswith("```"):
            inner_json_str = inner_json_str.strip("`")
            inner_json_str = inner_json_str.replace("json", "", 1).strip()

        # --- Parse JSON safely ---
        try:
            parsed = json.loads(inner_json_str)
        except json.JSONDecodeError:
            try:
                parsed = json5.loads(inner_json_str)  # more forgiving parser
            except Exception as e:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid JSON from AI (after repair attempt): {str(e)}",
                    "raw": inner_json_str
                }), 500

        # --- (Optional) Save to file like you did for career JSON ---
        file_path = os.path.join(current_app.static_folder, "career_comparisons.json")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    all_data = json.load(f)
                except json.JSONDecodeError:
                    all_data = []
        else:
            all_data = []

        if not isinstance(all_data, list):
            all_data = []

        # --- Store comparison result ---
        all_data.append({
            "user_id": current_user.id,
            "username": current_user.username,
            "career1": career1,
            "career2": career2,
            "comparison": parsed
        })

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)

        return jsonify({"status": "success", "comparison": parsed})

    except Exception as e:
        current_app.logger.exception("compare_careers failed")
        return jsonify({"status": "error", "message": str(e)}), 500


def call_groq_sync2(prompt, model="llama-3.1-8b-instant"):
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True
        )
        answer = ""
        for chunk in completion:
            delta = None
            try:
                delta = chunk.choices[0].delta.content
            except Exception:
                try:
                    delta = chunk.choices[0].delta.get("content")
                except Exception:
                    delta = None

            if delta:
                answer += delta

        return answer

    except Exception as e:
        print(f"Groq API call failed: {e}")
        return "Sorry, kuch problem ho gayi."

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('message')
    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    response = call_groq_sync2(prompt)
    return jsonify({"response": response})

# ✅ Saare exams list
ALL_EXAMS = [
    "UPSC Civil Services","SSC CGL","SSC CHSL","IBPS PO","IBPS Clerk",
    "SBI PO","SBI Clerk","RBI Grade B","RBI Assistant","NABARD Grade A",
    "CAT","XAT","MAT","CMAT","IIFT","SNAP","NMAT",
    "JEE Main","JEE Advanced","BITSAT","VITEEE",
    "NEET UG","AIIMS MBBS","JIPMER",
    "GATE","IES","ISRO Scientist Exam","DRDO Scientist Exam",
    "CLAT","AILET","LSAT India",
    "CUET UG","CUET PG","NET (UGC-NET)","CSIR NET",
    "NDA","CDS","AFCAT","Indian Navy Exam","Indian Airforce Exam",
    "State PSC (e.g., UPPSC, MPPSC)",
    "Railway RRB NTPC","Railway RRB Group D","Railway ALP","Railway JE",
    "LIC AAO","LIC ADO","NIACL AO","RRB PO","RRB Clerk","MHT CET","KCET","WBJEE","COMETK"
]

def serpapi_search(query):
    """Fetch results from SerpAPI"""
    try:
        search = GoogleSearch({
            "q": query,
            "hl": "en",
            "api_key": SERPAPI_KEY
        })
        return search.get_dict()
    except Exception as e:
        print("SerpAPI error:", e)
        return None


@main.route("/prep")
def prep():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template("prep.html", title='Preparation', image_file=image_file)


@main.route("/get_data_prep", methods = ['GET'])
def get_data_prep():
    exam = request.args.get("exam", "")
    if not exam or exam not in ALL_EXAMS:
        return jsonify({"error": "Invalid or missing exam"}), 400

    # ✅ Queries
    notes_query = f"{exam} preparation notes ebooks pdf"
    courses_query = f"{exam} online course site:coursera.org OR site:udemy.com OR site:edx.org"

    print(f"Fetching for exam: {exam}")

    # ✅ Notes
    notes_results = serpapi_search(notes_query)
    ebooks = []
    if notes_results and "organic_results" in notes_results:
        for r in notes_results["organic_results"][:6]:
            ebooks.append({
                "title": r.get("title", "Untitled"),
                "link": r.get("link", "#")
            })
    else:
        ebooks = [{"title": "Sample Notes", "link": "#"}]  # fallback

    # ✅ Courses
    courses_results = serpapi_search(courses_query)
    courses = []
    if courses_results and "organic_results" in courses_results:
        for r in courses_results["organic_results"][:6]:
            courses.append({
                "title": r.get("title", "Untitled"),
                "snippet": r.get("snippet", "No description"),
                "link": r.get("link", "#")
            })
    else:
        courses = [{"title": "Sample Course", "snippet": "Demo description", "link": "#"}]  # fallback

    return jsonify({"exam": exam, "ebooks": ebooks, "courses": courses})