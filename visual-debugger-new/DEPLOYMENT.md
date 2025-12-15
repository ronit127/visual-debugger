# Deployment Guide

This guide covers deploying Visual Debugger to production.

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+ with pip
- A hosting platform (Vercel, Heroku, AWS, etc.)

## Frontend Deployment (Next.js)

### Option 1: Vercel (Recommended)

Vercel is the creator of Next.js and offers seamless deployment:

1. Push your code to GitHub
2. Connect your repository at [vercel.com](https://vercel.com)
3. Vercel automatically builds and deploys on every push
4. Configure environment variables in Vercel dashboard

### Option 2: Manual Deployment

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Backend Deployment (Flask)

### Option 1: Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create a Procfile in the backend directory
echo "web: python app.py" > backend/Procfile

# Create Heroku app
heroku create your-app-name

# Deploy
git push heroku main
```

### Option 2: AWS EC2

1. Launch an EC2 instance
2. SSH into the instance
3. Clone repository
4. Install dependencies: `pip install -r requirements.txt`
5. Run Flask app with Gunicorn: `gunicorn -w 4 -b 0.0.0.0:5000 app:app`
6. Use Nginx as reverse proxy

### Option 3: Docker

Create a `Dockerfile` for Flask:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t visual-debugger-backend .
docker run -p 5000:5000 visual-debugger-backend
```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (.env)
```
FLASK_ENV=production
```

## Database Setup (if using MongoDB)

If using MongoDB in production:

1. Set up MongoDB Atlas account
2. Create a database
3. Get connection string
4. Update `MONGO_URI` in Flask app

## SSL/HTTPS

- For Vercel: Automatic SSL certificate
- For AWS/EC2: Use Let's Encrypt with Certbot
- For Heroku: Automatic HTTPS on *.herokuapp.com domains

## Monitoring & Logging

- Set up error tracking (Sentry, LogRocket)
- Monitor performance metrics
- Set up alerts for backend failures
- Use CDN for static assets (Cloudflare, CloudFront)

## Performance Optimization

1. **Frontend:**
   - Enable image optimization
   - Code splitting is automatic with Next.js
   - Use Vercel's edge functions for fast API responses

2. **Backend:**
   - Use connection pooling for database
   - Cache frequently accessed data
   - Implement rate limiting
   - Use Gunicorn with multiple workers

## Post-Deployment Checklist

- [ ] Environment variables are configured
- [ ] Database connections are working
- [ ] CORS is properly configured
- [ ] Error logging is enabled
- [ ] SSL/HTTPS is working
- [ ] Backend API is responding to requests
- [ ] Frontend can communicate with backend
- [ ] Monitoring and alerts are set up

## Troubleshooting

### Frontend won't load
- Check NEXT_PUBLIC_API_URL environment variable
- Verify backend is accessible
- Check browser console for errors

### Backend not responding
- Check Flask app is running
- Verify port is open
- Check environment variables
- Review server logs

### CORS errors
- Ensure flask-cors is installed
- Verify CORS configuration in app.py includes frontend URL
- Check request headers

## Support

For deployment issues, consult the documentation for your hosting platform or open an issue in the repository.
