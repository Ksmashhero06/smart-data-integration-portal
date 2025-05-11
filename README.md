<!-- Smart Data Integration Portal -->
The Smart Data Integration Portal is a Flask-based web application for secure data management using a blockchain. It supports multiple user roles (Student, Faculty, Admin, Developer) with features like report submission, user management, audit logging, and blockchain attack simulations. Data persistence is achieved using JSON files (users.json, audit_logs.json, attack_results.json).

<!-- Features -->

<!-- User Roles: -->
Student: View blockchain records.
Faculty: Submit and update reports with smart contract validation.
Admin: Manage users and view audit logs.
Developer: Validate blockchain integrity, simulate attacks (tampering, hash collision, double-spending), and view quality metrics.


Blockchain: SHA-256-based chain for secure report storage.
Persistence: Users, audit logs, and attack results stored in users.json, audit_logs.json, and attack_results.json.
Security: User authentication with Flask-Login, audit logging for all actions.

<!-- Prerequisites -->

Python 3.9+
Git
Docker (optional, for containerized deployment)
Render account (for cloud deployment)
GitHub account

<!-- *Project Structure* -->
smart_data_integration_portal/
├── app.py                  # Main Flask application
├── blockchain.py           # Blockchain logic and attack simulations
├── audit_log.py            # Audit log management
├── utils.py                # Utility functions (e.g., hashing)
├── templates/              # HTML templates for dashboards
├── static/                 # CSS and JS files
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

<!-- Setup Instructions -->

<!-- Local Setup -->

<!-- Clone the Repository: -->
git clone https://github.com/your-username/smart-data-integration-portal.git
cd smart-data-integration-portal


<!-- Create Virtual Environment: -->
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows


<!-- Install Dependencies: -->
pip install -r requirements.txt


<!-- Run the Application: -->
python app.py


Access at http://localhost:5000.



<!-- Docker Setup -->

Build and Run:
docker compose up --build


Access at http://localhost:5000.
If port 5000 is blocked, update docker-compose.yml to use 5050:5000 and access http://localhost:5050.

<!-- Stop Containers: -->
docker compose down



<!-- Deployment to Render -->

<!-- Push to GitHub: -->

Create a repository on GitHub (smart-data-integration-portal).
Push your local project:git remote add origin https://github.com/your-username/smart-data-integration-portal.git
git branch -M main
git push -u origin main




<!-- Set Up Render: -->

Sign up at https://render.com and connect your GitHub account.
Create a Web Service, select your repository, and configure:
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn -w 4 -b 0.0.0.0:5000 app:app
Disk: Name: data, Mount Path: /app, Size: 1 GB


Deploy and access the provided URL (e.g., https://smart-data-integration-portal.onrender.com).


<!-- Verify Persistence: -->

Ensure users.json, audit_logs.json, and attack_results.json are stored in /app.



<!-- Usage -->

<!-- Default Users: -->

Student: student1 / pass123
Faculty: faculty1 / pass456
Admin: admin1 / pass789
Developer: developer1 / pass101

<!-- Key Actions: -->

Admin: Add/remove users (persisted in users.json).
Faculty: Submit reports to add blockchain blocks (minimum 2 for attack simulations).
Developer: Run attack simulations after adding blocks.
Student: View blockchain records.


<!-- Enable Attack Simulations: -->

Log in as faculty1, submit 2–3 reports (e.g., “Test report 1”).
Log in as developer1, run simulations (tampering, hash collision, double-spending).

<!-- Troubleshooting -->

<!-- Docker "Connection Refused": -->

Ensure Docker Desktop is running.

Check port 5000 availability:

netstat -a -n -o | findstr "5000"



Add firewall rule for port 5000.



Files Not Persisting:





Verify disk configuration in Render or volume mounting in Docker.



Check file permissions in /app.



Attack Simulations Fail:





Submit reports as faculty1 to add blocks.



Ensure blockchain.py returns dictionaries in simulate_attack.

Contributing





Fork the repository.



Create a feature branch (git checkout -b feature-name).



Commit changes (git commit -m "Add feature").



Push to the branch (git push origin feature-name).



Open a Pull Request.

License

MIT License. See LICENSE for details.

Contact

For issues, open a GitHub issue or contact the maintainer at [kkssathiyamoorthi@gmail.com].

