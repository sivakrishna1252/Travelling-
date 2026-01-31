pipeline {
    agent any

    environment {
        PORT = '1252'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup & Install') {
            steps {
                dir('traveling') {
                    sh '''
                    # Create virtual environment if it doesn't exist
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi
                    
                    # Activate and install requirements
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Migrate & Static') {
            steps {
                dir('traveling') {
                    sh '''
                    . venv/bin/activate
                    python manage.py migrate
                    # Since we are using runserver in debug mode, collectstatic is not strictly needed 
                    # but good to have ready if we switch to production server
                    # python manage.py collectstatic --noinput 
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('traveling') {
                    sh '''
                    . venv/bin/activate
                    
                    echo "Deploying on port ${PORT}..."
                    
                    # Kill any process running on the port
                    fuser -k ${PORT}/tcp || true
                    
                    # Run server in background
                    nohup python manage.py runserver 0.0.0.0:${PORT} > server.log 2>&1 &
                    
                    echo "Deployment started on port ${PORT}"
                    echo "Admin Panel: http://<server-ip>:${PORT}/admin/"
                    echo "Swagger UI: http://<server-ip>:${PORT}/api/docs/"
                    '''
                }
            }
        }
    }
}
