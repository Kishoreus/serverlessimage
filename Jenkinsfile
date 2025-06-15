pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        STACK_NAME = 'serverlessimage'
        BASE_TEMPLATE = 'cloudformation/T1_base.yaml'
        FULL_TEMPLATE = 'cloudformation/T1.yaml'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git url: 'https://github.com/Kishoreus/serverlessimage.git', branch: 'main'
            }
        }

        stage('Package Lambda Functions') {
            steps {
                sh '''
                cd lambdas
                zip -r ../upload_handler.zip upload_handler.py
                zip -r ../image_processor.zip image_processor.py
                '''
            }
        }

        stage('Deploy Initial Stack (Create Bucket + IAM)') {
            steps {
                sh '''
                aws cloudformation deploy \
                  --template-file $BASE_TEMPLATE \
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

        stage('Deploy Full Stack (Lambdas + API Gateway)') {
            steps {
                sh '''
                aws cloudformation deploy \
                  --template-file $FULL_TEMPLATE \
                  --stack-name $STACK_NAME \
                  --capabilities CAPABILITY_NAMED_IAM \
                  --region $AWS_REGION
                '''
            }
        }
    }

    post {
        success {
            echo 'Full deployment succeeded.'
        }
        failure {
            echo 'Deployment failed.'
        }
    }
}
