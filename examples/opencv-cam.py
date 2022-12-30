import cv2

from faces import *

# Open the device at the ID 0
# Use the camera ID based on
# /dev/videoID needed
cap = cv2.VideoCapture(0)

#Check if camera was opened correctly
if not (cap.isOpened()):
    print("Could not open video device")

# 1920x1080
#Set the resolution
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Capture frame-by-frame
while(True):
    ret, frame = cap.read()

    # Display the resulting frame

#    cv2.imshow("INOUT-preview",frame)


    output_frame = find_and_mark_faces(frame)
    cv2.imshow("OUPUT-preview",output_frame)


    #cv2.imwrite("outputImage.jpg", frame)

    #Waits for a user input to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
