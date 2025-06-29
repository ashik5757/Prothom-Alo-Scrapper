# Prothom Alo Scrapper

A comprehensive web scraping system for monitoring and extracting news articles from Prothom Alo website. The system consists of a Django REST API backend with Celery for scheduled scraping tasks, Elasticsearch for search functionality, and a Next.js frontend for user interaction.

## 🏗️ Architecture

- **Backend**: Django REST API with Celery for background tasks
- **Frontend**: Next.js with Ant Design components
- **Database**: MySQL for application data
- **Search Engine**: Elasticsearch for article indexing and search
- **Cache/Queue**: Redis for Celery task queue
- **Web Scraping**: Selenium with Chrome/Chromium for dynamic content extraction

## 📋 Features

### Backend Features
- RESTful API for managing scraping tasks
- Scheduled scraping with Celery Beat
- Elasticsearch integration for advanced search
- Content filtering and search capabilities
- Task management (create, update, delete, view)
- Automatic task scheduling and execution

### Frontend Features
- Dark theme interface
- Task management dashboard
- Advanced search and filtering
- Real-time content viewing
- Task editing capabilities
- Generic search across all categories

### Scraping Features
- Category-based article scraping
- Dynamic content loading with infinite scroll
- Article details extraction (title, author, location, content, publish time)
- Duplicate prevention
- Configurable scraping limits and schedules

## 🚀 Quick Start with Docker

### Prerequisites

- Docker
- Docker Compose
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Prothom Alo Scrapper"
   ```

2. **Set up environment variables**
   ```bash
   cd backend
   cp .env.example .env
   ```
   
   Edit the `.env` file with your preferred configurations:
   ```env
   # Django Settings
   DEBUG=True
   DJANGO_SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

   # Database
   DB_NAME=prothom_alo_scrapper
   DB_USER=django_api
   DB_PASSWORD=1234
   DB_HOST=db
   DB_PORT=3306

   # Redis
   REDIS_HOST=redis
   REDIS_PORT=6379

   # Celery
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/0

   # Elasticsearch
   ELASTICSEARCH_HOST=elasticsearch
   ELASTICSEARCH_PORT=9200

   WEB_PORT=8000

   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

3. **Start the backend services**
   ```bash
   cd backend
   docker-compose up -d
   ```

4. **Start the frontend**
   ```bash
   cd ../frontend
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs/

## 🛠️ Development Setup

### Backend Development

1. **Start backend services**
   ```bash
   cd backend
   docker-compose up -d
   ```

2. **Check service health**
   ```bash
   docker-compose ps
   ```

3. **View logs**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f web
   docker-compose logs -f celery
   docker-compose logs -f celery_beat
   ```

### Frontend Development

1. **Start frontend**
   ```bash
   cd frontend
   docker-compose up -d
   ```

2. **View frontend logs**
   ```bash
   docker-compose logs -f nextjs
   ```

## 📖 Usage Guide

### 1. Login
- Username: `admin`
- Password: `adminpass`

### 2. Creating Scraping Tasks
1. Navigate to the Task List page
2. Select a news category from the dropdown
3. Set end time (optional, defaults to 1 hour later)
4. Configure scheduled hours for periodic scraping
5. Set maximum content limit
6. Click "Assign Task"

### 3. Managing Tasks
- **View Contents**: Click the eye icon to view scraped articles
- **Edit Task**: Click the edit icon to modify task parameters
- **Delete Task**: Click the delete icon to remove the task

### 4. Searching Articles
- Use the search filters in the task content view
- Search by content, author, location, or date range
- Use the generic search for cross-category searches

## 🔧 API Endpoints

### Tasks
- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Content
- `GET /api/tasks/{id}/contents/` - Get task contents
- `GET /api/tasks/{id}/elastic-search/` - Search task contents
- `GET /api/tasks/elastic-search/` - Generic search

### Documentation
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- Schema: `/api/schema/`

## 🏗️ Architecture Details

### Backend Services
- **Django Web**: Main API server
- **Celery Worker**: Background task processor
- **Celery Beat**: Task scheduler
- **MySQL**: Primary database
- **Redis**: Message broker and cache
- **Elasticsearch**: Search engine

### Data Flow
1. User creates scraping task via frontend
2. Task is stored in MySQL database
3. Celery Beat schedules periodic execution
4. Celery Worker executes scraping using Selenium
5. Scraped data is stored in both MySQL and Elasticsearch
6. Frontend queries data through Django API

## 🐛 Troubleshooting

### Common Issues

1. **Container startup failures**
   ```bash
   # Check container status
   docker-compose ps
   
   # View container logs
   docker-compose logs [service-name]
   
   # Restart services
   docker-compose restart
   ```

2. **Database connection issues**
   ```bash
   # Check MySQL health
   docker-compose exec db mysqladmin ping -h localhost
   
   # Reset database
   docker-compose down -v
   docker-compose up -d
   ```

3. **Elasticsearch connection issues**
   ```bash
   # Check Elasticsearch health
   curl http://localhost:9200/_cluster/health
   
   # Reset Elasticsearch data
   curl -X DELETE "localhost:9200/prothomalo_articles"
   ```

4. **Celery task issues**
   ```bash
   # Monitor Celery worker
   docker-compose logs -f celery
   
   # Monitor Celery beat
   docker-compose logs -f celery_beat
   ```

### Performance Optimization

1. **Increase scraping concurrency**
   - Modify `celery worker --concurrency=2` in docker-compose.yml

2. **Elasticsearch memory**
   - Adjust `ES_JAVA_OPTS=-Xms512m -Xmx512m` for larger datasets

3. **Database optimization**
   - Consider indexing frequently queried fields
   - Use connection pooling for high traffic

## 🔒 Security Considerations

- Change default passwords in production
- Use environment variables for sensitive data
- Implement proper authentication for production use
- Consider rate limiting for API endpoints
- Use HTTPS in production

## 📝 Development Notes

### Adding New Categories
Update the `categoryOptions` array in:
- [`frontend/src/app/tasklist/page.js`](frontend/src/app/tasklist/page.js)
- [`frontend/src/app/generic-search/page.js`](frontend/src/app/generic-search/page.js)

### Modifying Scraping Logic
Edit the scraping logic in:
- [`backend/api/scrapper.py`](backend/api/scrapper.py)

### Database Migrations
```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

## 🚦 Service Status Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View running services
docker-compose ps

# View service logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]

# Remove all data (careful!)
docker-compose down -v
```

## 📊 Monitoring

### Health Checks
- Backend API: http://localhost:8000/api/tasks/
- Elasticsearch: http://localhost:9200/_cluster/health
- Frontend: http://localhost:3000

### Logs
- Application logs: `docker-compose logs -f web`
- Celery logs: `docker-compose logs -f celery`
- Database logs: `docker-compose logs -f db`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for educational and research purposes. Please respect the target website's robots.txt and terms of service. Use responsibly and consider the impact on the target server.