from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    robot_a_node = Node(
        package='robot_a_brain',
        executable='event_publisher',
        name='robot_a_brain',
        output='screen'
    )

    robot_b_node = Node(
        package='robot_b_brain',
        executable='event_publisher',
        name='robot_b_brain',
        output='screen'
    )

    commander_c_node = Node(
        package='commander_c',
        executable='event_subscriber',
        name='commander_c',
        output='screen'
    )

    return LaunchDescription([
        robot_a_node,
        robot_b_node,
        commander_c_node
    ])
