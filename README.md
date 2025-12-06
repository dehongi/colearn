# CoLearn

CoLearn is a collaborative online learning platform designed to function like a "pedia" (e.g., Wikipedia) specifically for professional courses and learning materials. It connects subject matter experts (Instructors) who create content with users (Learners) who consume it, provide feedback, suggest improvements, and propose new topics.

## Problem Solved

Traditional online courses are often static, with limited avenues for learners to easily contribute feedback or influence content evolution directly within the learning environment. CoLearn aims to create a more dynamic ecosystem where courses are continuously refined based on expert knowledge *and* structured community input.

## Target Users & Roles

1. **Instructors (Creators):** Professionals, educators, or experts in specific fields.
   - Actions: Create courses (including text, video, quizzes, documents), upload learning materials, define course structure, review learner suggestions, approve/reject suggested edits or additions, manage course versions, potentially respond in discussion areas.

2. **Learners (Students/Users):** Professionals, students, or individuals seeking to learn new skills or knowledge.
   - Actions: Browse, search, and enroll in courses; consume course content; rate and review courses; **suggest specific edits or improvements** to course content (e.g., clarifying a paragraph, suggesting a better example, pointing out an error); **propose new course topics** or modules; participate in discussions related to the course content.

## Key Features

- Course creation interface for Instructors
- Course catalog: Browse, searching, and enrollment for Learners
- Learning interface (video player, text reader, quiz engine)
- Integrated suggestion system within the course content view
- Dashboard for Instructors to review and manage suggestions
- Rating, review, and discussion forum capabilities per course
- User profiles (Instructors and Learners)
- Mechanism for proposing and potentially upvoting new course topics

## Technical Implementation

- **Backend Framework:** Django 5.2
- **Frontend Rendering:** Server-Side Rendering using Django Templates
- **UI Framework:** Bootstrap 5.3 (manually included)
- **Icons:** Bootstrap Icons (manually included)
- **Database:** SQLite (default, can be configured for production)
- **Third-Party Packages:** imagekit, django-cleanup, Markdown, Pillow, etc.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd colearn
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Open your browser and go to `http://127.0.0.1:8000/`

## Usage

- **Instructors:** Register as an instructor, create courses, upload materials, and manage suggestions.
- **Learners:** Browse courses, enroll, consume content, and submit suggestions for improvements.

## Project Structure

- `accounts/`: User authentication and profiles
- `courses/`: Course management, lessons, modules
- `social/`: Discussion forums and user activities
- `website/`: Static pages (home, about, contact, etc.)
- `templates/`: Django templates
- `static/`: Static files (CSS, JS, images)

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Context

- **Current Date:** April 30, 2025
- **Location Context:** United Arab Emirates
- **Target Audience:** Global
- **Initial Language Support:** English only
