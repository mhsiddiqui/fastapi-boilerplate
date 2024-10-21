from fabric import task
from invoke import Collection


@task
def build(connection):
    connection.run(f"docker compose -f {connection['file']} build")


@task
def up(connection):
    connection.run(f"docker compose -f {connection['file']} up -d")


@task
def stop(connection):
    connection.run(f"docker compose -f {connection['file']} stop")


@task
def clean(connection):
    stop(connection)
    containers = [c for c in connection.run("docker ps -a -q").stdout.strip().split("\n") if c]
    if containers:
        connection.run("docker rm $(docker ps -a -q)")
    dangling_images = [
        di for di in connection.run('docker images -f "dangling=true" -q').stdout.strip().split("\n") if di
    ]
    if dangling_images:
        connection.run('docker rmi $(docker images -f "dangling=true" -q)')


@task
def logs(connection, service=""):
    connection.run(f"docker compose -f {connection['file']} logs -f --tail=500 {service}")


@task
def manage(connection, command, args=""):
    connection.run(f"docker compose -f {connection['file']} run --rm django python manage.py {command} {args}")


@task
def deploy(connection, branch="main"):
    clean(connection)
    current_branch = connection.run("git rev-parse --abbrev-ref HEAD").stdout.strip()
    if current_branch != branch:
        connection.run("git fetch")
        connection.run(f"git checkout {branch} --no-ff")
    connection.run(f"git pull origin {branch} --no-ff")
    build(connection)
    up(connection)


TASKS = [build, up, stop, logs, clean, deploy, manage]
local = Collection("local")
prod = Collection("prod")

for t in TASKS:
    local.add_task(t)
    prod.add_task(t)

local.configure({"file": "local.yml"})
prod.configure({"file": "production.yml"})
ns = Collection(local, prod)
