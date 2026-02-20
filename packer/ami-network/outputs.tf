output "vpc_id" {
  value = aws_vpc.packer_vpc.id
}

output "subnet_id" {
  value = aws_subnet.packer_subnet.id
}
