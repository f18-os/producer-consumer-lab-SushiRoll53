#!/usr/bin/env python3

from threading import Thread, Condition
import threading
import time
import random
import cv2
import numpy as np
import base64
from queue import Queue
# Max items a queue can have
MAX_NUM = 10


class Producer(threading.Thread):
    def __init__(self, queue, fileName, condition):
        Thread.__init__(self)
        self.queue = queue
        self.fileName = fileName
        self.condition = condition
        self.start()
    def run(self):
        # Initialize frame count
        count = 0
        # open video file
        vidcap = cv2.VideoCapture(self.fileName)
        # read first image
        success,image = vidcap.read()

        while True:
            # acquire() is the "lock"
            self.condition.acquire()
            if self.queue.qsize() == MAX_NUM:
                print ("Queue full, producer is waiting")
                self.condition.wait()
                print ("Space in queue, Consumer notified the producer")

            success, jpgImage = cv2.imencode('.jpg', image)
            #print(jpgImage)
            jpgAsText = base64.b64encode(jpgImage)

            self.queue.put(jpgAsText)
            self.condition.notify()
            # To release the acquire / "lock'
            self.condition.release()

            success,image = vidcap.read()

            print('Reading frame {} {}'.format(count, success))
            count += 1
            # Sleep a random time in ms
            time.sleep(random.uniform(0.03,0.06))


class Consumer(threading.Thread):
    def __init__(self, gqueue, condition2):
        Thread.__init__(self)
        self.gqueue = gqueue
        self.condition2 = condition2
        self.start()
    def run(self):
        count = 0
        while True:
            # acquire() is the "lock"
            self.condition2.acquire()
            if self.gqueue.empty():
                print ("Nothing in queue, consumer is waiting")
                self.condition2.wait()
                print ("Producer added something to queue and notified the consumer")

            frameAsText = self.gqueue.get()
            self.condition2.notify()
            # To release the acquire / "lock'
            self.condition2.release()

            jpgRawImage = base64.b64decode(frameAsText)

            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

            print("Displaying frame {}".format(count))

            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1
            # Sleep a random time in ms
            time.sleep(random.uniform(0.03,0.06))

        print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows()


class ConsumerProducer(threading.Thread):
    def __init__(self,queue,gqueue,condition,condition2):
        Thread.__init__(self)
        self.queue = queue
        self.gqueue = gqueue
        self.condition = condition
        self.condition2 = condition2
        self.start()
    def run(self):
        count = 0
        while True:
            # acquire() is the "lock"
            self.condition.acquire()
            if self.queue.empty():
                print ("Nothing in queue, consumer2 is waiting")
                self.condition.wait()
                print ("Producer added something to queue and notified the consumer")
            frameAsText = self.queue.get()
            self.condition.notify()
            # To release the acquire / "lock'
            self.condition.release()
            # Sleep a random time in ms
            time.sleep(random.uniform(0.03,0.06))

            # acquire() is the "lock"
            self.condition2.acquire()
            if self.gqueue.qsize() == MAX_NUM:
                print ("Queue full, producer2 is waiting")
                self.condition.wait()
                print ("Space in queue, Consumer notified the producer")


            jpgRawImage = base64.b64decode(frameAsText)

            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

            img = cv2.imdecode( jpgImage ,cv2.IMREAD_GRAYSCALE)

            success, jpgImage = cv2.imencode('.jpg', img)

            grayFrame = base64.b64encode(jpgImage)

            print("Converting frame {}".format(count))

            self.gqueue.put(grayFrame)


            count += 1
            self.condition2.notify()
            # To release the acquire / "lock'
            self.condition2.release()
            # Sleep a random time in ms
            time.sleep(random.uniform(0.03,0.06))



def main():
    # Colored queue
    queue = Queue(MAX_NUM)
    # Grayed queue
    gqueue = Queue(MAX_NUM)
    # I used condition for semaphores
    condition = Condition()
    condition2 = Condition()
    # Name of the clip
    fileName = 'clip.mp4'
    # Initialize and start threads
    Producer(queue,fileName,condition)
    ConsumerProducer(queue,gqueue,condition,condition2)
    Consumer(gqueue,condition2)
    queue.join()
    gqueue.join()
main()
