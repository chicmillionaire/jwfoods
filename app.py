from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import click # Import click for Flask CLI commands

app = Flask(__name__)
# IMPORTANT: Use an environment variable for SECRET_KEY in production!
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))

# Use DATABASE_URL for Heroku PostgreSQL, fallback to SQLite for local development
database_url = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "jwfoods.db")}')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app) # Enable CORS for frontend communication

# Database Models
class DeliveryCoefficients(db.Model):
    __tablename__ = 'delivery_coefficients'
    
    id = db.Column(db.Integer, primary_key=True)
    distance_coefficient = db.Column(db.Float, nullable=False, default=0.5)
    weight_coefficient = db.Column(db.Float, nullable=False, default=0.5)
    base_cost = db.Column(db.Float, nullable=False, default=5.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'distance_coefficient': self.distance_coefficient,
            'weight_coefficient': self.weight_coefficient,
            'base_cost': self.base_cost,
            'updated_at': self.updated_at.isoformat()
        }

class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'message': self.message,
            'submitted_at': self.submitted_at.isoformat()
        }

class DeliveryCalculation(db.Model):
    __tablename__ = 'delivery_calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    distance = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    calculated_cost = db.Column(db.Float, nullable=False)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'distance': self.distance,
            'weight': self.weight,
            'calculated_cost': self.calculated_cost,
            'calculated_at': self.calculated_at.isoformat()
        }

# Flask CLI command for database initialization
@app.cli.command('init-db')
def init_db_command():
    """Clear existing data and create new tables, then add default coefficients."""
    with app.app_context():
        db.drop_all() # Drop all tables to ensure a clean start (useful for development)
        db.create_all() # Create all tables
        
        # Check if coefficients exist, if not create default ones
        if not DeliveryCoefficients.query.first():
            default_coeffs = DeliveryCoefficients(
                distance_coefficient=0.5,
                weight_coefficient=0.5,
                base_cost=5.0
            )
            db.session.add(default_coeffs)
            db.session.commit()
            click.echo('Initialized the database with default coefficients.')
        else:
            click.echo('Database already initialized with coefficients. Skipping default insertion.')
    click.echo('Database initialized successfully.')


