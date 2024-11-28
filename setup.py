from setuptools import setup

setup(
    name="caterpillar_world_saver",
    version="1.0.0",
    description="A 2D game where you control a caterpillar navigating through stages",
    author="Amit",
    packages=["caterpillar_world_saver"],
    install_requires=[
        "pygame==2.5.2",
        "numpy==1.26.4",
    ],
    entry_points={
        "console_scripts": [
            "caterpillar-game=caterpillar_world_saver.main:main",
        ],
    },
    python_requires=">=3.11",
)
