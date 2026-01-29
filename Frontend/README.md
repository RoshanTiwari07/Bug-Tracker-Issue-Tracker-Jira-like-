# Bug Tracker Frontend

A modern, production-ready bug tracking application built with React, TypeScript, Tailwind CSS, and Zustand. Features an interactive Kanban board with drag-and-drop, project management, ticket tracking, comments, and file attachments.

## 🚀 Quick Start

### Option 1: Docker (Recommended for Production)

```bash
# From project root directory
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Database: PostgreSQL on port 5432
```

### Option 2: Local Development

```bash
# Install dependencies
cd Frontend
npm install

# Start development server
npm run dev

# Frontend will run on http://localhost:3000
```

## 📋 Prerequisites

### For Docker:
- Docker & Docker Compose
- Backend API running (included in docker-compose)

### For Local Development:
- Node.js 18+
- npm or yarn
- Backend API running on http://localhost:8000

## 🛠️ Installation & Setup

### 1. Environment Configuration

```bash
# Copy environment file
cp .env.example .env

# Edit .env file
VITE_API_URL=http://localhost:8000
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

Application will be available at **http://localhost:3000**

## 🐳 Docker Setup

### Build Docker Image

```bash
# Build frontend image
docker build -t bug-tracker-frontend:latest .

# Or use docker-compose from root
cd ..
docker-compose build frontend
```

### Run with Docker Compose

```bash
# Start all services (from project root)
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Docker Architecture

```
Frontend Container (Nginx)
├── Port: 3000 → 80
├── Serves: Static React build
├── Proxies: /api → backend:8000
└── Networks: bug_tracker_network
```

## 📦 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run lint` | Run ESLint |

## 🏗️ Project Structure

```
Frontend/
├── src/
│   ├── components/
│   │   ├── ui/                    # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   └── Avatar.tsx
│   │   ├── layout/                # Layout components
│   │   │   ├── Layout.tsx
│   │   │   └── Navbar.tsx
│   │   └── kanban/                # Kanban board
│   │       ├── KanbanBoard.tsx
│   │       ├── KanbanColumn.tsx
│   │       ├── TicketCard.tsx
│   │       ├── TicketDetailsModal.tsx
│   │       └── CreateTicketModal.tsx
│   ├── pages/                     # Page components
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Projects.tsx
│   │   └── Board.tsx
│   ├── stores/                    # Zustand state management
│   │   ├── authStore.ts
│   │   ├── projectStore.ts
│   │   └── ticketStore.ts
│   ├── lib/                       # Utilities
│   │   ├── api.ts                # Axios API client
│   │   └── utils.ts              # Helper functions
│   ├── types/                     # TypeScript types
│   │   └── index.ts
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Global styles
├── public/                        # Static assets
├── Dockerfile                     # Docker configuration
├── nginx.conf                     # Nginx configuration
├── docker-compose.yml             # Docker Compose (root)
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── README.md
```

## ✨ Features

### 🔐 Authentication
- Login with email or username
- User registration
- JWT token management
- Protected routes
- Auto-login from localStorage

### 📊 Dashboard
- Project statistics
- Recent projects
- Quick navigation
- Activity overview

### 📁 Project Management
- Create/Edit/Delete projects
- Project key validation (2-10 uppercase)
- Private/Public projects
- Project members management

### 🎯 Kanban Board (Main Feature)
- **4 Status Columns**: To Do, In Progress, In Review, Done
- **Drag & Drop**: Move tickets between columns
- **Search**: Find tickets by keyword
- **Filters**: Filter by status, priority, assignee
- **Real-time Updates**: Instant status changes
- **Visual Feedback**: Smooth animations

### 🎫 Ticket Management
- Create tickets with title, description, type, priority
- Edit ticket details
- Assign to team members
- Change status and priority
- Color-coded priority badges
- Issue type icons (🐛 Bug, ✨ Feature, 📋 Task, 🚀 Improvement)

### 💬 Comments & Collaboration
- Add comments to tickets
- Threaded discussions
- Edit/Delete comments
- Real-time comment updates
- User avatars

### 📎 File Attachments
- Upload files to tickets
- Download attachments
- File size display
- Delete attachments
- Multiple file support

### 🎨 UI/UX
- Responsive design (mobile, tablet, desktop)
- Modern Tailwind CSS styling
- Toast notifications
- Loading states
- Error handling
- Empty states
- Smooth animations

## 🔧 Tech Stack

| Category | Technology |
|----------|-----------|
| **Framework** | React 18 |
| **Language** | TypeScript |
| **State Management** | Zustand |
| **Styling** | Tailwind CSS |
| **Routing** | React Router v6 |
| **HTTP Client** | Axios |
| **Drag & Drop** | @hello-pangea/dnd |
| **Icons** | Lucide React |
| **Notifications** | React Hot Toast |
| **Date Formatting** | date-fns |
| **Build Tool** | Vite |
| **Container** | Docker + Nginx |

## 🌐 API Integration

All API calls are centralized in `src/lib/api.ts`:

### Endpoints

```typescript
// Authentication
POST   /api/v1/auth/login
POST   /api/v1/auth/register
GET    /api/v1/auth/me

// Projects
GET    /api/v1/projects
POST   /api/v1/projects
GET    /api/v1/projects/:id
PUT    /api/v1/projects/:id
DELETE /api/v1/projects/:id

// Tickets
GET    /api/v1/tickets/:projectName/search
GET    /api/v1/tickets/:id
POST   /api/v1/tickets
PATCH  /api/v1/tickets/:id
PATCH  /api/v1/tickets/:id/status
PATCH  /api/v1/tickets/:id/assign

// Comments
GET    /api/v1/tickets/:id/comments
POST   /api/v1/tickets/:id/comments
PATCH  /api/v1/comments/:id
DELETE /api/v1/comments/:id

// Attachments
GET    /api/v1/attachments/tickets/:id/attachments
POST   /api/v1/attachments/tickets/:id/upload
GET    /api/v1/attachments/:id/download
DELETE /api/v1/attachments/:id
```

