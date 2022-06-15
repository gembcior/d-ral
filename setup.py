import setuptools


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()


setuptools.setup(
    name="dral",
    author="Gembcior",
    author_email="gembcior@gmail.com",
    description="D-RAL - Device Register Access Layer",
    url="https://github.com/gembcior/d-ral",
    long_description_content_type="text/markdown",
    long_description=readme,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.8',
    ],
    license="MIT",
    python_requires='>=3.6',
    setup_requires=['setuptools_scm'],
    install_requires=[
        'svd2py',
        'rich',
    ],
    extras_require={
        'tests': [
            'pyyaml',
            'pytest',
            'pytest-sugar',
            'pytest-cov',
            'pytest-clarity',
        ],
    },
    use_scm_version=True,
    include_package_data=True,
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            "dral = dral.app:main",
        ]
    },
)
