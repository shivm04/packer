terraform {
  backend "s3" {
    bucket       = "dce-demo-terraform-state-bucket"
    key          = "packer/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}