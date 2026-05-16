# main.tf - Infrastructure as Code for NextStep

provider "aws" {
  region = "us-east-1"
}

# Variable to switch between environments (dev, staging, prod)
variable "environment" {
  description = "Target environment (dev, staging, prod)"
  default     = "dev"
}

# 1. S3 Bucket for Resumes (Isolated per environment)
resource "aws_s3_bucket" "resume_bucket" {
  bucket = "nextstep-resumes-${var.environment}-bucket"
  
  tags = {
    Name        = "NextStep Resumes"
    Environment = var.environment
  }
}

# 2. EC2 Instance for the Backend (Isolated per environment)
resource "aws_instance" "app_server" {
  ami           = "ami-0c7217cdde317cfec" # Ubuntu AMI
  instance_type = var.environment == "prod" ? "t2.medium" : "t2.micro" # Bigger server for prod
  
  tags = {
    Name        = "NextStep-Backend-${var.environment}"
    Environment = var.environment
  }
}
