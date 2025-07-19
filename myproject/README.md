# Nepali Food Nutrition Analyser (DalByte)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-4.2%2B-green?logo=django)](https://www.djangoproject.com/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

> **DalByte** is a full-stack AI-powered web application for tracking, analyzing, and visualizing food nutrition, with a focus on Nepali and Indian cuisine. Users can log meals, scan food using their camera for automatic detection and classification, set nutrition goals, track water intake, and view analytics. Admins have access to advanced analytics and user management.

---

## 🚀 Table of Contents

- [Features](#features)
- [Demo](#demo)
- [Getting Started](#getting-started)
- [Directory Structure](#directory-structure)
- [AI/ML Model Integration](#aiml-model-integration)
- [Main Data Models](#main-data-models)
- [API Endpoints](#api-endpoints)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

---

## ✨ Features

- **AI Food Detection & Classification**  
  Detect and classify food items from camera images using TensorFlow.js models in the browser.
- **Portion Estimation**  
  Estimate portion size based on object detection bounding box area.
- **Nutrition Tracking**  
  Log calories, protein, fat, carbs, and fiber for each meal.
- **User Goals**  
  Set and track daily nutrition and water intake goals.
- **Cheat Day Management**  
  Fun, animated cheat day selection and reward system, with admin override.
- **Admin Analytics Dashboard**  
  Pie charts, top user stats, and user tables for insights.
- **History & Filtering**  
  View and filter meal history by date and food type.
- **Modern UI**  
  Responsive, mobile-friendly design using Tailwind CSS.
- **Dockerized & Remote-Ready**  
  Easily run locally or expose securely via ngrok.

---

## 🖼️ Demo

<!-- Add screenshots or GIFs here -->

---

## ⚡ Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for TensorFlow.js model conversion, optional)
- Docker (optional, for containerized deployment)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shubarna-tech/Nepali-Food-Nutrition-Analyser.git
cd Nepali-Food-Nutrition-Analyser/myproject

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Create a superuser
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

#### (Optional) Use Docker
```bash
docker build -t dalbyte .
docker run -p 8000:8000 dalbyte
```

#### (Optional) Expose to the internet with ngrok
```bash
./ngrok http 8000
```

---

## 📁 Directory Structure

```text
myproject/
├── myapp/                # Main Django app (models, views, APIs, templates)
├── static/myapp/js/      # Frontend JavaScript (AI, UI logic)
├── templates/myapp/      # HTML templates (dashboard, scan, cheat day, etc.)
├── saved_model1/         # TensorFlow/TFLite models for classification
├── saved_model2/         # TensorFlow/TFLite models for detection
├── model_conversion/     # Scripts for converting PyTorch models to TF/TFLite/TF.js
├── requirements.txt      # Python dependencies
└── ...
```

---

## 🤖 AI/ML Model Integration

| Task              | Model Type         | Framework         | Location           |
|-------------------|-------------------|-------------------|--------------------|
| Object Detection  | TFLite/TF.js      | TensorFlow.js     | saved_model2/      |
| Classification    | TFLite/TF.js      | TensorFlow.js     | saved_model1/      |
| Model Conversion  | PyTorch → ONNX → TFLite/TF.js | PyTorch, ONNX, TensorFlow | model_conversion/ |

- **Portion Estimation:** Uses bounding box area to estimate portion and scale nutrition info.

---

## 🗃️ Main Data Models

| Model      | Description                                              |
|------------|---------------------------------------------------------|
| Nutrition  | Stores each meal log (user, food class, nutrition, timestamp) |
| Log        | Tracks user actions for analytics                       |
| UserGoal   | Stores per-user nutrition and water goals, cheat day info |
| WaterLog   | Tracks daily water intake                               |

---

## 🔗 API Endpoints

| Endpoint                | Method | Description                        |
|------------------------|--------|------------------------------------|
| `/api/logs/`           | GET    | Get user meal logs (auth required) |
| `/api/track/`          | POST   | Log a new meal                     |
| `/api/cheat-day/`      | GET/POST | Manage cheat day (user/admin)    |
| `/api/admin-analytics/`| GET    | Admin analytics data               |

---

## 📦 Dependencies

See [`requirements.txt`](requirements.txt) for the full list.

- Django
- djangorestframework
- PyJWT
- tensorflowjs
- opencv-python
- pillow
- torch (for model conversion)

---

## 📝 Usage

1. Register or log in.
2. Set your nutrition and water goals.
3. Use the scan page to detect and classify food via your camera.
4. Log meals and track your progress on the dashboard.
5. Enjoy cheat day features and view your history.
6. Admins can view analytics and manage users.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- TensorFlow.js
- Django REST Framework
- Tailwind CSS
- Nepali and Indian food datasets

---

## 📬 Contact

For questions or support, open an issue or contact the maintainer. 