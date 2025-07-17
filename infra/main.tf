provider "aws" {
  region = var.aws_region
}

# VPC, subnets, and networking
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  name    = "mini-artemis-vpc"
  cidr    = "10.0.0.0/16"
  azs     = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
  enable_nat_gateway = true
  single_nat_gateway = true
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "mini-artemis-cluster"
}

# RDS PostgreSQL
module "db" {
  source  = "terraform-aws-modules/rds/aws"
  identifier = "mini-artemis-db"
  engine = "postgres"
  engine_version = "15"
  instance_class = "db.t4g.micro"
  allocated_storage = 20
  username = var.db_username
  password = var.db_password
  db_name  = "mini_artemis"
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  subnet_ids = module.vpc.private_subnets
  publicly_accessible = false
  skip_final_snapshot = true
}

# ElastiCache Redis
module "redis" {
  source  = "terraform-aws-modules/elasticache/aws"
  name                = "mini-artemis-redis"
  engine              = "redis"
  node_type           = "cache.t4g.micro"
  num_cache_nodes     = 1
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnets
  security_group_ids  = [module.vpc.default_security_group_id]
}

# Task Execution Role (minimal)
resource "aws_iam_role" "ecs_task_execution" {
  name = "mini-artemis-ecs-task-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Effect = "Allow"
    }]
  })
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
  ]
}

# ECS Task Definition (app container, add celery/flower as needed)
resource "aws_ecs_task_definition" "main" {
  family                   = "mini-artemis"
  cpu                      = 512
  memory                   = 1024
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  container_definitions    = jsonencode([
    {
      name  = "app"
      image = var.app_image  # e.g. ghcr.io/youruser/mini-artemis:latest
      essential = true
      portMappings = [{ containerPort = 8000 }]
      environment = [
        { name = "POSTGRES_URL", value = module.db.db_instance_endpoint },
        { name = "REDIS_URL", value = module.redis.primary_endpoint_address },
        # Add other envs
      ]
    }
  ])
}

resource "aws_ecs_service" "main" {
  name            = "mini-artemis-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  launch_type     = "FARGATE"
  desired_count   = 1
  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [module.vpc.default_security_group_id]
    assign_public_ip = true
  }
}
