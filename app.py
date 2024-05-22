from tkinter import *
import cv2
import pafy
from PIL import Image, ImageTk
import os
import glob

# # clear all previous files
if not os.path.exists('images'): os.makedirs('images')
else: 
    for f in glob.glob('images/*'): 
        os.remove(f)
if not os.path.exists('app_images'): os.makedirs('app_images')
else:
    for f in glob.glob('app_images/*'): os.remove(f)

# fetch files for the time app
url='https://www.youtube.com/watch?v=Gh9bGHhQxhQ' # change url accordingly
skip=float(input('how many seconds to skip intro: '))
video = pafy.new(url)
best = video.getbest(preftype="mp4")
cap = cv2.VideoCapture(best.url)
count = 0
if(skip>0): 
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(30*skip))
    count+=int(30*skip)
end=count+600
path = "app_images"
print('fetching screenshots')
while cap.isOpened() and count <= end:
    ret, frame = cap.read()

    if ret:
        filename=url[url.index('watch?v=')+8:]
        name = path + "./"+ filename + "{:05d}".format(count) + ".jpg"
        frame=cv2.resize(frame,(700,int(700/frame.shape[1]*frame.shape[0])))
        cv2.imwrite(name, frame)
        count += int(10) # 30 fps
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    else:
        cap.release()
        break

# time app picks the duration between frames for the tab
class TimeApp(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        self.frame1 = Frame(self)
        self.original = Image.open('app_images/'+os.listdir('app_images')[0])
        self.image = ImageTk.PhotoImage(self.original)
        self.display = Canvas(self.frame1)
        self.slider = Scale(root, from_=0, to=len(os.listdir('app_images'))-1,orient=HORIZONTAL, command=self.setImg)
        self.display.pack(fill=BOTH, expand=1)
        self.slider.pack()
        self.startLabel = Label(root,text='start: ')
        self.endLabel = Label(root,text='end: ')
        self.button1 = Button(root, text ="Pick start", command = self.pickstart)
        self.button2 = Button(root, text ="Pick end", command = self.pickend)
        self.button3 = Button(root, text ="Done", command = self.done)
        self.startLabel.place(x=375,y=100)
        self.endLabel.place(x=375,y=120)
        self.button1.place(x=350,y=600)
        self.button2.place(x=350,y=650)
        self.button3.place(x=450,y=625)
        self.pack(fill=BOTH, expand=1)
        self.frame1.pack(fill=BOTH, expand=1)
        self.start=0
        self.end=0
    def setImg(self, *args):
        num = self.slider.get()
        img=Image.open('app_images/'+os.listdir('app_images')[num])
        self.image = ImageTk.PhotoImage(img)
        self.display.delete("IMG")
        self.display.create_image(self.display.winfo_width()/2, self.display.winfo_height()/2, anchor=CENTER, image=self.image, tags="IMG")
    def pickstart(self, *args):
        self.start=self.slider.get()
        self.startLabel.config(text='start: '+str(self.start))
    def pickend(self, *args):
        self.end=self.slider.get()
        self.endLabel.config(text='end: '+str(self.end))
    def done(self, *args):
        root.destroy()

root = Tk()
root.wm_title("Set timings")
w = 800
h = 700
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y-60))
app = TimeApp(root)
app.mainloop()
start=app.start
end=app.end
sec=(end-start)/3
if sec<=0: quit()

# fetch the frames to be used for the tab
video = pafy.new(url)
best = video.getbest(preftype="mp4")
cap = cv2.VideoCapture(best.url)
count = 0
if(skip>0): 
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(30*skip))
    count+=int(30*skip)
path = "images"
while cap.isOpened():
    ret, frame = cap.read()

    if ret:
        filename=url[url.index('watch?v=')+8:]
        name = path + "./"+ filename + "{:05d}".format(count) + ".jpg"
        cv2.imwrite(name, frame)
        count += int(30*sec) # 30 fps
        cap.set(cv2.CAP_PROP_POS_FRAMES, count)
    else:
        cap.release()
        break
print('All screenshots taken')

# crop the images to get only the tab part
class CropApp(Frame):
    def __init__(self,root):
        Frame.__init__(self, root)
        self.frame1 = Frame(self)
        img=Image.open('images/'+os.listdir('images')[0])
        w,h=img.size
        img=img.resize((700,int(700/w*h)))
        # print(int(700/w*h))
        self.im=img
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.display = Canvas(self.frame1,cursor="cross")
        self.x = self.y = self.curX = self.curY = 0
        self.display.bind("<ButtonPress-1>", self.on_button_press)
        self.display.bind("<B1-Motion>", self.on_move_press)
        self.display.bind("<ButtonRelease-1>", self.on_button_release)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.button = Button(root, text ="Done", command = self.done)
        self.button.place(x=400,y=450)
        self.display.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)
        self.frame1.pack(fill=BOTH, expand=1)
        self.display.create_image(400,250, anchor=CENTER, image=self.tk_im)

    def on_button_press(self,event):
        # save mouse drag start position
        self.start_x = self.display.canvasx(event.x)
        self.start_y = self.display.canvasy(event.y)
        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.display.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def on_move_press(self,event):
        self.curX = self.display.canvasx(event.x)
        self.curY = self.display.canvasy(event.y)
        self.display.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_button_release(self, event):
        return
    def done(self, *args):
        root.destroy()

root=Tk()
root.wm_title("Crop")
w = 800
h = 500
ws = root.winfo_screenwidth()
hs = root.winfo_screenheight()
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
root.geometry('%dx%d+%d+%d' % (w, h, x, y-60))
app = CropApp(root)
app.pack()
root.mainloop()
img=Image.open('images/'+os.listdir('images')[0])
w,h=img.size
resized_y=int(700/w*h)
x1=round((app.start_x-50)*(w/700))
x2=round((app.curX-app.start_x)*(w/700)+x1)
y1=round((app.start_y-250+int(resized_y/2))*(h/resized_y))
y2=round((app.curY-app.start_y)*(h/resized_y)+y1)
if x1 < 0: x1=0
if x1 > w: x1=w
if x2 < 0: x2=0
if x2 > w: x2=w
if y1 < 0: y1=0
if y1 > h: y1=h
if y2 < 0: y2=0
if y2 > h: y2=h
print('Crop coordinates: '+str((x1,y1,x2,y2)))

# crop and merge all the images into a tab
output=Image.new('RGB',((x2-x1),(y2-y1)*len(os.listdir('images'))))
y_offset=0
for file in os.listdir('images'):
    img=Image.open('images/'+file)
    img = img.crop((x1, y1, x2, y2))
    output.paste(img,(0,y_offset))
    y_offset += y2-y1
output.save('output.jpg')
output.show('output.jpg')