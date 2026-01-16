# BulkMail Pilot ✈️

A responsive, full-stack web application for automated bulk email sending with attachments. Designed to streamline communication campaigns with personalization and real-time tracking.

## 🚀 Features

- **📊 Dashboard**: Real-time sending statistics, success rates, and activity logs.
- **✍️ Compose**: Rich HTML email support, file attachments, and `{Name}` personalization.
- **👥 Recipients**: Bulk import from CSV/Excel or manage the recipient list manually.
- **📝 Templates**: Save and load reusable email templates for consistent messaging.
- **🌙 UI/UX**: Responsive design built with Vanilla JS and CSS (includes Dark Mode).

## 🛠️ Tech Stack

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Vanilla JavaScript

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BulkMail_Pilot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file in the root directory (if applicable) to configure your SMTP settings:
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

## 🏃 Usage

1. **Run the application**
   ```bash
   python app.py
   ```

2. **Open in Browser**
   Navigate to `http://127.0.0.1:5000` in your web browser.

3. **Workflow**
   - Go to **Recipients** to upload your CSV/Excel list.
   - Navigate to **Compose** to draft your email. Use `{Name}` to insert the recipient's name dynamically.
   - Attach files if needed and click **Send**.
   - Monitor progress on the **Dashboard**.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.
