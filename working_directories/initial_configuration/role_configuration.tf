terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    key    = "role_configuration.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.book_name}_lambda_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "basic_lambda_policy_attachment" {
  name       = "${var.book_name}_lambda_role_policy_attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "python_monitoring" {
  name   = "python_monitoring"
  role   = aws_iam_role.lambda_role.name
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": "logs:CreateLogGroup",
        "Resource": "arn:aws:logs:us-west-2:719468614044:log-group:/aws/lambda/sandbox-main-python"
    },
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": [
            "logs:PutLogEvents",
            "logs:CreateLogStream"
        ],
        "Resource": "arn:aws:logs:us-west-2:719468614044:log-group:/aws/lambda/sandbox-main-python:log-stream:*"
    },
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": [
            "xray:PutTraceSegments",
            "xray:PutTelemetryRecords"
        ],
        "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "python_test_state" {
  name   = "python_test_state"
  role   = aws_iam_role.lambda_role.name
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Sid": "",
        "Effect": "Allow",
        "Action": "dynamodb:*",
        "Resource": "arn:aws:dynamodb:us-west-2:719468614044:table/sandbox-main-test_state"
    }
  ]
}
EOF
}
