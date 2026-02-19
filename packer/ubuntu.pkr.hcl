packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = ">= 1.2.0"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "ami_version" {
  type = string
}

source "amazon-ebs" "ubuntu" {
  region                  = var.aws_region
  instance_type           = "t2.micro"
  ssh_username            = "ubuntu"
  ami_name                = "custom-ubuntu-${var.ami_version}"
  ami_description         = "Custom Ubuntu AMI built via Packer"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"
      virtualization-type = "hvm"
      root-device-type    = "ebs"
    }
    most_recent = true
    owners      = ["099720109477"] # Canonical
  }

  tags = {
    Name    = "custom-ubuntu-${var.ami_version}"
    Version = var.ami_version
    BuiltBy = "Packer-GitHub-Actions"
  }
}

build {
  name    = "custom-ubuntu-build"
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {
    script = "packer/scripts/install.sh"
  }
}
