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
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build . -t cointracker:${env.BUILD_NUMBER} -t cointracker:latest'
                }
            }
        }
    }
}