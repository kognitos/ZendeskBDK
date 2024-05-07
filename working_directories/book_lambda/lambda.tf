terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    region = "us-west-2"
  }
}

provider "aws" {
  region = "us-west-2"
}

data "archive_file" "lambda_source_code" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lambda_function_payload.zip"
}

data "aws_iam_role" "lambda_role" {
  name = "${var.book_name}_lambda_role"
}

resource "aws_lambda_function" "python" {
  package_type  = "Image"
  image_uri     = var.image_uri
  function_name = "${var.book_name}-lambda-${var.book_version}"
  role          = aws_iam_role.python.arn
  timeout       = 60
  memory_size   = 512
  description   = "python native sandbox"

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    environment = var.environment
    version     = var.book_version
    owner       = var.owner
  }
}