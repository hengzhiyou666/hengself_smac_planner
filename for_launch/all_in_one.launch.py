#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('smac_planner')

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_dir, 'maps', '111.yaml'),
        description='Full path to map yaml',
    )
    declare_params = DeclareLaunchArgument(
        'params_file',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_params.yaml'),
        description='Full path to nav2 params yaml',
    )
    declare_rviz = DeclareLaunchArgument(
        'rviz_config',
        default_value=os.path.join(pkg_dir, 'config', 'nav2_default_view.rviz'),
        description='Full path to rviz config',
    )

    # map->odom 由 initial_pose_to_tf 在收到 /initialpose 时发布（无激光时 AMCL 不发布）
    initial_pose_to_tf = ExecuteProcess(
        cmd=['python3', os.path.join(pkg_dir, 'scripts', 'initial_pose_to_tf')],
        output='screen',
    )
    # 只发布 odom -> base_link
    tf_odom_base = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_odom_base',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link'],
    )

    # 定位：map_server + amcl（官方 launch）
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    localization_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'localization_launch.py')
        ),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': LaunchConfiguration('params_file'),
            'use_composition': 'False',
            'use_sim_time': 'false',
        }.items(),
    )

    # 导航：不含 smoother_server，避免其激活失败导致整栈起不来
    nav_no_smoother = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch', 'navigation_launch_no_smoother.py')
        ),
        launch_arguments={
            'params_file': LaunchConfiguration('params_file'),
            'use_sim_time': 'false',
        }.items(),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        output='screen',
    )

    return LaunchDescription([
        declare_map,
        declare_params,
        declare_rviz,
        initial_pose_to_tf,
        tf_odom_base,
        localization_launch,
        nav_no_smoother,
        rviz_node,
    ])
