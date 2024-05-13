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

resource "aws_iam_policy_attachment" "basic_lambda_policy_attachment" {
  name       = "${var.book_name}_${var.book_version}_lambda_role_policy_attachment"
  roles      = [aws_iam_role.book_lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "book_lambda" {
  package_type  = "Image"
  image_uri     = var.image_uri
  function_name = "${var.book_name}_${var.book_version}_lambda"
  role          = aws_iam_role.book_lambda_role.arn
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  tags = {
    book_name     = var.book_name
    book_version  = var.book_version
    owner         = var.owner
    runtime       = var.runtime
  }
}

output "lambda_name" {
  value = aws_lambda_function.book_lambda.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.book_lambda.arn
}
