from rqt_gui_py.plugin import Plugin
import python_qt_binding.QtGui as QtGui
from python_qt_binding.QtGui import QAction, QIcon, QMenu, QWidget, \
QPainter, QColor, QFont, QBrush, QPen, QMessageBox, QSizePolicy, \
QLabel, QComboBox
from python_qt_binding.QtCore import Qt, QTimer, qWarning, Slot, QEvent, QSize
from threading import Lock
import rospy
import python_qt_binding.QtCore as QtCore
from std_msgs.msg import Bool, Time
import math
from resource_retriever import get_filename
import yaml
import os, sys

from std_msgs.msg import String

class StringLabel(Plugin):
    """
    rqt plugin to provide simple label
    """
    def __init__(self, context):
        super(StringLabel, self).__init__(context)
        self.setObjectName("StringLabel")
        self._widget = StringLabelWidget()
        context.add_widget(self._widget)
    def save_settings(self, plugin_settings, instance_settings):
        self._widget.save_settings(plugin_settings, instance_settings)
    def restore_settings(self, plugin_settings, instance_settings):
        self._widget.restore_settings(plugin_settings, instance_settings)


class StringLabelWidget(QWidget):
    def __init__(self):
        super(StringLabelWidget, self).__init__()
        self.lock = Lock()
        vbox = QtGui.QVBoxLayout(self)
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored))
        self.combo_box = QComboBox(self)
        self.combo_box.activated.connect(self.onActivated)
        vbox.addWidget(self.combo_box)
        vbox.addWidget(self.label)
        self.string_sub = None
        self._string_topics = []
        self._update_topic_timer = QTimer(self)
        self._update_topic_timer.timeout.connect(self.updateTopics)
        self._update_topic_timer.start(1)
        self._active_topic = None
    def updateTopics(self):
        need_to_update = False
        for (topic, topic_type) in rospy.get_published_topics():
            if topic_type == "std_msgs/String":
                if not topic in self._string_topics:
                    self._string_topics.append(topic)
                    need_to_update = True
        if need_to_update:
            self._string_topics = sorted(self._string_topics)
            self.combo_box.clear()
            for topic in self._string_topics:
                self.combo_box.addItem(topic)
            if self._active_topic:
                self.combo_box.setCurrentIndex(self._string_topics.index(self._active_topic))
    def setupSubscriber(self, topic):
        if self.string_sub:
            self.string_sub.unregister()
        self.image_sub = rospy.Subscriber(topic, String,
                                          self.stringCallback)
        self._active_topic = topic
    def onActivated(self, number):
        self.setupSubscriber(self._string_topics[number])
    def stringCallback(self, msg):
        self.string = msg.data
        self.label.setText(self.string)
    def save_settings(self, plugin_settings, instance_settings):
        if self._active_topic:
            instance_settings.set_value("active_topic", self._active_topic)
    def restore_settings(self, plugin_settings, instance_settings):
        if instance_settings.value("active_topic"):
            topic = instance_settings.value("active_topic")
            self.combo_box.addItem(topic)
            self.setupSubscriber(topic)

    








