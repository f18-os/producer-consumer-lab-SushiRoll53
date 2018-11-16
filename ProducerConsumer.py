from threading import Thread, Condition
import time
import random
import cv2
import numpy as np
import base64
import queue

queue =[]
MAX_NUM = 10
condition = Condition()

class Producer(Thread):
    def run(self):
        global queue
        global fileName
        # Initialize frame count 
        count = 0
        # open video file
        vidcap = cv2.VideoCapture(fileName)
        # read first image
        success,image = vidcap.read()
        
        while success:
            condition.acquire()
            if len(queue) == MAX_NUM:
                print ("Queue full, producer is waiting")
                condition.wait()
                print ("Space in queue, Consumer notified the producer")

            success, jpgImage = cv2.imencode('.jpg', image)

            jpgAsText = base64.b64encode(jpgImage)

            queue.append(jpgAsText)

            success,image = vidcap.read()
                
            # num = random.choice(nums)
            # queue.append(num)
            print('Reading frame {} {}'.format(count, success))
            count += 1
            condition.notify()
            condition.release()
            time.sleep(random.random())


class Consumer(Thread):
    def run(self):
        global queue
        count = 0
        while True:
            condition.acquire()
            if not queue:
                print ("Nothing in queue, consumer is waiting")
                condition.wait()
                print ("Producer added something to queue and notified the consumer")

            frameAsText = queue.pop(0)
            
            jpgRawImage = base64.b64decode(frameAsText)

            jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

            img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

            print("Displaying frame {}".format(count))

            cv2.imshow("Video", img)
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break

            count += 1
            condition.notify()
            condition.release()
            time.sleep(random.random())

        print("Finished displaying all frames")
        # cleanup the windows
        cv2.destroyAllWindows()

        

fileName = 'clip.mp4'

#queue = queue.Queue()

Producer().start()

Consumer().start()
