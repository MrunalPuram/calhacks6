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

    def on_connect(self, controller):
        print("Connected")

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print("Disconnected")

    def on_exit(self, controller):
        print("Exited")

    def on_frame(self, controller):
        global handle
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
           for gesture in frame.gestures():
               if gesture.type == Leap.Gesture.TYPE_SWIPE:
                swipe = SwipeGesture(gesture)
                print "  Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                        gesture.id, self.state_names[gesture.state],
                        swipe.position, swipe.direction, swipe.speed)
                if swipe.direction[0] <= 0:
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
                    time.sleep(swipe.speed/100)
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
                    time.sleep(swipe.speed/100)
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
                   print("circle")
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
                   print(self.last)
                   print(time.time() - self.last)
                   if clockwiseness == "clockwise" and time.time() - self.last > self.zoom_thresh:
                       print(self.last)
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
                       self.last = time.time()
                   elif clockwiseness == "counterclockwise" and time.time() - self.last > self.zoom_thresh:
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
                       self.last = time.time()
               print("here")

           #print(rf.next_joint)
           distr = euclidean(rt.next_joint, rf.next_joint)
           distl = euclidean(lt.next_joint, lf.next_joint)
           #scaling = rt.next_joint - lt.next_joint#euclidean(rt.next_joint, lt.next_joint)
           #print(rt.next_joint)
           #print(lt.next_joint)
           #print(scaling)
           #scaling = normalize(self.first, self.second, scaling)
           #print(distr)
           #print(scaling)
           if(distr <= self.thresh and distl <= self.thresh):
               print('PINCHING')
               rx = rt.next_joint.x + self.width/2
               lx = lt.next_joint.x + self.width/2
               rz = rt.next_joint.z + self.height/2
               lz = lt.next_joint.z + self.height/2
               #print("HI")
               deltarx = rx - (self.lastrt.next_joint.x + self.width/2)
               deltalx = lx - (self.lastlt.next_joint.x + self.width/2)
               rightdir = deltarx/abs(deltarx)
               leftdir = deltalx/abs(deltalx)
               print(rt.next_joint.x)
               print(self.lastrt.next_joint.x)

               rx = 0 if rx < 0 else rx
               #print("KO")
               rz = 0 if rz < 0 else rz
               #print("OK")
               lx = 0 if lx < 0 else lx
               lz = 0 if lz < 0 else lz
               print("BYE")
               rx = normalize(0,self.width,rx)*pyautogui.size()[0]
               lx = normalize(0,self.width,lx)*pyautogui.size()[0]
               rz = normalize(0,self.height,rz)*pyautogui.size()[1]
               lz = normalize(0,self.height,lz)*pyautogui.size()[1]
               #print("HI")
               gotox = int((rx+lx)/2)
               gotoy = int((rz+lz)/2)
               print("HI")
               pyautogui.moveTo(gotox, gotoy, duration=0)
               print(rightdir)
               print(leftdir)
               print("HI")
               if rightdir == 1 and leftdir == -1 and (abs(deltarx) > 4 or abs(deltalx) > 4):
                   pyautogui.scroll(100)
               elif rightdir == -1 and leftdir == 1 and (abs(deltarx) > 4 or abs(deltalx) > 4):
                   pyautogui.scroll(-100)
           else:
               xpos = rf.next_joint.x + self.width/2 #0 at the left
               ypos = rf.next_joint.z + self.height/2 #0 at the top
               xpos = 0 if xpos < 0 else xpos
               ypos = 0 if ypos < 0 else ypos
               pyautogui.moveTo(int(normalize(0,self.width,xpos)*pyautogui.size()[0]), int(normalize(0,self.height,ypos)*pyautogui.size()[1]), duration=0)

               #pyautogui.moveTo(0, 100, duration = 1)
           print("")
        except:
            return
        print("HELLO")
        print(rt.next_joint.x)
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
    print(handle)
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
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
