variable "region" {
  default = "ap-south-1"
}

variable "ami_id" {
  description = "AMI ID from Packer"
  type        = string
}
