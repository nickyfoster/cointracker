pipeline {
    agent {
        node {
            label 'ec2-fleet'
        }
    }
    stages {
        stage('Checkout project') {
            steps {
                script {
                    git branch: "master",
                        credentialsId: 'my-credentials',
                        url: 'https://user@github.org/myproject/sample-repo.git'
                }
            }
        }
        stage('Installing packages') {
            steps {
                script {
                    sh 'pip install -r requirements.txt'
                }
            }
        }
    }
}