data "aws_ami" "latest_custom" {
  most_recent = true
  owners      = ["self"]

  filter {
    name   = "tag:BuiltBy"
    values = ["Packer-GitHub-Actions"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_launch_template" "lt" {
  name_prefix   = "custom-lt-"
  image_id      = data.aws_ami.latest_custom.id
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.web_sg.id]
}

resource "aws_autoscaling_group" "asg" {
  desired_capacity    = 1
  max_size            = 2
  min_size            = 1
  vpc_zone_identifier = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  launch_template {
    id      = aws_launch_template.lt.id
    version = "$Latest"
  }

  target_group_arns = [aws_lb_target_group.tg.arn]
}
