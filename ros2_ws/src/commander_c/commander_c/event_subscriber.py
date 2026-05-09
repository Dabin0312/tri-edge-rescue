import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CommanderCSubscriber(Node):
    def __init__(self):
        super().__init__('commander_c_subscriber')

        self.create_subscription(
            String,
            '/robot_a/event_summary',
            self.robot_a_callback,
            10
        )

        self.create_subscription(
            String,
            '/robot_b/event_summary',
            self.robot_b_callback,
            10
        )

        print("[Commander C] Started. Waiting for Robot A/B summaries...", flush=True)

    def robot_a_callback(self, msg):
        self.handle_event("A", msg.data)

    def robot_b_callback(self, msg):
        self.handle_event("B", msg.data)

    def handle_event(self, robot_id, data):
        try:
            event = json.loads(data)

            detected_object = event.get("object", "unknown")
            risk_score = event.get("risk_score", 0)
            position = event.get("position", {})
            x = position.get("x")
            y = position.get("y")

            if risk_score >= 7:
                decision = "HIGH RISK: avoid or replan route"
            elif detected_object == "person":
                decision = "VICTIM CANDIDATE: prioritize rescue target"
            elif detected_object == "obstacle":
                decision = "OBSTACLE: update map and avoid"
            else:
                decision = "NORMAL: continue exploration"

            print(
                f"[Commander C] Robot {robot_id} | "
                f"object={detected_object}, "
                f"pos=({x}, {y}), "
                f"risk={risk_score} | "
                f"decision={decision}",
                flush=True
            )

        except Exception as e:
            print(f"[Commander C] Error from Robot {robot_id}: {e}", flush=True)
            print(f"Raw data: {data}", flush=True)


def main(args=None):
    rclpy.init(args=args)
    node = CommanderCSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
