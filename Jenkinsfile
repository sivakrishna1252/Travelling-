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
                sh '''
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi

                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
            }
        }

        stage('Migrate') {
            steps {
                sh '''
                    . venv/bin/activate
                    
                    # Robust cleanup: Remove all migration files and restore from Git
                    # This ensures only tracked migrations from the repository are present
                    find accounts/migrations/ -name "*.py" ! -name "__init__.py" -delete
                    git checkout accounts/migrations/

                    echo "Collecting static files..."
                    python manage.py collectstatic --noinput

                    echo "Making migrations..."
                    python manage.py makemigrations --noinput
                    
                    echo "Applying migrations..."
                    python manage.py migrate --noinput
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                   withEnv(['JENKINS_NODE_COOKIE=dontKillMe']) {
                        sh '''
                        . venv/bin/activate

                        echo "Stopping old processes..."
                        pkill -f gunicorn || true
                        pkill -f runserver || true
                        pkill -f celery || true

                        echo "Starting server on port ${PORT} using gunicorn..."
                        nohup gunicorn --bind 0.0.0.0:${PORT} traveling.wsgi:application > server.log 2>&1 &

                        echo "Live: http://SERVER_IP:${PORT}"
                        '''
                   }
                }
            }
        }
    }
}
