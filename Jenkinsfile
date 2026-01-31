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
                    
                    echo "Making migrations..."
                    python manage.py makemigrations --noinput
                    
                    echo "Applying migrations..."
                    python manage.py migrate --noinput
                    
                    echo "Creating superuser if not exists..."
                    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin@123')"
                '''
            }
        }

        stage('Deploy') {
            steps {
                script {
                   withEnv(['JENKINS_NODE_COOKIE=dontKillMe']) {
                        sh '''
                        . venv/bin/activate

                        echo "Stopping old server..."
                        pkill -f gunicorn || true
                        pkill -f runserver || true

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
