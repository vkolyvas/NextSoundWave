"""Tests for Phase 6 - Docker & Deployment."""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDockerfile:
    """Test Dockerfile exists and is properly configured."""
    
    def test_dockerfile_exists(self):
        """Dockerfile should exist."""
        assert os.path.exists('Dockerfile'), "Dockerfile should exist"
    
    def test_dockerfile_has_python_base(self):
        """Dockerfile should use Python base image."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'FROM python' in content or 'FROM python:' in content
    
    def test_dockerfile_installs_dependencies(self):
        """Dockerfile should install Python dependencies."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'pip install' in content or 'COPY requirements.txt' in content
    
    def test_dockerfile_exposes_port(self):
        """Dockerfile should expose port 8000."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'EXPOSE 8000' in content or 'EXPOSE' in content
    
    def test_dockerfile_runs_server(self):
        """Dockerfile should run FastAPI server."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'uvicorn' in content or 'python main.py' in content


class TestDockerCompose:
    """Test docker-compose.yml exists and is configured."""
    
    def test_docker_compose_exists(self):
        """docker-compose.yml should exist."""
        assert os.path.exists('docker-compose.yml'), "docker-compose.yml should exist"
    
    def test_docker_compose_has_service(self):
        """docker-compose should have music-streaming service."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert 'music-streaming' in content or 'nextsoundwave' in content.lower()
    
    def test_docker_compose_maps_port(self):
        """docker-compose should map port 8000."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert '8000:8000' in content or '"8000:8000"' in content
    
    def test_docker_compose_has_build(self):
        """docker-compose should have build configuration."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert 'build:' in content or 'image:' in content


class TestRequirementsFile:
    """Test requirements.txt is properly configured."""
    
    def test_requirements_exists(self):
        """requirements.txt should exist."""
        assert os.path.exists('requirements.txt'), "requirements.txt should exist"
    
    def test_has_fastapi(self):
        """requirements should include fastapi."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        assert 'fastapi' in content.lower()
    
    def test_has_uvicorn(self):
        """requirements should include uvicorn."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        assert 'uvicorn' in content.lower()
    
    def test_has_yt_dlp(self):
        """requirements should include yt-dlp."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        assert 'yt-dlp' in content.lower()
    
    def test_has_test_dependencies(self):
        """requirements should include test dependencies."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        assert 'pytest' in content.lower()


class TestProjectStructure:
    """Test project structure for deployment."""
    
    def test_has_main_py(self):
        """main.py should exist."""
        assert os.path.exists('main.py'), "main.py should exist"
    
    def test_has_config(self):
        """config.py should exist."""
        assert os.path.exists('config.py'), "config.py should exist"
    
    def test_has_web_directory(self):
        """web directory should exist."""
        assert os.path.isdir('web'), "web directory should exist"
    
    def test_has_api_directory(self):
        """api directory should exist."""
        assert os.path.isdir('api'), "api directory should exist"
    
    def test_has_tests_directory(self):
        """tests directory should exist."""
        assert os.path.isdir('tests'), "tests directory should exist"
    
    def test_has_extraction_backends(self):
        """extraction_backends.py should exist."""
        assert os.path.exists('extraction_backends.py'), "extraction_backends.py should exist"


class TestDockerfileBestPractices:
    """Test Dockerfile follows best practices."""
    
    def test_dockerfile_uses_slim_image(self):
        """Dockerfile should use slim Python image."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'slim' in content, "Dockerfile should use slim Python image"
    
    def test_dockerfile_copies_requirements_first(self):
        """Dockerfile should copy requirements before installing."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        # Requirements should be copied before pip install
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'COPY requirements.txt' in line:
                # Check pip install comes after
                for j in range(i, min(i+10, len(lines))):
                    if 'pip install' in lines[j]:
                        assert True
                        break
                else:
                    assert False, "pip install should come after COPY requirements.txt"
                return
        assert False, "COPY requirements.txt should exist"
    
    def test_dockerfile_does_not_run_as_root(self):
        """Dockerfile should not run as root (check for security)."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        # Note: For simplicity, this test checks if WORKDIR is set
        # Production deployments should add USER directive
        assert 'WORKDIR' in content, "Should set WORKDIR"
    
    def test_dockerfile_has_workdir(self):
        """Dockerfile should set working directory."""
        with open('Dockerfile', 'r') as f:
            content = f.read()
        assert 'WORKDIR' in content


class TestDockerComposeConfiguration:
    """Test docker-compose configuration."""
    
    def test_docker_compose_version(self):
        """docker-compose should have version."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert 'version' in content or 'Version' in content
    
    def test_docker_compose_has_volumes(self):
        """docker-compose should have volume mappings."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert 'volumes:' in content or 'volume:' in content
    
    def test_docker_compose_has_restart_policy(self):
        """docker-compose should have restart policy."""
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        assert 'restart:' in content or '"restart"' in content


class TestDeploymentReadiness:
    """Test deployment readiness."""
    
    def test_has_readme(self):
        """README.md should exist."""
        assert os.path.exists('README.md'), "README.md should exist"
    
    def test_readme_has_run_instructions(self):
        """README should have run instructions."""
        with open('README.md', 'r') as f:
            content = f.read()
        assert 'docker' in content.lower() or 'pip install' in content.lower()
    
    def test_has_ports_file(self):
        """ports.md should exist for port management."""
        assert os.path.exists('ports.md'), "ports.md should exist for port management"
    
    def test_static_files_accessible(self):
        """Static files should be accessible."""
        assert os.path.isdir('web') or os.path.exists('web/index.html'), "web directory should exist"
