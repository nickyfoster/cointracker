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
                        credentialsId: 'github-creds',
                        url: 'https://github.com/nickyfoster/cointracker.git'
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