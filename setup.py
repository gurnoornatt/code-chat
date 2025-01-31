from setuptools import setup, find_packages

setup(
    name="ai-tutor-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=0.19.0",
        "supabase>=2.3.0",
        "httpx>=0.24.0,<0.25.0",
        "email-validator>=2.0.0"
    ],
    python_requires=">=3.8",
) 