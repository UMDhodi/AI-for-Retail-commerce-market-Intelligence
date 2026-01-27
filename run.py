#!/usr/bin/env python3
"""
BharatSignal Application Runner
Simple script to start the Flask application with proper configuration
"""

import os
import sys
from app import app
from config import config

def main():
    """Main function to run the application"""
    
    # Get environment from command line or default to development
    env = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    if env not in config:
        print(f"Invalid environment: {env}")
        print(f"Available environments: {list(config.keys())}")
        sys.exit(1)
    
    # Load configuration
    app.config.from_object(config[env])
    
    # Check AWS credentials
    if not app.config.get('AWS_ACCESS_KEY_ID'):
        print("⚠️  Warning: AWS credentials not configured")
        print("Please set up your .env file with AWS credentials")
        print("See .env.example for the required format")
    
    # Run the application
    print(f"🚀 Starting BharatSignal in {env} mode...")
    print(f"🌐 Access the application at: http://localhost:5000")
    
    app.run(
        debug=app.config.get('DEBUG', False),
        host='0.0.0.0',
        port=5000
    )

if __name__ == '__main__':
    main()