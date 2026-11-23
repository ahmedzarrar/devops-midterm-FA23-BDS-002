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
for i in $(seq 1 15); do
  curl -sf http://localhost:8000/metrics && exit 0
  sleep 2
done
exit 1'''
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
        def emails = [] as Set
        try {
          sh(script: 'git log -1 --pretty=format:%ae%n%ce', returnStdout: true)
            .trim().split('\n').each { e ->
              e = e.trim()
              if (e && !e.contains('noreply')) { emails << e }
            }
        } catch (err) { echo "could not read committer: ${err}" }
        if (emails) {
          mail to: emails.join(','),
               subject: "[${env.REG}] ${env.JOB_NAME} #${env.BUILD_NUMBER} ${currentBuild.currentResult}",
               body: "Reg no: ${env.REG}\nResult: ${currentBuild.currentResult}\nBuild: ${env.BUILD_URL}"
        } else {
          echo 'No usable committer email found, no mail sent'
        }
      }
    }
  }
}
