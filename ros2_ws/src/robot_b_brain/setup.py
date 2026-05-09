from setuptools import find_packages, setup

package_name = 'robot_b_brain'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ys9072',
    maintainer_email='ys9072@todo.todo',
    description='Robot B brain package for Tri-Edge Rescue',
    license='TODO',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'event_publisher = robot_b_brain.event_publisher:main',
        ],
    },
)
