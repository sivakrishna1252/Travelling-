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
                    if [ ! -d "venv" ]; then
                        python3 -m venv venv
                    fi

                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    '''
                }
            }
        }

        stage('Migrate') {
            steps {
                dir('traveling') {
                    sh '''
                    . venv/bin/activate
                    python manage.py migrate
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                dir('traveling') {
                    sh '''
                    . venv/bin/activate

                    echo "Stopping old server..."
                    pkill -f runserver || true

                    echo "Starting server on port ${PORT}"
                    nohup python manage.py runserver 0.0.0.0:${PORT} > server.log 2>&1 &

                    echo "Live: http://SERVER_IP:${PORT}"
                    '''
                }
            }
        }
    }
}
