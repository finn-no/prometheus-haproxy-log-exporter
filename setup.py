#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="prometheus-haproxy-log-exporter",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-haproxy-log-exporter = prometheus_haproxy_log_exporter.cli:main',
        ],
    },
    # Requirements
    install_requires=[
         'configargparse',
         'prometheus-client',
         #'systemd', ??? Unknown which module this is
         'pygtail',
         'haproxy-log-analysis<2.0',
         #'pkg-resources', ??? Unknown which module this is
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest-sugar', 'pytest-html', 'pytest-cov', 'pytest'],
)
