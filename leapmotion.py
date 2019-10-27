#!c:/Python27/python.exe
################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import sys
sys.path.append('C:\\Users\\User\\Documents\\Berkeley\\calhacks\\leapmotion\\LeapDeveloperKit_2.3.1+31549_win\\LeapSDK\\lib\\x64')
import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import pyautogui
import subprocess
import win32con
import win32api
import win32gui
import win32process

def euclidean(a, b):
    return (a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2
def normalize(first, second, scaling):
    if scaling <= first:
        scaling = first
    if scaling >= second:
        scaling = second
    scaling = (scaling-first)/(second-first)
    return scaling

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    thresh = 1000
    first = 2000
    second = 50000
    width = 640
    height = 400
    scrolldir = 1
    lastrt, lastlt = None, None
    circling = False
    moving = 0
    zoom_thresh = 0.5
    last = time.time()
    def on_init(self, controller):
        print("Initialized")
        sys.stdout.flush()

    def on_connect(self, controller):
        print("Connected")
        sys.stdout.flush()

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")
        sys.stdout.flush()

    def on_exit(self, controller):
        print("Exited")
        sys.stdout.flush()

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        rt, lt, rf, lf = None, None, None, None
        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"


            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction


            # Get arm bone
            arm = hand.arm


            # Get fingers
            for finger in hand.fingers:


                # Get bones
                for b in range(0, 4):
                    bone = finger.bone(b)
                    if self.finger_names[finger.type] == 'Thumb' and self.bone_names[bone.type]=='Distal':
                        if handType == "Left hand":
                            lt = bone
                        else:
                            rt = bone
                    elif self.finger_names[finger.type] == 'Index' and self.bone_names[bone.type]=='Distal':
                        if handType == "Left hand":
                            lf = bone
                        else:
                            rf = bone
        distr, distl, scaling = 0, 0, 0
        try:
           nothing = True
           for gesture in frame.gestures():
               if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                nothing = False
                # print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                #         gesture.id, self.state_names[gesture.state],
                #         swipe.position, swipe.direction, swipe.speed)
                if swipe.direction[0] <= 0:
                    print("swipe_left")
                    sys.stdout.flush()
                    #TODO: Change leap motion code to dict update
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYDOWN,
                    win32con.VK_LEFT,
                    0)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYUP,
                    win32con.VK_LEFT,
                    0)
                    time.sleep(0.5)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYDOWN,
                    win32con.VK_RIGHT,
                    0)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYUP,
                    win32con.VK_RIGHT,
                    0)
                else:
                    #TODO: Change leap motion code to dict update
                    print("swipe_right")
                    sys.stdout.flush()
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYDOWN,
                    win32con.VK_RIGHT,
                    0)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYUP,
                    win32con.VK_RIGHT,
                    0)
                    time.sleep(0.5)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYDOWN,
                    win32con.VK_LEFT,
                    0)
                    win32api.PostMessage(
                    self.handle['FREEGLUT'],
                    win32con.WM_KEYUP,
                    win32con.VK_LEFT,
                    0)
               if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                   circle = CircleGesture(gesture)
                   if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                       clockwiseness = "clockwise"
                   else:
                       clockwiseness = "counterclockwise"
                   swept_angle = 0
                   if circle.state != Leap.Gesture.STATE_START:
                       previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                       swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI
                   degrees = swept_angle * Leap.RAD_TO_DEG
                   if clockwiseness == "clockwise" and time.time() - self.last > self.zoom_thresh:
                       #TODO: Change leap motion code to dict update
                       print("zoom_in")
                       sys.stdout.flush()
                       win32api.PostMessage(
                       self.handle['FREEGLUT'],
                       win32con.WM_CHAR,
                       ord("="),
                       0)
                       win32api.PostMessage(
                       self.handle['FREEGLUT'],
                       win32con.WM_CHAR,
                       ord("="),
                       0)
                       time.sleep(0.5)
                       self.last = time.time()
                   elif clockwiseness == "counterclockwise" and time.time() - self.last > self.zoom_thresh:
                       #TODO: Change leap motion code to dict update
                       print("zoom_out")
                       sys.stdout.flush()
                       win32api.PostMessage(
                       self.handle['FREEGLUT'],
                       win32con.WM_CHAR,
                       ord("-"),
                       0)
                       win32api.PostMessage(
                       self.handle['FREEGLUT'],
                       win32con.WM_CHAR,
                       ord("-"),
                       0)
                       time.sleep(0.5)
                       self.last = time.time()
           if nothing:
               print("idle")
               sys.stdout.flush()
        except:
            return
        self.lastrt, self.lastlt = rt, lt


    def add_handle(self, handle):
        self.handle = handle
    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def left():
    win32api.PostMessage(
    handle['FREEGLUT'],
    win32con.WM_KEYDOWN,
    win32con.VK_LEFT,
    0)
    win32api.PostMessage(
    handle['FREEGLUT'],
    win32con.WM_KEYUP,
    win32con.VK_LEFT,
    0)
    win32api.PostMessage(
    handle['FREEGLUT'],
    win32con.WM_CHAR,
    ord("f"),
    0)

def main():
    # proc = subprocess.Popen("C:\\Program Files (x86)\\Leap Motion\\Core Services\\VisualizerApp.exe", stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    # time.sleep(1)
    # try:
    #     proc.stdin.write(b'f')
    # except:
    #     print("Killing")
    #     proc.kill()
    _, cmd = win32api.FindExecutable('"C:\\Program Files (x86)\\Leap Motion\\Core Services\\VisualizerApp.exe"')
    time.sleep(1)
    _, _, pid, tid = win32process.CreateProcess(
        None,    # name
        cmd,     # command line
        None,    # process attributes
        None,    # thread attributes
        0,       # inheritance flag
        0,       # creation flag
        None,    # new environment
        None,    # current directory
        win32process.STARTUPINFO ())
    def wcallb(hwnd, handle):
        handle[win32gui.GetClassName(hwnd)] = hwnd
        win32gui.EnumChildWindows(hwnd, wcallb, handle)
        return True
    handle = {}
    while not handle:   # loop until the window is loaded
        time.sleep(0.5)
        win32gui.EnumThreadWindows(tid, wcallb, handle)
    win32api.PostMessage(
    handle['FREEGLUT'],
    win32con.WM_CHAR,
    ord("f"),
    0)
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()
    listener.add_handle(handle)

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print("Press Enter to quit...")
    sys.stdout.flush()
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
