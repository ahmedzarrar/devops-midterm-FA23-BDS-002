pipeline {
  agent any
  triggers { githubPush() }
  environment { IMAGE = 'midterm-img'; REG = 'FA23-BDS-002' }
  stages {
    stage('Build + Train') {
      steps { sh 'docker build --build-arg GIT_COMMIT=$GIT_COMMIT -t $IMAGE:latest .' }
    }
    stage('Test') {
      steps { sh 'docker run --rm $IMAGE:latest python -m pytest -q' }
    }
    stage('Deploy') {
      steps {
        sh '''docker rm -f midterm-app || true
docker run -d --name midterm-app --restart unless-stopped -p 8000:8000 $IMAGE:latest
sleep 5
curl -sf http://localhost:8000/metrics'''
      }
    }
  }
  post {
    always {
      mail to: 'qasimalik@gmail.com',
           from: 'YOUR_SENDER@gmail.com',
           subject: "[${env.REG}] ${env.JOB_NAME} #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
           body: "Reg no: ${env.REG}\nResult: ${currentBuild.currentResult}\nBuild: ${env.BUILD_URL}"
    }
  }
}
