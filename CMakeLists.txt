cmake_minimum_required(VERSION 3.8)
project(smac_planner)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)

# 安装 for_launch 下文件到 share/.../launch（launch 文件在 for_launch/ 根下），一条命令: ros2 launch smac_planner all_in_one.launch.py
install(
  DIRECTORY for_launch/
  DESTINATION share/${PROJECT_NAME}/launch
  USE_SOURCE_PERMISSIONS
)

# 安装 config（nav2 参数与 rviz 配置）到 share/smac_planner/config
install(
  DIRECTORY config/
  DESTINATION share/${PROJECT_NAME}/config
)

# 安装 maps（pgm + yaml）到 share/smac_planner/maps
install(
  DIRECTORY maps/
  DESTINATION share/${PROJECT_NAME}/maps
)

# 安装 initial_pose_to_tf 脚本（无激光时由 2D Pose Estimate 发布 map->odom）
install(
  PROGRAMS scripts/initial_pose_to_tf.py
  DESTINATION share/${PROJECT_NAME}/scripts
  RENAME initial_pose_to_tf
)

ament_package()
