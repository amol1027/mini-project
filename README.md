# 🎓 Student Resource Exchange (SRE)

A modern web platform built with Django that enables students to share, exchange, and discover educational resources within their community. From textbooks and study notes to tech gadgets, SRE connects students with what they need.

![Django](https://img.shields.io/badge/Django-5.1.6-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.x-38B2AC.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- 📚 **Easy Resource Exchange** - Post and discover educational resources with an intuitive interface
- 👥 **Community Driven** - Connect with students from your campus and beyond
- 🔒 **Secure & Free** - Your data is protected, completely free to use
- 🌍 **Global Reach** - Access resources from students worldwide
- 📅 **Borrow/Lend System** - Request items, set deadlines, and receive automatic reminders
- ⭐ **Review & Rating System** - Build trust through user ratings and reviews

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher (for Tailwind CSS)
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/student-resource-exchange.git
   cd student-resource-exchange
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tailwind CSS dependencies**
   ```bash
   python manage.py tailwind install
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Build Tailwind CSS**
   ```bash
   python manage.py tailwind build
   ```

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
mini project/
├── Student_Resource_Exchange/    # Main project settings
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Main URL configuration
│   └── wsgi.py                  # WSGI configuration
├── landing/                     # Landing page app
│   ├── templates/               # HTML templates
│   ├── views.py                 # View logic
│   └── urls.py                  # App URLs
├── theme/                       # Tailwind CSS theme
│   ├── static/                  # Compiled CSS
│   ├── static_src/              # Source files
│   │   ├── src/styles.css      # Tailwind source
│   │   └── tailwind.config.js  # Tailwind config
│   └── templates/base.html      # Base template
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
└── requirements.txt             # Python dependencies
```

## 🛠️ Development

### Running Tailwind in Watch Mode

For automatic CSS rebuilding during development:

```bash
python manage.py tailwind start
```

### Running Tests

```bash
python manage.py test
```

### Collecting Static Files

For production deployment:

```bash
python manage.py collectstatic
```

## 🎨 Design & UI/UX

The platform features a modern, professional design with:
- Responsive layouts for mobile and desktop
- Smooth animations and transitions
- Glass-morphism effects
- Accessible color contrasts
- Optimized touch targets for mobile

See [UI_UX_IMPROVEMENTS.md](UI_UX_IMPROVEMENTS.md) for detailed design documentation.

## 📚 Technology Stack

### Backend
- **Django 5.1.6** - Python web framework
- **SQLite** - Database (development)
- **Python 3.x** - Programming language

### Frontend
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **DaisyUI** - Tailwind CSS component library
- **Inter Font** - Typography

### Development Tools
- **django-tailwind** - Tailwind CSS integration for Django
- **django-browser-reload** - Auto-reload during development

## 🚀 Deployment

### Environment Variables

Create a `.env` file in the root directory:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=your-database-url
```

### Production Checklist

- [ ] Set `DEBUG = False` in settings.py
- [ ] Configure production database
- [ ] Set up proper `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up static files serving
- [ ] Configure HTTPS
- [ ] Set up logging
- [ ] Configure email backend
- [ ] Run security checks: `python manage.py check --deploy`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Write tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- Built by students, for students
- Inspired by the need for accessible educational resources
- Thanks to all contributors and testers

## 📞 Support

For support, email support@sre-platform.com or create an issue in the GitHub repository.

## 🗺️ Roadmap

- [ ] User authentication and profiles
- [ ] Advanced search and filtering
- [ ] Real-time chat between users
- [ ] Mobile app development
- [ ] Integration with university systems
- [ ] AI-powered resource recommendations
- [ ] Multi-language support

## 📊 Project Status

This project is currently in active development. Version 1.0 is expected to be released in Q1 2026.

---

**Made with ❤️ by the Student Resource Exchange Team**
