# Prothom Alo Scrapper

A comprehensive web scraping system for monitoring and extracting news articles from Prothom Alo website. The system consists of a Django REST API backend with Celery for scheduled scraping tasks, Elasticsearch for search functionality, and a Next.js frontend for user interaction.

## 🏗️ Architecture

- **Backend**: Django REST API with Celery for background tasks
- **Frontend**: Next.js with Ant Design components
- **Database**: MySQL for application data
- **Search Engine**: Elasticsearch for article indexing and search
- **Cache/Queue**: Redis for Celery task queue
- **Web Scraping**: Selenium with Chrome/Chromium for dynamic content extraction

## `📋 Features

### Backend Features
- RESTful API for managing scraping tasks
- Scheduled scraping with Celery Beat
- Elasticsearch integration for advanced search
- Content filtering and search capabilities
- Task management (create, update, delete, view)
- Automatic task scheduling and execution

### Frontend Features

- Advanced search and filtering
- Real-time content viewing
- Task editing capabilities
- Generic search across all categories

### Scraping Features
- Category-based article scraping
- Dynamic content loading with infinite scroll
- News Article details extraction (title, author, location, content, publish time)
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
   git clone https://github.com/ashik5757/Prothom-Alo-Scrapper.git
   ```

   Go to root directory : 

   ```bash
   cd "Prothom-Alo-Scrapper"
   ```



2. **Set up environment variables**
   ```bash
   cd backend
   cp .env.example .env
   ```
   
   Edit the `.env` file with your `DJANGO_SECRET_KEY` configurations:
   ```env
   # Django Settings
   DEBUG=True
   DJANGO_SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0



   #### Existing CODE...............

   ```
3. **Open two terminal in root directory for backend and frontend.**

    > NOTE : Make sure you're in the root directory and Docker is running background : 

    ```bash
    Prothom-Alo-Scrapper/           # root 
    ├── README.md
    ├── backend/       # Django (Backend)
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   └── ...
    └── frontend/      # Next.js (frontend)
        ├── Dockerfile
        ├── docker-compose.yml
        └── ...
    ```


4. **Build and start the backend services**
   ```bash
   cd backend
   ```

   ```bash
   docker-compose up --build
   ```

    > NOTE : Wait for few minutes to migrate and load all the containers.

   <br>

   ***Additional Notes:***

   > To stop all the containers in this terminal PRESS `Ctrl+C` twice.

   To start the containers only after stopping all the containers :
   ```bash
   docker-compose up --d
   ```

   To stop all the containers :
   ```bash
   docker-compose stop
   ```

5. **Build and start the frontend services**
   ```bash
   cd frontend
   ```
   ```bash
   docker-compose up --build
   ```


   <br>

   ***Additional Notes:***

   > To stop all the containers in this terminal PRESS `Ctrl+C` twice.

   To start the containers only after stopping all the containers :
   ```bash
   docker-compose up --d
   ```

   To stop all the containers :
   ```bash
   docker-compose stop
   ```


6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/tasks/
   - API Documentation: http://localhost:8000/api/docs/



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
- `GET /api/tasks/{id}/contents/` - Get task contents FROM MySQL
- `GET /api/tasks/{id}/elastic-search/` - Search task contents From Elastic Search
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


   - Modify `celery worker --concurrency=2` in docker-compose.yml

   - Adjust `ES_JAVA_OPTS=-Xms512m -Xmx512m` for larger datasets



## 📝 Development Notes


### Updating API docs
Edit the scraping logic in:
- [`backend/api/views.py`](backend/api/views.py)

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


<!-- 
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

This tool is for educational and research purposes. Please respect the target website's robots.txt and terms of service. Use responsibly and consider the impact on the target server. -->