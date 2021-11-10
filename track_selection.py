import cv2
import numpy as np
from tkinter import ttk
from tkinter import filedialog
from tkinter import *
import tkinter as tk 
from tkinter import Tk
from numpy.core.defchararray import upper
import ctypes

user_depth = 0
user_color = 0
edges = np.zeros((2,2),np.int)
counter = 0


def get_edges():
    global col1, col2, image

    Tk().withdraw() 
    filename = filedialog.askopenfilename()
    im = cv2.imread(filename)

    #resize to fit window
    image = cv2.resize(im, (1000,800))

    #dialog with instructions
    ctypes.windll.user32.MessageBoxW(0, "Please select your desired track's left and right boundaries", "Color Curve Digitizer", 1)

    while True:

        for x in range (0,2):
                cv2.circle(image, (edges[x][0],edges[x][1]),2,(0,0,0),cv2.FILLED)

        if counter == 2:
        #collect first and last columns
            col1 = (edges[0][0])
            col2 = (edges[1][0])

            cv2.destroyAllWindows()

            break #continue once two edges are detected

        cv2.imshow("Image", image)
        cv2.setMouseCallback("Image", findEdges)
        cv2.waitKey(1)


def user_input_win():
    global user_depth, user_color, col1, col2, depth_entry, color_entry, r, color

    root = tk.Tk()
    root.title("Color Curve Digitizer")

    #center window
    w = 300
    h = 100
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    root.geometry('%dx%d+%d+%d' % (w,h,x,y))

    depth = tk.StringVar()

    #input frame
    entry = ttk.Frame(root)
    entry.pack(padx=5, pady=5, fill='x', expand=True)

    depth_label = ttk.Label(entry, text = "Please enter track depth and select track color", 
    anchor=tk.CENTER)
    depth_label.pack(fill='x', expand=True, pady=2)

    depth_entry = ttk.Entry(entry, textvariable=depth)
    depth_entry.pack(fill='x', expand=True)
    depth_entry.focus()

    colors = [('Green', 'G'),('Red', 'R'),('Blue', 'B'),('Black', 'BL')]
    color_entry = tk.StringVar(entry) #pass name of frame containing radiobuttons to update button variable
    color_entry.set(" ")

    for text, color in colors:
        ttk.Radiobutton(entry, text=text, variable=color_entry, value=color).pack(fill='x', padx=5, pady=5, side='left')

    #button
    digitize_button = ttk.Button(entry, text="Digitize", command=masking)
    digitize_button.pack(fill='x', expand=True, pady=10, anchor='s')

    root.mainloop()


def findEdges(event,x,y, flags, params):
    global counter, user_depth, user_color, col1, col2, depth_entry, color_entry, track_slice

    if event == cv2.EVENT_LBUTTONDOWN:
        edges[counter] = x,y
        counter = counter + 1


def masking():
    global user_depth, user_color, edges, col1, col2, color_entry
    #create img from track selection

    user_depth = depth_entry.get()
    user_color = color_entry.get()

    print("user_depth = ", user_depth)
    print("user_color = ", user_color)

    new_image = image[0:int(user_depth),int(col1):int(col2)]

    #convert selection to HSV for masking
    hsv = cv2.cvtColor(new_image, cv2.COLOR_BGR2HSV)

    #set color boundaries
    upper_green = np.array([180,255,235])
    lower_green = np.array([12,35,15])
    upper_blue = np.array([185, 185, 244])
    lower_blue = np.array([60, 50, 255])
    upper_red = np.array([10, 255, 255])
    lower_red = np.array([0, 100, 50])

    #create masks
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue) 
        
    #create masked images based on user color selection
    if user_color=='G':
        track_slice = cv2.bitwise_and(new_image, new_image, mask=green_mask)
        
    elif user_color=='R':
        track_slice = cv2.bitwise_and(new_image, new_image, mask=red_mask)
        
    elif user_color=='B':
        track_slice = cv2.bitwise_and(new_image, new_image, mask=blue_mask)

    ###send variable track_slice to digitizing program

    #cv2.namedWindow("mask", cv2.WINDOW_NORMAL)

    cv2.imshow("Selection", track_slice)

    #save masked image if desired
    cv2.imwrite("track_slice.png", track_slice, [cv2.IMWRITE_PNG_COMPRESSION, 0])

    #quit()


get_edges()
user_input_win()

