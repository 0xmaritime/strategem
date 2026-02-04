from setuptools import setup, find_packages

setup(
    name="strategem",
    version="2.0.0-dev",
    description="Decision Support System with Independent Analytical Frameworks (V1 stable, V2 in development)",
    packages=find_packages(),
    install_requires=[
        "openrouter>=0.1.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "markdown>=3.5",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "jinja2>=3.1.0",
        "python-multipart>=0.0.6",
        "aiofiles>=23.2.0",
    ],
    entry_points={
        "console_scripts": [
            "strategem=strategem.cli:main",
            "strategem-web=strategem.web.app:main",
        ],
    },
    python_requires=">=3.8",
)
