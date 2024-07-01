terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.region
}

locals {
  formatted_book_version = replace(var.book_version, ".", "_")
  owners_no_parenthesis = replace(replace(replace(replace(replace(replace(var.owner, "[", ""), "]", ""), "(", "",), ")", ""), "{", ""), "}", "")
  formatted_owners = replace(replace(replace(local.owners_no_parenthesis, " <", ": "), ">", ""), ", ", " - ")
}

resource "aws_iam_role" "book_lambda_role" {
  name = "${var.book_name}_${var.book_version}_lambda_role"
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

resource "aws_iam_policy" "secrets_manager_policy" {
  name        = "${var.book_name}_${var.book_version}_secrets_manager_policy"
  description = "Allow Lambda function to query secret 'infrastructure/datadog_api_key' from Secrets Manager"
  policy      = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:${var.region}:${data.aws_caller_identity.current.account_id}:secret:infrastructure/datadog_api_key*"
    }
  ]
}
EOF
}

data "aws_caller_identity" "current" {}

resource "aws_iam_policy_attachment" "basic_lambda_policy_attachment" {
  name       = "${var.book_name}_${var.book_version}_lambda_role_policy_attachment"
  roles      = [aws_iam_role.book_lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy_attachment" "secrets_manager_policy_attachment" {
  name       = "${var.book_name}_${var.book_version}_secrets_manager_policy_attachment"
  roles      = [aws_iam_role.book_lambda_role.name]
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
}

resource "aws_lambda_function" "book_lambda" {
  package_type  = "Image"
  image_uri     = var.image_uri
  function_name = "${var.book_name}_${local.formatted_book_version}_lambda"
  role          = aws_iam_role.book_lambda_role.arn
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  tags = {
    bdk_runtime_version = var.bdk_runtime_version
    book_name           = var.book_name
    book_version        = var.book_version
    owner               = local.formatted_owners
  }

  environment {
    variables = {
      BDK_SERVICE_NAME = "kognitos.book.${var.book_name}"
      BDK_SERVICE_VERSION = var.book_version
      BDK_DEPLOYMENT_ENVIRONMENT = "main"
    }
  }
}

output "lambda_name" {
  value = aws_lambda_function.book_lambda.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.book_lambda.arn
}
