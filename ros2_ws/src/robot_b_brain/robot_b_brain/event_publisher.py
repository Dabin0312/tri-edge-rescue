import json
import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class RobotBEventPublisher(Node):
    def __init__(self):
        super().__init__('robot_b_event_publisher')
        self.publisher_ = self.create_publisher(String, '/robot_b/event_summary', 10)
        self.timer = self.create_timer(1.0, self.publish_event)
        self.count = 0

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
            "event": "local_detection_summary"
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
