from setuptools import setup, find_packages

setup(
    name="prometheus-haproxy-log-exporter",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-haproxy-log-exporter = prometheus_haproxy_log_exporter.cli:main',
        ],
    },
)
