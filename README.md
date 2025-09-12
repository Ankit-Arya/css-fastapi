# FastAPI Project

A simple FastAPI project with a clean structure for scalability and maintainability.

---

## 📂 Project Structure

```bash
├── main.py              # Entry point of the application
├── services/            # Business logic and reusable functions
│   └── example_service.py
├── models/              # Pydantic request/response models
│   └── request_models.py
├── env/                 # Virtual environment (ignored in git)
└── __pycache__/         # Python cache (ignored in git)

```bash

### 🔹 `main.py`
- The application entry point.  
- Initializes FastAPI, includes routes, and runs the server.  

### 🔹 `services/`
- Contains service functions and business logic.  
- Keeps routes/controllers clean by separating core logic.  

### 🔹 `models/`
- Defines **Pydantic models** for request and response validation.  
- Example: `UserRequest`, `UserResponse`.

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>


### 🔹 `main.py`
- The application entry point.  
- Initializes FastAPI, includes routes, and runs the server.  

### 🔹 `services/`
- Contains service functions and business logic.  
- Keeps routes/controllers clean by separating core logic.  

### 🔹 `models/`
- Defines **Pydantic models** for request and response validation.  
- Example: `UserRequest`, `UserResponse`.

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>

2. Create and activate virtual environment
   python -m venv env
   source env/bin/activate   # On macOS/Linux
   env\Scripts\activate      # On Windows

3. Install dependencies
   pip install fastapi uvicorn

4. Run the server
   uvicorn main:app --reload
   The app will be available at:
  👉 http://127.0.0.1:8000

5. Interactive API Docs
   Swagger UI: http://127.0.0.1:8000/docs
   ReDoc: http://127.0.0.1:8000/redoc


   
   

