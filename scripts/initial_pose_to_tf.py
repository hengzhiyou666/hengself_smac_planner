#!/usr/bin/env python3
"""
订阅 /initialpose，收到后持续发布 map -> odom 的 TF。
用于无激光时让「2D Pose Estimate」设的起点立即生效（AMCL 无 /scan 时不发布 map->odom）。
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class InitialPoseToTF(Node):
    def __init__(self):
        super().__init__("initial_pose_to_tf")
        self._br = TransformBroadcaster(self)
        # 默认 (0,0,0)，收到 /initialpose 后改为用户设的位姿
        self._pose = None
        self._sub = self.create_subscription(
            PoseWithCovarianceStamped,
            "/initialpose",
            self._cb_initial_pose,
            10,
        )
        self._timer = self.create_timer(0.1, self._publish_tf)

    def _cb_initial_pose(self, msg: PoseWithCovarianceStamped):
        self._pose = msg.pose.pose

    def _publish_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = "map"
        t.child_frame_id = "odom"
        if self._pose is not None:
            t.transform.translation.x = self._pose.position.x
            t.transform.translation.y = self._pose.position.y
            t.transform.translation.z = self._pose.position.z
            t.transform.rotation.x = self._pose.orientation.x
            t.transform.rotation.y = self._pose.orientation.y
            t.transform.rotation.z = self._pose.orientation.z
            t.transform.rotation.w = self._pose.orientation.w
        else:
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.0
            t.transform.rotation.x = 0.0
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = 1.0
        self._br.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    node = InitialPoseToTF()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
