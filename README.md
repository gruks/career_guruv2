# 🎓 CareerGuru — AI-Powered Career Guidance Platform

**Live Demo:** [career-guruv2-3.onrender.com/home](https://career-guruv2-3.onrender.com/home)

CareerGuru is an **AI-driven career guidance platform** built to help students discover the right career paths, prepare effectively, and make informed education decisions.  
It combines smart recommendations, degree comparisons, and free study resources — all powered by **Flask**, **PostgreSQL**, and advanced **AI APIs**.

---

## 🌟 Features

### 🧭 Personalized Career Guidance
- AI-powered recommendations based on students’ interests, academic background, and goals.  
- Insights on suitable degree programs, potential job roles, and career growth paths.

### 🧠 Smart Career Prep
- AI tools to help students prepare for their chosen fields.
- Tailored advice, resource links, and preparation roadmaps.

### ⚖️ Degree Comparison
- Compare multiple degrees or career options side-by-side.
- Get detailed insights on curriculum, job prospects, and salary expectations.

### 📚 Free Study Resources
- Curated open-source learning materials, books, and online courses.  
- Helps students upskill without expensive tuition fees.

### 🤖 Powered by AI
- **Groq API:** Delivers intelligent, fast responses for career and learning recommendations.  
- **Serp API:** Fetches real-time educational and career data from the web.

---

## 🧩 Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Flask (Python) |
| **Database** | PostgreSQL |
| **Authentication** | JWT (JSON Web Tokens) |
| **APIs Used** | Groq API, Serp API |
| **Deployment** | Render |

---

## 🔐 Authentication

CareerGuru uses **JWT-based authentication** to ensure secure login and data access for users.  
Students can register, sign in, and maintain personalized data safely.

---

## 🚀 Deployment

The website is fully deployed on **Render** for fast, reliable, and scalable hosting.

**Live Site:**  
👉 [https://career-guruv2-3.onrender.com/home](https://career-guruv2-3.onrender.com/home)

---

## 🛠️ Installation (For Local Setup)

If you want to run the project locally:

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/career-guru.git
cd career-guru

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
# Example (.env file)
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/career_guru
JWT_SECRET_KEY=your_secret_key
GROQ_API_KEY=your_groq_key
SERP_API_KEY=your_serp_key

# 5. Run the Flask app
flask run
