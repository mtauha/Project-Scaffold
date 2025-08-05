import subprocess
import shutil


def collect():
    docker = {}
    try:
        if not shutil.which("docker"):
            docker["error"] = "docker CLI not installed"
            return docker

        docker_info = subprocess.run(["docker", "info"], capture_output=True, text=True)
        docker["info"] = docker_info.stdout

        ps = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True)
        docker["containers"] = ps.stdout

        images = subprocess.run(["docker", "images"], capture_output=True, text=True)
        docker["images"] = images.stdout

        volumes = subprocess.run(
            ["docker", "volume", "ls"], capture_output=True, text=True
        )
        docker["volumes"] = volumes.stdout

    except Exception as e:
        docker["error"] = str(e)
    return docker
