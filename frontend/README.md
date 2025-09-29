# Business CRM Frontend

Modern, responsive Next.js frontend for the Business CRM System with MoySklad integration.

## 🚀 Features

- ✅ **Next.js 14** with App Router
- ✅ **TypeScript** for type safety
- ✅ **Tailwind CSS** for styling
- ✅ **React Query** for data fetching
- ✅ **Zustand** for state management
- ✅ **Responsive Design** - Mobile, tablet, desktop
- ✅ **Dark Mode Support** (ready)
- ✅ **Authentication** with JWT
- ✅ **Real-time Updates** with polling
- ✅ **Beautiful UI** with shadcn/ui inspired components

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── (auth)/            # Auth pages
│   │   ├── (dashboard)/       # Protected pages
│   │   └── layout.tsx         # Root layout
│   ├── components/
│   │   ├── ui/                # Reusable UI components
│   │   └── providers.tsx      # React Query provider
│   ├── lib/
│   │   ├── api/               # API client
│   │   ├── hooks/             # Custom hooks
│   │   ├── store/             # Zustand stores
│   │   ├── types/             # TypeScript types
│   │   └── utils.ts           # Utility functions
│   └── styles/
│       └── globals.css        # Global styles
├── public/                     # Static assets
├── Dockerfile                  # Docker configuration
├── next.config.js             # Next.js config
├── tailwind.config.ts         # Tailwind config
└── package.json               # Dependencies
```

## 🛠️ Tech Stack

### Core
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **React 18** - UI library

### State & Data
- **Zustand** - State management
- **TanStack Query (React Query)** - Server state
- **Axios** - HTTP client

### UI & Styling
- **Tailwind CSS** - Utility-first CSS
- **Lucide React** - Icons
- **Sonner** - Toast notifications
- **class-variance-authority** - Component variants

### Forms & Validation
- **React Hook Form** - Form handling
- **Zod** - Schema validation

## 🚀 Quick Start

### Development (Standalone)

```bash
# Install dependencies
npm install

# Create .env.local
cp .env.local.example .env.local

# Start development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Development (With Docker)

The frontend is already configured in the main docker-compose.yml:

```bash
# From project root
docker-compose up frontend

# Or start all services
docker-compose up
```

Visit [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 🔐 Authentication

Default credentials:
- **Email:** admin@example.com
- **Password:** admin123

The app uses JWT tokens stored in Zustand with persistence.

## 📱 Pages

### Public
- `/` - Redirects to dashboard or login
- `/login` - Login page

### Protected (Dashboard)
- `/dashboard` - Main dashboard with metrics
- `/products` - Product catalog
- `/inventory/stock` - Stock levels
- `/analytics/dashboard` - Analytics & reports
- `/organizations` - Organizations & employees
- `/admin/integrations` - Admin panel

## 🎨 UI Components

The app uses simplified shadcn/ui-inspired components:

- **Button** - Multiple variants and sizes
- **Card** - Container component
- **Input** - Form input
- **Badge** - Status indicators
- **Toast** - Notifications (Sonner)

## 🔌 API Integration

### API Client

Located in `src/lib/api/client.ts`:

```typescript
import { apiClient } from '@/lib/api/client';

// Example usage
const products = await apiClient.getProducts({ page: 1, limit: 20 });
```

### Custom Hooks

Located in `src/lib/hooks/use-api.ts`:

```typescript
import { useProducts, useDashboardMetrics } from '@/lib/hooks/use-api';

function MyComponent() {
  const { data, isLoading } = useProducts();
  // ...
}
```

## 🌐 Environment Variables

Create `.env.local`:

```bash
# API URL (backend)
NEXT_PUBLIC_API_URL=http://localhost:8000

# App name
NEXT_PUBLIC_APP_NAME=Business CRM System
```

For Docker:
```bash
NEXT_PUBLIC_API_URL=http://api:8000
```

## 🐳 Docker

### Development

```dockerfile
# Dockerfile already configured for development
# Hot reload enabled with volume mounts
```

### Production

```bash
# Build production image
docker build -t crm-frontend:prod .

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://your-api:8000 \
  crm-frontend:prod
```

## 📊 Features by Page

### Dashboard
- Revenue & orders metrics
- Growth indicators
- Low stock alerts
- Top products & customers

### Products
- Paginated product list
- Search & filters
- Product details
- Category filtering

### Inventory
- Stock levels by warehouse
- Low stock warnings
- Out of stock alerts
- Multi-warehouse support

### Analytics
- Sales dashboard
- Orders metrics
- Money flow
- Charts & visualizations

### Organizations
- Companies list
- Employees directory
- Projects management
- Contracts tracking

### Admin
- Integration status
- System health monitoring
- Sync controls
- Statistics dashboard

## 🎯 Performance

- **Code Splitting** - Automatic with Next.js
- **Image Optimization** - Next.js Image component
- **React Query** - Smart caching & refetching
- **Lazy Loading** - Components loaded on demand
- **Static Generation** - Where possible

## 🔧 Customization

### Colors

Edit `tailwind.config.ts` and `globals.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%;
  /* ... more colors */
}
```

### Layout

Edit `src/app/(dashboard)/layout.tsx` for sidebar and navigation.

### API Base URL

Update `NEXT_PUBLIC_API_URL` in `.env.local`

## 🧪 Testing (TODO)

```bash
# Run tests
npm test

# With coverage
npm run test:coverage
```

## 📝 Scripts

```bash
npm run dev          # Development server
npm run build        # Production build
npm run start        # Production server
npm run lint         # Run ESLint
npm run type-check   # TypeScript check
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build
docker build -t crm-frontend .

# Run
docker run -p 3000:3000 crm-frontend
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

## 📄 License

Same as main project

## 🆘 Support

For issues or questions:
1. Check documentation
2. Review error logs
3. Contact team

## 🎉 Credits

Built with:
- Next.js
- Tailwind CSS
- shadcn/ui (inspiration)
- Lucide Icons
- And many more amazing open-source projects