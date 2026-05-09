import json
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotBEventPublisher(Node):
    def __init__(self):
        super().__init__('robot_b_event_publisher')

        self.publisher_ = self.create_publisher(
            String,
            '/robot_b/event_summary',
            10
        )

        self.command_subscriber = self.create_subscription(
            String,
            '/robot_b/task_command',
            self.command_callback,
            10
        )

        self.timer = self.create_timer(1.0, self.publish_event)
        self.count = 0
        self.last_command = "none"

        self.get_logger().info("Robot B Brain started. Waiting for task commands...")

    def command_callback(self, msg):
        try:
            command = json.loads(msg.data)
            self.last_command = command.get("command", "unknown")

            self.get_logger().info(
                f"Robot B received command: {msg.data}"
            )

        except json.JSONDecodeError:
            self.get_logger().error(f"Robot B received invalid command: {msg.data}")

    def publish_event(self):
        self.count += 1

        event = {
            "robot_id": "B",
            "timestamp": self.count,
            "object": random.choice(["person", "obstacle", "hazard"]),
            "confidence": round(random.uniform(0.75, 0.98), 2),
            "position": {
                "x": round(random.uniform(0.0, 10.0), 2),
                "y": round(random.uniform(0.0, 10.0), 2)
            },
            "risk_score": random.randint(1, 9),
            "event": "local_detection_summary",
            "last_command": self.last_command
        }

        msg = String()
        msg.data = json.dumps(event, ensure_ascii=False)
        self.publisher_.publish(msg)

        self.get_logger().info(f"Robot B summary published: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = RobotBEventPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