# API Routes
@app.route('/api/calculate-delivery', methods=['POST'])
def calculate_delivery():
    """Calculate delivery cost based on distance and weight"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        distance = data.get('distance')
        weight = data.get('weight')
        
        if distance is None or weight is None:
            return jsonify({'error': 'Distance and weight are required'}), 400
        
        if distance <= 0 or weight <= 0:
            return jsonify({'error': 'Distance and weight must be positive values'}), 400
        
        # Get current coefficients from database
        coeffs = DeliveryCoefficients.query.first()
        if not coeffs:
            # If coefficients are not found, it means the database wasn't initialized
            return jsonify({'error': 'Delivery coefficients not configured. Please initialize the database.'}), 500
        
        # Calculate delivery cost
        calculated_cost = (coeffs.base_cost + 
                           (coeffs.distance_coefficient * distance) + 
                           (coeffs.weight_coefficient * weight))
        
        # Round to 2 decimal places
        calculated_cost = round(calculated_cost, 2)
        
        # Save calculation to database for analytics
        calculation = DeliveryCalculation(
            distance=distance,
            weight=weight,
            calculated_cost=calculated_cost
        )
        db.session.add(calculation)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'cost': calculated_cost,
            'distance': distance,
            'weight': weight,
            'coefficients_used': {
                'distance_coefficient': coeffs.distance_coefficient,
                'weight_coefficient': coeffs.weight_coefficient,
                'base_cost': coeffs.base_cost
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500

@app.route('/api/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()
        
        if not name or not email or not message:
            return jsonify({'error': 'Name, email, and message are required'}), 400
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please provide a valid email address'}), 400
        
        # Save contact submission
        submission = ContactSubmission(
            name=name,
            email=email,
            phone=phone if phone else None,
            message=message
        )
        db.session.add(submission)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your message! We\'ll get back to you soon.',
            'submission_id': submission.id
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit contact form: {str(e)}'}), 500

@app.route('/api/coefficients', methods=['GET'])
def get_coefficients():
    """Get current delivery coefficients"""
    try:
        coeffs = DeliveryCoefficients.query.first()
        if not coeffs:
            return jsonify({'error': 'No coefficients found. Please initialize the database.'}), 404
        
        return jsonify({
            'success': True,
            'coefficients': coeffs.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get coefficients: {str(e)}'}), 500

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    # Ensure database is accessible and tables exist before querying
    try:
        coeffs = DeliveryCoefficients.query.first()
        recent_calculations = DeliveryCalculation.query.order_by(DeliveryCalculation.calculated_at.desc()).limit(10).all()
        recent_contacts = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).limit(10).all()
    except Exception as e:
        # Log the error for debugging
        app.logger.error(f"Database query error in admin_dashboard: {e}")
        flash(f"Error loading dashboard data: {e}. Please ensure the database is initialized.", 'danger')
        coeffs = None
        recent_calculations = []
        recent_contacts = []
    
    return render_template('admin.html', 
                           coefficients=coeffs,
                           calculations=recent_calculations,
                           contacts=recent_contacts)

@app.route('/admin/update-coefficients', methods=['POST'])
def update_coefficients():
    """Update delivery coefficients"""
    try:
        distance_coeff = float(request.form.get('distance_coefficient', 0.5))
        weight_coeff = float(request.form.get('weight_coefficient', 0.5))
        base_cost = float(request.form.get('base_cost', 5.0))
        
        if distance_coeff < 0 or weight_coeff < 0 or base_cost < 0:
            flash('All coefficients must be positive values', 'error')
            return redirect(url_for('admin_dashboard'))
        
        coeffs = DeliveryCoefficients.query.first()
        if coeffs:
            coeffs.distance_coefficient = distance_coeff
            coeffs.weight_coefficient = weight_coeff
            coeffs.base_cost = base_cost
            coeffs.updated_at = datetime.utcnow()
        else:
            # This case should ideally not happen if init-db is run, but handles it gracefully
            coeffs = DeliveryCoefficients(
                distance_coefficient=distance_coeff,
                weight_coefficient=weight_coeff,
                base_cost=base_cost
            )
            db.session.add(coeffs)
        
        db.session.commit()
        flash('Coefficients updated successfully!', 'success')
        
    except ValueError:
        flash('Please enter valid numeric values', 'error')
    except Exception as e:
        flash(f'Error updating coefficients: {str(e)}', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/calculations')
def admin_calculations():
    """View all delivery calculations"""
    try:
        page = request.args.get('page', 1, type=int)
        calculations = DeliveryCalculation.query.order_by(DeliveryCalculation.calculated_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
    except Exception as e:
        app.logger.error(f"Database query error in admin_calculations: {e}")
        flash(f"Error loading calculations data: {e}. Please ensure the database is initialized.", 'danger')
        calculations = None # Or an empty Pagination object if preferred
    return render_template('calculations.html', calculations=calculations)

@app.route('/admin/contacts')
def admin_contacts():
    """View all contact submissions"""
    try:
        page = request.args.get('page', 1, type=int)
        contacts = ContactSubmission.query.order_by(ContactSubmission.submitted_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
    except Exception as e:
        app.logger.error(f"Database query error in admin_contacts: {e}")
        flash(f"Error loading contacts data: {e}. Please ensure the database is initialized.", 'danger')
        contacts = None # Or an empty Pagination object if preferred
    return render_template('contacts.html', contacts=contacts)

# Serve the main website
@app.route('/')
def index():
    """Serve the main website"""
    return render_template('index.html')

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Attempt a simple database query to check connection
        db.session.execute(db.select(1)).scalar_one()
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status
    })

if __name__ == '__main__':
    # When running app.py directly, you can still call init_db_command()
    # However, for 'flask run', you MUST use 'flask init-db' first.
    # It's generally better to rely on the CLI command for consistency.
    app.run(debug=True, host='0.0.0.0', port=5000)
