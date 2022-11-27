pipeline {
    agent {
        node {
            label 'ec2-fleet'
        }
    }

    environment {
        GITHUB_REPO_URL = 'https://github.com/nickyfoster/cointracker.git'
        GITHUB_CREDENTIALS = 'github-creds'
        ECR_URL = '381171443050.dkr.ecr.us-east-2.amazonaws.com'
        ECR_REGION = 'us-east-2'
        REPO_NAME = 'cointracker'
        ECR_CREDENTIALS_NAME = 'jenkins-ecr-global-pusher'
    }

    stages {
        stage('Checkout project') {
            steps {
                script {
                    git branch: "master", credentialsId: GITHUB_CREDENTIALS, url: GITHUB_REPO_URL
                }
            }
        }
        stage('Build & Push Docker Image') {
            steps {
                script {
                    withAWS(credentials: ECR_CREDENTIALS_NAME) {
                        sh "aws ecr get-login-password --region ${ECR_REGION} | docker login --username AWS --password-stdin ${ECR_URL}"
                        sh "docker build . -t ${REPO_NAME}:${env.BUILD_NUMBER}"
                        docker_image = docker.build("${ECR_URL}/${REPO_NAME}:${env.BUILD_NUMBER}")
                        docker_image.push()
                        println 11111
                        println env.BRANCH_NAME
                        if (env.BRANCH_NAME == "master") {
                            docker_image.push("latest")
                        }
                    }
                }
            }
        }
    }
}