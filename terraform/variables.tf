variable "region" {
  type = string
  default = "This will be overriden by the pipeline"
}

variable "owner" {
  type = string
}

variable "lambda_timeout" {
  type = number
}

variable "lambda_memory_size" {
  type = number  
}

variable "image_uri" {
  type = string
}

variable "book_name" {
  type = string
}

variable "book_version" {
  type = string
}

variable "bdk_runtime_version" {
  type = string
}

