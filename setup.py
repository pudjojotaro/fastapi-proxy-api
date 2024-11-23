from setuptools import setup, find_packages

setup(
    name="proxy_api",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'fastapi',
        'uvicorn',
        'python-dotenv',
        'typer'
    ],
    package_data={
        'proxy_api': ['handler.py', 'proxy_converter.py', 'proxies.txt'],
    },
    entry_points={
        'console_scripts': [
            'proxy-cli=proxy_cli:app',
        ],
    },
    python_requires='>=3.7',
) 