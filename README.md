# J.W. Foods - Modern Single Page Website

A modern, responsive single-page website for J.W. Foods, a food service company in the Greater Toronto Area. This project includes a static HTML website with integrated Flask API for delivery cost calculations.

## Project Overview

This project was built to replace J.W. Foods' outdated website with a modern, mobile-friendly single-page design that includes:

- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, professional design using Bootstrap 5
- **Delivery Calculator**: Interactive tool powered by Flask API
- **Easy Navigation**: Smooth scrolling navigation between sections
- **Admin Panel**: Web interface for updating delivery coefficients

## Features

### Frontend (HTML/CSS/JavaScript)
- Single-page responsive design
- Bootstrap 5 for styling and components
- Custom SVG graphics and animations
- Smooth scrolling navigation
- Mobile-optimized layout
- Delivery cost calculator with real-time API integration

### Backend (Flask API)
- RESTful API for delivery cost calculations
- SQLite database for storing coefficients
- Admin panel for updating pricing parameters
- Health check endpoints
- Error handling and validation

## File Structure

```
jwfoods/
├── templates/             # HTML template files
│   ├── index.html         # Main website file
│   ├── admin.html         # Admin panel interface
│   ├── contacts.html      # Contact information page
│   └── calculations.html  # Delivery calculations page
├── app.py                 # Flask API application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment configuration
├── render.yaml           # Render deployment configuration
├── jwfoods.db            # SQLite database (created automatically)
└── README.md             # This file
```

## Requirements

### For Local Development
- Python 3.7 or higher
- Modern web browser (Firefox 100+, Chrome, Safari, Edge)

### For Production Deployment
- Render account or Heroku account (for deployment)
- Git for version control

## Setup Instructions

### 1. Local Development Setup

1. **Clone or download the project files**
   ```bash
   mkdir jwfoods
   cd jwfoods
   # Copy all project files to this directory
   ```

2. **Set up Python virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Flask API**
   ```bash
   python app.py
   ```
   The API will be available at `http://localhost:5000`

5. **Open the website**
   - Open `templates/index.html` in your web browser
   - Or serve it using a local web server:
     ```bash
     # Using Python's built-in server
     python -m http.server 8080
     # Then visit http://localhost:8080/templates/
     ```

### 2. Testing the Application

1. **Test the API directly**
   ```bash
   # Health check
   curl http://localhost:5000/health
   
   # Calculate delivery cost
   curl -X POST http://localhost:5000/api/calculate-delivery \
     -H "Content-Type: application/json" \
     -d '{"distance": 25, "weight": 5.0}'
   ```

2. **Access the Admin Panel**
   - Visit `http://localhost:5000/admin`
   - Update coefficients and test calculations

3. **Test the Website**
   - Open `templates/index.html` in your browser
   - Navigate through all sections
   - Test the delivery calculator
   - Verify mobile responsiveness

## Deployment Options

### Option 1: Deploy to Render (Recommended)

Render is a modern cloud platform that offers free hosting with automatic deployments from Git.

#### Prerequisites
- Render account (free at render.com)
- Git repository (GitHub, GitLab, or Bitbucket)

#### Steps

1. **Create render.yaml configuration file**
   Create a `render.yaml` file in your project root:
   ```yaml
   services:
     - type: web
       name: jwfoods-api
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: python app.py
       envVars:
         - key: PYTHON_VERSION
           value: 3.9.16
         - key: PORT
           value: 10000
   ```

2. **Push your code to a Git repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/jwfoods-website.git
   git push -u origin main
   ```

3. **Deploy on Render**
   - Go to [render.com](https://render.com) and sign in
   - Click "New +" and select "Web Service"
   - Connect your Git repository
   - Render will automatically detect your Python app
   - Configure the following settings:
     - **Name**: jwfoods-api (or your preferred name)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
   - Click "Create Web Service"

4. **Update the API URL in templates/index.html**
   - Change the `API_BASE_URL` in the JavaScript section to your Render app URL
   - Example: `const API_BASE_URL = 'https://jwfoods-api.onrender.com';`
   - Commit and push the changes

5. **Access your deployed app**
   - Your app will be available at `https://your-app-name.onrender.com`
   - Render provides automatic HTTPS and custom domains

#### Render Benefits
- Free tier available with 750 hours/month
- Automatic deployments from Git
- Built-in SSL certificates
- No credit card required for free tier
- Better performance than Heroku free tier

