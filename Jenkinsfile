pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        STACK_NAME = 'serverlessimage'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/Kishoreus/serverlessimage.git', branch: 'main'
            }
        }

        stage('Package Lambda Functions') {
            steps {
                script {
                    sh '''
                    cd lambdas
                    zip -r ../upload_handler.zip .
                    zip -r ../image_processor.zip .
                    '''
                }
            }
        }

        stage('Deploy CloudFormation Stack') {
            steps {
                sh '''
                aws cloudformation deploy \
                  --template-file cloudformation/T1.yaml \
                  --stack-name $STACK_NAME \
                  --capabilities CAPABILITY_NAMED_IAM \
                  --region $AWS_REGION
                '''
            }
        }

        stage('Upload Lambda Code to S3') {
            steps {
                script {
                    def bucketName = sh(
                        script: """
                        aws cloudformation describe-stacks \
                          --stack-name $STACK_NAME \
                          --query "Stacks[0].Outputs[?OutputKey=='S3Bucket'].OutputValue" \
                          --output text \
                          --region $AWS_REGION
                        """,
                        returnStdout: true
                    ).trim()

                    env.S3_BUCKET = bucketName

                    sh """
                    aws s3 cp upload_handler.zip s3://$S3_BUCKET/upload_handler.zip --region $AWS_REGION
                    aws s3 cp image_processor.zip s3://$S3_BUCKET/image_processor.zip --region $AWS_REGION
                    """
                }
            }
        }

        stage('Redeploy Stack to Update Lambda Code') {
            steps {
                sh '''
                aws cloudformation deploy \
                  --template-file cloudformation/T1.yaml \
                  --stack-name $STACK_NAME \
                  --capabilities CAPABILITY_NAMED_IAM \
                  --region $AWS_REGION
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployment succeeded.'
        }
        failure {
            echo 'Deployment failed.'
        }
    }
}
