from setuptools import setup

setup(
    package_data={
        'odm_report_shot_coverage': ['scripts/web/*']
    },
    include_package_data=True,
    entry_points={
        'console_scripts': ['odm-report-shot-coverage=odm_report_shot_coverage.scripts.report:main'],
    }
)