### Option 2: Deploy to Heroku (Alternative)

#### Prerequisites
- Heroku CLI installed
- Git repository initialized
- Heroku account

#### Steps

1. **Initialize Git repository** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

3. **Deploy to Heroku**
   ```bash
   git push heroku main
   ```

4. **Open your deployed app**
   ```bash
   heroku open
   ```

5. **Update the API URL in templates/index.html**
   - Change the `API_BASE_URL` in the JavaScript section to your Heroku app URL
   - Example: `const API_BASE_URL = 'https://your-app-name.herokuapp.com';`

## Deployment Configuration Files

### For Render: render.yaml
```yaml
services:
  - type: web
    name: jwfoods-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.16
      - key: PORT
        value: 10000
```

### For Heroku: Procfile
```
web: python app.py
```

## API Endpoints

### Public Endpoints

- `GET /` - API documentation page
- `GET /health` - Health check endpoint
- `POST /api/calculate-delivery` - Calculate delivery cost
  ```json
  {
    "distance": 25,
    "weight": 5.0
  }
  ```

### Admin Endpoints

- `GET /admin` - Admin panel interface
- `POST /admin/update` - Update coefficients
- `GET /api/coefficients` - Get current coefficients

## Configuration

### Delivery Calculation Formula
```
delivery_cost = (distance_coefficient × distance) + (weight_coefficient × weight)
```

### Default Coefficients
- Distance coefficient: 0.5 (cost per kilometer)
- Weight coefficient: 0.5 (cost per kilogram)

These can be updated through the admin panel at `/admin`.

## Browser Compatibility

- Firefox 100+
- Chrome 80+
- Safari 13+
- Edge 80+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Design Features

### Typography
- Font family: Arial, Verdana (as per requirements)
- Minimum 16px font size for readability
- Responsive text scaling

### Layout
- Single-page design with smooth scrolling
- Fixed navigation with logo
- Mobile-first responsive approach
- Consistent section padding and spacing

### Color Scheme
- Primary: #007bff (Bootstrap blue)
- Success: #28a745 (green)
- Dark: #343a40 (navigation and contact section)
- Light: #f8f9fa (alternate section backgrounds)

## Troubleshooting

### Common Issues

1. **API not connecting**
   - Ensure Flask app is running on port 5000 locally
   - Check if the deployed API URL is correct in index.html
   - Check deployment logs on Render/Heroku dashboard
   - Website will fall back to demo mode if API is unavailable

2. **Database issues**
   - Delete `jwfoods.db` file and restart Flask app locally
   - For deployed apps, database will be recreated automatically
   - Note: Render and Heroku have ephemeral storage, database resets on restart

3. **Mobile display issues**
   - Ensure viewport meta tag is present
   - Test on multiple devices and screen sizes

4. **Deployment issues**
   - Check build logs on your hosting platform
   - Ensure all dependencies are in requirements.txt
   - Verify Python version compatibility

### Development Tips

1. **Testing on mobile**
   - Use browser developer tools
   - Test on actual mobile devices
   - Check touch interactions

2. **Performance optimization**
   - Images are optimized SVGs for fast loading
   - Minimal external dependencies
   - CSS and JS are minified in production

3. **Environment variables**
   - Use environment variables for configuration in production
   - Keep sensitive data out of version control

## Hosting Platform Comparison

| Feature | Render (Free) | Heroku (Free - Discontinued) |
|---------|---------------|-------------------------------|
| Monthly Hours | 750 hours | N/A (free tier ended) |
| Sleep Policy | After 15 min inactivity | N/A |
| Build Time | Fast | Moderate |
| Custom Domains | Yes (paid plans) | Yes (paid plans) |
| Automatic HTTPS | Yes | Yes |
| Git Integration | Yes | Yes |
| Database | Ephemeral storage | Ephemeral storage |

**Note**: Heroku discontinued their free tier in November 2022. Render is currently the recommended free hosting option.

## Future Enhancements

- User authentication for admin panel
- Persistent database solution (PostgreSQL on paid hosting)
- Order tracking system
- Integration with payment processing
- Real-time delivery tracking
- Customer feedback system
- Multi-language support
- Environment-based configuration

## License

This project is created for educational purposes as part of the CKCS145 course requirements.

## Support

For technical support or questions about this implementation, please refer to the course materials or contact the development team.
