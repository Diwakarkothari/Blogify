# Operational Value - Multi-Platform Blogging Assistant

Operational Value is a Flask-based web application designed to streamline content creation and publishing across multiple blogging platforms like **Medium**, **Dev.to**, and **Hashnode**. With AI-generated content support using **Google's Gemini API**, users can create, edit, and publish blog posts with ease.

---

## 🚀 Features

- ✍️ **AI-Powered Blog Generation** – Generate full blog posts using Google's Gemini AI.
- 📤 **Multi-Platform Upload** – Publish markdown files or AI-generated content to:
  - Medium
  - Dev.to
  - Hashnode
- 📝 **Post Editing** – Modify AI-generated articles before publishing.
- 🔐 **User Authentication** – Register/login system with session management.
- ⚙️ **Token-Based Platform Integration** – Securely store and manage user API tokens.
- 🌐 **Responsive UI** – Built with Flask-WTF and clean HTML templates.

---

## 🧠 Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, Flask-WTF (WTForms)
- **AI Integration**: Google Generative AI (Gemini 1.5 Flash)
- **APIs Used**: Medium, Dev.to, Hashnode GraphQL
- **Storage**: JSON (for simplicity and demonstration)
- **Deployment**: Docker

---

## ⚙️ Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your-username/operational-value.git
cd operational-value
