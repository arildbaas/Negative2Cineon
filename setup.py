from setuptools import setup, find_packages

setup(
    name="negative2cineon",
    version="0.1.0",
    description="Convert scanned RAW negatives to Cineon-style log TIFFs",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/negative2cineon",
    packages=find_packages(),
    py_modules=["convert_negative"],
    install_requires=[
        "rawpy",
        "numpy",
        "imageio",
        "matplotlib",
        "scikit-image"
    ],
    entry_points={
        'console_scripts': [
            'negative2cineon=convert_negative:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Capture",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)