import rclpy
import signal
from rclpy.node import Node
from std_msgs.msg import String
import threading
from flask import Flask, render_template

class TestPublisher(Node):
    def __init__(self):
        super().__init__('test_publisher')
        self.publisher = self.create_publisher(String, 'flask_pub_topic', 10)
        self.subscription = self.create_subscription(
            String,
            '/topic',
            self.chatter_callback,
            10)
        self.latest_message = None

    def chatter_callback(self, msg):
        print(f'chatter cb received: {msg.data}')
        self.latest_message = msg.data

    def publish_message(self):
        msg = String()
        msg.data = 'hello, world!'
        self.publisher.publish(msg)


def ros2_thread(node):
    print('entering ros2 thread')
    rclpy.spin(node)
    print('leaving ros2 thread')


def sigint_handler(signal, frame):
    """
    SIGINT handler

    We have to know when to tell rclpy to shut down, because
    it's in a child thread which would stall the main thread
    shutdown sequence. So we use this handler to call
    rclpy.shutdown() and then call the previously-installed
    SIGINT handler for Flask
    """
    rclpy.shutdown()
    if prev_sigint_handler is not None:
        prev_sigint_handler(signal)


rclpy.init(args=None)
ros2_node = TestPublisher()
app = Flask(__name__)
prev_sigint_handler = signal.signal(signal.SIGINT, sigint_handler)

@app.route('/')
def index():
    return render_template("camera-view.html")


@app.route('/latest_message')
def get_current_time():
    return {'message': ros2_node.latest_message}

@app.route('/publish_message')
def get_publish_message():
    ros2_node.publish_message()
    return {}

def main():
    print('Hi from otomo_webserver.')
    threading.Thread(target=ros2_thread, args=[ros2_node]).start()
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)

if __name__ == '__main__':
    main()
