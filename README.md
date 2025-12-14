# CareerGuru — AI-Powered Career Guidance Platform

**Live Demo:** [career-guruv2-3.onrender.com/home](https://career-guruv2-3.onrender.com/home)

CareerGuru is a comprehensive AI-driven career guidance platform designed to empower students in discovering optimal career paths, preparing effectively for their chosen fields, and making informed educational decisions. The platform integrates intelligent recommendation systems, detailed degree comparisons, and curated free study resources, all powered by a robust technology stack including Flask, PostgreSQL, and advanced AI APIs.

## Table of Contents
- [Features](#features)
- [Technical Architecture](#technical-architecture)
- [Authentication](#authentication)
- [API Integrations](#api-integrations)
- [Deployment](#deployment)
- [Local Installation](#local-installation)
- [Contributing](#contributing)
- [License](#license)

## Features

### Personalized Career Guidance
CareerGuru leverages advanced AI algorithms to deliver highly personalized career recommendations based on:
- Students' academic background and performance
- Personal interests and aptitude assessments
- Long-term career goals and preferences
- Market demand and emerging industry trends

Users receive detailed insights including suitable degree programs, potential job roles, expected salary ranges, and comprehensive career growth trajectories.

### Smart Career Preparation Tools
The platform provides specialized preparation resources tailored to each user's selected career path:
- Customized study roadmaps and preparation timelines
- Targeted skill development recommendations
- Practice resources and assessment tools
- Direct links to relevant learning materials

### Advanced Degree Comparison
Students can perform side-by-side comparisons of multiple degree programs and career options, gaining insights into:
- Curriculum structure and course requirements
- Duration, cost, and entry requirements
- Job placement rates and alumni success metrics
- Salary expectations and career progression opportunities

### Curated Free Study Resources
Access a comprehensive library of free, high-quality learning materials including:
- Open-source textbooks and academic papers
- MOOC courses from leading universities
- Interactive tutorials and video lectures
- Practice exams and certification prep materials

## Technical Architecture

| Layer | Technologies | Purpose |
|-------|--------------|---------|
| **Frontend** | HTML5, CSS3, JavaScript | Responsive user interface and dynamic content rendering |
| **Backend** | Flask (Python 3.9+) | RESTful API development and business logic |
| **Database** | PostgreSQL 15+ | User data, career profiles, and recommendation storage |
| **Authentication** | JWT (JSON Web Tokens) | Secure user session management |
| **AI/ML APIs** | Groq API, Serp API | Intelligent recommendations and real-time data |
| **Deployment** | Render | Production hosting and auto-scaling |
| **Version Control** | Git/GitHub | Source code management |

## Authentication

CareerGuru implements secure JWT-based authentication with the following features:
- Secure user registration and password hashing (bcrypt)
- Token-based session management with automatic refresh
- Role-based access control
- Password reset functionality via email
- Session timeout and security headers

All user data is encrypted and protected according to industry best practices.

## API Integrations

### Groq API
Provides lightning-fast AI inference for:
- Career path recommendations
- Personalized learning suggestions
- Natural language processing of user inputs
- Real-time career advice generation

### Serp API
Enables real-time web data extraction for:
- Current job market trends
- Educational program details
- Salary and employment statistics
- Industry news and developments

## Deployment

The platform is deployed on Render with zero-downtime deployments and automatic scaling.

**Production URL:**  
[https://career-guruv2-3.onrender.com/home](https://career-guruv2-3.onrender.com/home)

## Local Installation

Follow these steps to set up CareerGuru locally:


```bash
1. **Clone the repository**
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
```
The application will be available at `http://localhost:5000`.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
