variable "environment" {
  type = string
  default = "test"
}

variable "owner" {
  type = string
  default = "kognitos"
}

variable "image_uri" {
  type = string
}

variable "book_name" {
  type = string
}

variable "book_version" {
  type = string
  default = "1_0_0"
}
