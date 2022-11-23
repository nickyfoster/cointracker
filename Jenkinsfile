pipeline {
    agent {
        node {
            label 'ec2-fleet'
        }
    }

    environment {
        ECR_URL = 'https://381171443050.dkr.ecr.us-east-2.amazonaws.com'
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
        stage('Build & Push Docker Image') {
            steps {
                script {
                    docker.withRegistry(ECR_URL, 'aws-ecr') {
                        sh "docker build . -t cointracker:${env.BUILD_NUMBER} -t cointracker:latest"
                        docker_image = docker.build("cointracker:${env.BUILD_NUMBER}")
                        docker_image.push()
                        docker_image.push("latest")
                    }
                }
            }
        }
    }
}