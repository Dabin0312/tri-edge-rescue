import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess


def generate_launch_description():
    world_path = os.path.join(
        get_package_share_directory('tri_edge_worlds'),
        'worlds',
        'rescue_lab.world'
    )

    gazebo = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            '-s',
            'libgazebo_ros_init.so',
            '-s',
            'libgazebo_ros_factory.so',
            world_path
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo
    ])
