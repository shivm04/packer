variable "region" {
  default = "us-east-1"
}

variable "ami_id" {
  description = "AMI ID from Packer"
  type        = string
}
