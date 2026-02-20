provider "aws" {
  region = us-east-1
}

resource "aws_vpc" "packer_vpc" {
  cidr_block           = "10.50.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "packer-temp-vpc"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.packer_vpc.id

  tags = {
    Name = "packer-temp-igw"
  }
}

resource "aws_subnet" "packer_subnet" {
  vpc_id                  = aws_vpc.packer_vpc.id
  cidr_block              = "10.50.1.0/24"
  map_public_ip_on_launch = true

  tags = {
    Name = "packer-temp-subnet"
  }
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.packer_vpc.id

  tags = {
    Name = "packer-temp-rt"
  }
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}

resource "aws_route_table_association" "rta" {
  subnet_id      = aws_subnet.packer_subnet.id
  route_table_id = aws_route_table.rt.id
}
