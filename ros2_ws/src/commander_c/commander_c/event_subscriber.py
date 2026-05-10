import json
import os
import sqlite3
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from commander_c.qwen_planner import QwenMissionPlanner


class CommanderCSubscriber(Node):
    def __init__(self):
        super().__init__('commander_c_subscriber')

        self.robot_a_subscriber = self.create_subscription(
            String,
            '/robot_a/event_summary',
            self.robot_a_callback,
            10
        )

        self.robot_b_subscriber = self.create_subscription(
            String,
            '/robot_b/event_summary',
            self.robot_b_callback,
            10
        )

        self.robot_a_command_publisher = self.create_publisher(
            String,
            '/robot_a/task_command',
            10
        )

        self.robot_b_command_publisher = self.create_publisher(
            String,
            '/robot_b/task_command',
            10
        )

        self.db_path = os.path.expanduser('~/tri_edge_rescue/db/mission_events.db')
        self.init_db()

        self.get_logger().info("[Commander C] Loading Qwen Mission Planner...")
        self.qwen_planner = QwenMissionPlanner()
        self.get_logger().info("[Commander C] Started with Qwen planner. Waiting for Robot A/B summaries...")

    def init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TEXT,
            robot_id TEXT,
            object TEXT,
            confidence REAL,
            x REAL,
            y REAL,
            risk_score INTEGER,
            decision TEXT,
            command TEXT,
            target_robot TEXT,
            llm_reason TEXT
        )
        """)

        # 기존 DB에 llm_reason 컬럼이 없을 경우 추가
        cursor.execute("PRAGMA table_info(event_summary)")
        columns = [row[1] for row in cursor.fetchall()]

        if "llm_reason" not in columns:
            cursor.execute("ALTER TABLE event_summary ADD COLUMN llm_reason TEXT")

        conn.commit()
        conn.close()

        self.get_logger().info(f"[Commander C] DB ready: {self.db_path}")

    def decide_command(self, detected_object, risk_score):
        if risk_score >= 7:
            return (
                "HIGH RISK: avoid or replan route",
                "avoid_area",
                "high_risk_detected"
            )

        if detected_object == "person":
            return (
                "VICTIM CANDIDATE: prioritize rescue target",
                "approach_victim",
                "victim_candidate_detected"
            )

        if detected_object == "obstacle":
            return (
                "OBSTACLE: update map and avoid",
                "update_map_and_avoid",
                "obstacle_detected"
            )

        return (
            "NORMAL: continue exploration",
            "continue_exploration",
            "normal_status"
        )

    def save_to_db(
        self,
        robot_id,
        detected_object,
        confidence,
        x,
        y,
        risk_score,
        decision,
        command,
        target_robot,
        llm_reason
    ):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO event_summary (
            received_at,
            robot_id,
            object,
            confidence,
            x,
            y,
            risk_score,
            decision,
            command,
            target_robot,
            llm_reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(timespec='seconds'),
            robot_id,
            detected_object,
            confidence,
            x,
            y,
            risk_score,
            decision,
            command,
            target_robot,
            llm_reason
        ))

        conn.commit()
        conn.close()
        return True

    def publish_task_command(self, target_robot, command, reason, risk_score, x, y, llm_reason):
        command_msg = {
            "target_robot": target_robot,
            "command": command,
            "reason": reason,
            "risk_score": risk_score,
            "target_position": {
                "x": x,
                "y": y
            },
            "llm_reason": llm_reason
        }

        msg = String()
        msg.data = json.dumps(command_msg, ensure_ascii=False)

        if target_robot == "A":
            self.robot_a_command_publisher.publish(msg)
        elif target_robot == "B":
            self.robot_b_command_publisher.publish(msg)

        self.get_logger().info(f"[Commander C] Command sent to Robot {target_robot}: {msg.data}")

    def process_summary(self, msg, expected_robot_id):
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            self.get_logger().error(f"[Commander C] Invalid JSON received: {msg.data}")
            return

        robot_id = data.get("robot_id", expected_robot_id)
        detected_object = data.get("object", "unknown")
        confidence = float(data.get("confidence", 0.0))
        position = data.get("position", {})
        x = float(position.get("x", 0.0))
        y = float(position.get("y", 0.0))
        risk_score = int(data.get("risk_score", 0))

        decision, command, reason = self.decide_command(detected_object, risk_score)

        try:
            llm_reason = self.qwen_planner.generate_reason(
                robot_id=robot_id,
                detected_object=detected_object,
                risk_score=risk_score,
                x=x,
                y=y,
                command=command
            )
        except Exception as e:
            llm_reason = f"LLM unavailable. Rule-based reason: {reason}"
            self.get_logger().error(f"[Commander C] Qwen generation failed: {e}")

        self.publish_task_command(
            target_robot=robot_id,
            command=command,
            reason=reason,
            risk_score=risk_score,
            x=x,
            y=y,
            llm_reason=llm_reason
        )

        saved = self.save_to_db(
            robot_id=robot_id,
            detected_object=detected_object,
            confidence=confidence,
            x=x,
            y=y,
            risk_score=risk_score,
            decision=decision,
            command=command,
            target_robot=robot_id,
            llm_reason=llm_reason
        )

        self.get_logger().info(
            f"[Commander C] Robot {robot_id} | "
            f"object={detected_object}, pos=({x}, {y}), risk={risk_score} | "
            f"decision={decision} | command={command} | "
            f"llm_reason={llm_reason} | saved_to_db={saved}"
        )

    def robot_a_callback(self, msg):
        self.process_summary(msg, "A")

    def robot_b_callback(self, msg):
        self.process_summary(msg, "B")


def main(args=None):
    rclpy.init(args=args)
    node = CommanderCSubscriber()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