### API Client Features
- Automatic JWT token injection
- Request/Response interceptors
- Error handling
- Auto-redirect on 401
- TypeScript type safety

## 🎨 Design System

### Colors
- **Primary**: Blue (#3b82f6)
- **Success**: Green (#10b981)
- **Warning**: Yellow (#f59e0b)
- **Error**: Red (#ef4444)
- **Priority Colors**:
  - Low: Gray
  - Medium: Blue
  - High: Orange
  - Critical: Red

### Components
- **Buttons**: 4 variants (primary, secondary, danger, ghost)
- **Inputs**: With labels, validation, error states
- **Modals**: Responsive sizes (sm, md, lg, xl, full)
- **Cards**: White background, subtle shadow
- **Badges**: Color-coded, rounded
- **Avatars**: With initials fallback

## 🔒 Security

- JWT token authentication
- Protected API routes
- XSS prevention (React escaping)
- Input validation
- Secure file uploads
- HTTPS in production
- Security headers in Nginx

## 📱 Responsive Design

| Breakpoint | Width | Layout |
|------------|-------|--------|
| Mobile | < 768px | Single column |
| Tablet | 768px - 1024px | 2 columns |
| Desktop | > 1024px | 4 columns (Kanban) |

## 🚀 Production Deployment

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Docker Production

```bash
# Build image
docker build -t bug-tracker-frontend:latest .

# Run container
docker run -p 3000:80 \
  -e VITE_API_URL=https://api.yourdomain.com \
  bug-tracker-frontend:latest
```

### Deploy to Cloud

#### Vercel
```bash
npm install -g vercel
vercel deploy
```

#### Netlify
```bash
npm install -g netlify-cli
netlify deploy --prod
```

#### AWS S3 + CloudFront
```bash
npm run build
aws s3 sync dist/ s3://your-bucket-name
```

### Environment Variables

Set these in your hosting platform:

```bash
VITE_API_URL=https://api.yourdomain.com
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Mac/Linux
lsof -i :3000
kill -9 <PID>
```

### Backend Connection Issues

1. Verify backend is running: http://localhost:8000/docs
2. Check `.env` file: `VITE_API_URL=http://localhost:8000`
3. Check CORS settings in backend
4. Clear browser cache

### Docker Issues

```bash
# View logs
docker-compose logs -f frontend

# Rebuild image
docker-compose build --no-cache frontend

# Restart container
docker-compose restart frontend

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## 📊 Performance

- **Bundle Size**: Optimized with Vite
- **Code Splitting**: Automatic route-based
- **Lazy Loading**: Components on demand
- **Caching**: Static assets cached 1 year
- **Compression**: Gzip enabled in Nginx

## 🧪 Testing (Recommended)

```bash
# Install testing dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom

# Run tests
npm run test
```

## 🎯 Usage Guide

### 1. First Time Setup

1. **Register Account**
   - Navigate to http://localhost:3000
   - Click "Sign up"
   - Fill in email, username, password
   - Click "Sign Up"

2. **Create Project**
   - Click "Projects" in navbar
   - Click "New Project"
   - Enter name, key (e.g., "BUG"), description
   - Click "Create Project"

3. **Create Ticket**
   - You'll be on the Kanban board
   - Click "Create Ticket"
   - Fill in title, description, type, priority
   - Click "Create Ticket"

4. **Manage Tickets**
   - Drag tickets between columns
   - Click ticket to view details
   - Add comments
   - Upload attachments
   - Assign to team members

### 2. Keyboard Shortcuts (Future)

- `Ctrl/Cmd + K`: Quick search
- `C`: Create ticket
- `Esc`: Close modal
- `/`: Focus search

## 🔄 State Management

### Zustand Stores

```typescript
// Auth Store
useAuthStore()
  - user: User | null
  - isAuthenticated: boolean
  - login(credentials)
  - register(data)
  - logout()

// Project Store
useProjectStore()
  - projects: Project[]
  - currentProject: Project | null
  - fetchProjects()
  - createProject(data)
  - updateProject(id, data)
  - deleteProject(id)

// Ticket Store
useTicketStore()
  - tickets: Ticket[]
  - currentTicket: Ticket | null
  - searchTickets(projectName, params)
  - createTicket(data)
  - updateTicket(id, data)
  - changeTicketStatus(id, status)
```

## 🌟 Future Enhancements

- [ ] Real-time updates with WebSockets
- [ ] Advanced filtering and sorting
- [ ] Bulk ticket operations
- [ ] Custom fields
- [ ] Email notifications
- [ ] Sprint planning
- [ ] Time tracking
- [ ] Reports and analytics
- [ ] Dark mode
- [ ] Keyboard shortcuts
- [ ] Mobile app

## 📝 License

MIT

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

- **Documentation**: This README
- **Backend API**: http://localhost:8000/docs
- **Issues**: Open an issue on GitHub
- **Email**: support@bugtracker.com

## 🎉 Summary

This is a **complete, production-ready** bug tracking frontend with:

✅ Full authentication system  
✅ Interactive Kanban board with drag-and-drop  
✅ Complete CRUD for projects and tickets  
✅ Comments and file attachments  
✅ Responsive design  
✅ Docker support  
✅ TypeScript type safety  
✅ Modern UI with Tailwind CSS  
✅ State management with Zustand  
✅ Comprehensive error handling  

**Ready to deploy and use!** 🚀
