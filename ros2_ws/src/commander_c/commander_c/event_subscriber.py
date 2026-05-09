import json
import os
import sqlite3
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class CommanderCSubscriber(Node):
    def __init__(self):
        super().__init__('commander_c_subscriber')

        home_dir = os.path.expanduser("~")
        db_dir = os.path.join(home_dir, "tri_edge_rescue", "db")
        os.makedirs(db_dir, exist_ok=True)

        self.db_path = os.path.join(db_dir, "mission_events.db")
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

        self.robot_a_command_pub = self.create_publisher(
            String,
            '/robot_a/task_command',
            10
        )

        self.robot_b_command_pub = self.create_publisher(
            String,
            '/robot_b/task_command',
            10
        )

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
        print(f"[Commander C] DB path: {self.db_path}", flush=True)

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TEXT,
                robot_id TEXT,
                object TEXT,
                confidence REAL,
                x REAL,
                y REAL,
                risk_score INTEGER,
                event TEXT,
                decision TEXT,
                command TEXT,
                target_robot TEXT,
                raw_json TEXT
            )
        """)

        existing_columns = [
            row[1] for row in self.cursor.execute("PRAGMA table_info(event_summary)")
        ]

        if "command" not in existing_columns:
            self.cursor.execute("ALTER TABLE event_summary ADD COLUMN command TEXT")

        if "target_robot" not in existing_columns:
            self.cursor.execute("ALTER TABLE event_summary ADD COLUMN target_robot TEXT")

        self.conn.commit()

    def robot_a_callback(self, msg):
        self.handle_event("A", msg.data)

    def robot_b_callback(self, msg):
        self.handle_event("B", msg.data)

    def make_decision_and_command(self, robot_id, detected_object, risk_score, position):
        if risk_score >= 7:
            decision = "HIGH RISK: avoid or replan route"
            command = {
                "target_robot": robot_id,
                "command": "avoid_area",
                "reason": "high_risk_detected",
                "risk_score": risk_score,
                "target_position": position
            }

        elif detected_object == "person":
            decision = "VICTIM CANDIDATE: prioritize rescue target"
            command = {
                "target_robot": robot_id,
                "command": "approach_victim",
                "reason": "victim_candidate_detected",
                "risk_score": risk_score,
                "target_position": position
            }

        elif detected_object == "obstacle":
            decision = "OBSTACLE: update map and avoid"
            command = {
                "target_robot": robot_id,
                "command": "update_map_and_avoid",
                "reason": "obstacle_detected",
                "risk_score": risk_score,
                "target_position": position
            }

        else:
            decision = "NORMAL: continue exploration"
            command = {
                "target_robot": robot_id,
                "command": "continue_exploration",
                "reason": "normal_status",
                "risk_score": risk_score,
                "target_position": position
            }

        return decision, command

    def publish_command(self, robot_id, command):
        msg = String()
        msg.data = json.dumps(command, ensure_ascii=False)

        if robot_id == "A":
            self.robot_a_command_pub.publish(msg)
        elif robot_id == "B":
            self.robot_b_command_pub.publish(msg)

        print(
            f"[Commander C] Command sent to Robot {robot_id}: {msg.data}",
            flush=True
        )

    def save_event(self, event, decision, command, raw_json):
        position = event.get("position", {})

        self.cursor.execute("""
            INSERT INTO event_summary (
                received_at,
                robot_id,
                object,
                confidence,
                x,
                y,
                risk_score,
                event,
                decision,
                command,
                target_robot,
                raw_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec="seconds"),
            event.get("robot_id"),
            event.get("object"),
            event.get("confidence"),
            position.get("x"),
            position.get("y"),
            event.get("risk_score"),
            event.get("event"),
            decision,
            command.get("command"),
            command.get("target_robot"),
            raw_json
        ))

        self.conn.commit()

    def handle_event(self, robot_id, data):
        try:
            event = json.loads(data)

            detected_object = event.get("object", "unknown")
            risk_score = event.get("risk_score", 0)
            position = event.get("position", {})
            x = position.get("x")
            y = position.get("y")

            decision, command = self.make_decision_and_command(
                robot_id,
                detected_object,
                risk_score,
                position
            )

            self.save_event(event, decision, command, data)
            self.publish_command(robot_id, command)

            print(
                f"[Commander C] Robot {robot_id} | "
                f"object={detected_object}, "
                f"pos=({x}, {y}), "
                f"risk={risk_score} | "
                f"decision={decision} | "
                f"command={command.get('command')} | "
                f"saved_to_db=True",
                flush=True
            )

        except Exception as e:
            print(f"[Commander C] Error from Robot {robot_id}: {e}", flush=True)
            print(f"Raw data: {data}", flush=True)

    def destroy_node(self):
        self.conn.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CommanderCSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
