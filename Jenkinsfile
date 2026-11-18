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
    stage('Push to Docker Hub') {
      steps {
        catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
          timeout(time: 3, unit: 'MINUTES') {
            withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
              sh '''
                set +x
                trap 'docker logout' EXIT
                SHORT=$(echo "$GIT_COMMIT" | cut -c1-7)
                REPO="$DH_USER/midterm-fa23-bds-002"
                echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                docker tag $IMAGE:latest $REPO:latest
                docker tag $IMAGE:latest $REPO:$SHORT
                docker push $REPO:latest
                docker push $REPO:$SHORT
              '''
            }
          }
        }
      }
    }
  }
  post {
    always {
      script {
        def to = 'qasimalik@gmail.com'
        try {
          def committer = sh(script: 'git log -1 --pretty=format:%ae', returnStdout: true).trim()
          if (committer && !committer.contains('noreply') && !to.contains(committer)) {
            to += ",${committer}"
          }
        } catch (e) { echo "could not read committer: ${e}" }
        mail to: to,
             subject: "[${env.REG}] ${env.JOB_NAME} #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
             body: "Reg no: ${env.REG}\nResult: ${currentBuild.currentResult}\nBuild: ${env.BUILD_URL}"
      }
    }
  }
}