from threading import Thread, Condition
import threading
import time
import random
import cv2
import numpy as np
import base64
import queue

queue =[]
gqueue = []
MAX_NUM = 10
condition = Condition()
condition2 = Condition()

class Producer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        global queue
        global fileName
        # Initialize frame count 
        count = 0
        # open video file
        vidcap = cv2.VideoCapture(fileName)
        # read first image
        success,image = vidcap.read()
        
        while True:
            condition.acquire()
            if len(queue) == MAX_NUM:
                print ("Queue full, producer is waiting")
                condition.wait()
                print ("Space in queue, Consumer notified the producer")

            success, jpgImage = cv2.imencode('.jpg', image)
            #print(jpgImage)
            jpgAsText = base64.b64encode(jpgImage)

            queue.append(jpgAsText)
            condition.notify()
            condition.release()
            
            success,image = vidcap.read()
                
            print('Reading frame {} {}'.format(count, success))
            count += 1

            time.sleep(random.random())


class Consumer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        global gqueue
        count = 0
        while True:
            condition2.acquire()
            if not gqueue:
                print ("Nothing in queue, consumer is waiting")
                condition2.wait()
                print ("Producer added something to queue and notified the consumer")

            frameAsText = gqueue.pop(0)
            condition2.notify()
            condition2.release()

            jpgRawImage = base64.b64decode(frameAsText)
     
            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
     
            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)
        
            print("Displaying frame {}".format(count))

            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1

            time.sleep(random.random())

        print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows()


class ConsumerProducer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        global gqueue, queue
        count = 0
        while True:
            condition.acquire()
            if not queue:
                print ("Nothing in queue, consumer2 is waiting")
                condition.wait()
                print ("Producer added something to queue and notified the consumer")
            frameAsText = queue.pop(0)
            condition.notify()
            condition.release()
            time.sleep(random.random())

            condition2.acquire()
            if len(gqueue) == MAX_NUM:
                print ("Queue full, producer2 is waiting")
                condition.wait()
                print ("Space in queue, Consumer notified the producer")

                
            jpgRawImage = base64.b64decode(frameAsText)

            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
            
            img = cv2.imdecode( jpgImage ,cv2.IMREAD_GRAYSCALE)
            
            success, jpgImage = cv2.imencode('.jpg', img)
            
            grayFrame = base64.b64encode(jpgImage)
            
            print("Converting frame {}".format(count))

            gqueue.append(grayFrame)

            
            count += 1
            condition2.notify()
            condition2.release()
            time.sleep(random.random())



fileName = 'clip.mp4'

Producer()
ConsumerProducer()
Consumer()
