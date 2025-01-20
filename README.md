
# SmartCaretaker WhatsApp Chatbot 

**SmartCaretaker** is a cutting-edge chatbot designed to streamline property management tasks through WhatsApp. It leverages Twilio's WhatsApp API and Django's robust backend capabilities to provide seamless communication and efficient operations.

---

## 🛠️ Features

- **Automated Responses**: Provides instant replies to user inquiries.
- **Dynamic Conversation Handling**: Tailors responses based on user queries.
- **WhatsApp Integration**: Uses Twilio's API for secure messaging.
- **User Inquiry Management**: Tracks and stores user inquiries for better service delivery.
- **Django-Powered Backend**: Ensures scalability and efficiency.

---

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### Prerequisites
- Python 3.8+
- Django 4.x
- Twilio Account with WhatsApp API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Mashon8945/SmartCaretaker-WhatsApp-Chatbot.git
   cd SmartCaretaker-WhatsApp-Chatbot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory and add the following:
   ```env
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_whatsapp_phone_number
   ```

### Running the Application

1. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

3. Set up the webhook URL in your Twilio account:
   ```
   http://<your-domain>/whatsapp-webhook/
   ```

---

## 📂 Project Structure

```plaintext
SmartCaretaker-WhatsApp-Chatbot/
├── chatbot/             # Core chatbot application
├── templates/           # HTML templates for frontend
├── static/              # Static files (CSS, JS, etc.)
├── manage.py            # Django project entry point
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```


## 🤝 Contributing

Contributions are welcome! To contribute:
1. Fork this repository.
2. Create a new branch for your feature/bug fix.
3. Commit your changes and push to your branch.
4. Open a pull request for review.


## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.


## 💡 Acknowledgements

- **Django**: High-level Python web framework.
- **Twilio**: For WhatsApp API integration.
- **OpenAI**: AI capabilities for smarter conversations.

---

## 📬 Contact

Have questions or suggestions? Feel free to reach out:
- **Email**: [Leonardlemashon@gmail.com](mailto:Leonardlemashon@gmail.com)
- **GitHub**: [Mashon8945](https://github.com/Mashon8945)

