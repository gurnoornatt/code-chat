from setuptools import setup, find_packages

setup(
    name="ai-tutor-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "python-dotenv>=1.0.0",
        "supabase==1.0.3",
        "httpx==0.23.3",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "pytest>=7.4.4",
        "sentry-sdk>=1.39.1",
        "gotrue==1.0.1",
        "postgrest==0.10.6",
        "realtime==1.0.0",
        "storage3==0.5.2",
    ],
    python_requires=">=3.8",
) 