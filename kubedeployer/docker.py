import subprocess


class DockerError(Exception):
    pass


def docker_login(server: str, username: str, password: str):
    cmd = f"docker login -u {username} -p {password} {server}"
    result = subprocess.run(cmd, capture_output=True, shell=True)
    if result.returncode != 0:
        raise DockerError(result.stderr.decode("utf-8"))


def is_docker_login(server: str, username: str, password: str) -> bool:
    try:
        docker_login(server, username, password)
        return True
    except DockerError:
        return False
