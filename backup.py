#Importing required modules
from flask import Flask, request, render_template
from turtle import Turtle, Screen
import tkinter as tk
import threading
import math
import time
import matplotlib.pyplot as plt
import pandas as pd
final=[] # final list of all processes for SJF simulator
#Creating a flask app
app = Flask(__name__)

#Routing for home page 
@app.route("/", methods=['GET','POST'])
def home():
    if request.method == "POST" : #handling post request
        return render_template("index.html")
    #Return render_template will give the html page as output that is mentioned in it
    return render_template("index.html")

@app.route('/sjf', methods =["GET", "POST"])#Routing
def sjf():
    if request.method == "POST":#Handling post requests
        if request.form.get("b1") == "v1" :
            a=[] #creating list for individual process
            at= request.form.get("at") #getting arrival time
            bt= request.form.get("bt") #getting burst time
            pid= request.form.get("PID") #getting PID
            #appending values in list 'a'
            a.append(int(at)) 
            a.append(int(bt))
            a.append(int(pid))
            final.append(a) #appending 'a' list in 'final' list
            a=[]
            gc=[]
            return render_template("sjf.html",test= len(gc)) #sending length of gc to html file
        elif request.form.get("b2") == "v2" :
            #declaring constants
            tim = 0
            test = 0
            count = 1
            ct = []
            wt = []
            bt = []
            gc = []
            tat = []
            final.sort() #sorting the final list
            cop = final.copy() #creating a shallow copy
            gc.append(final[0][2])
            # when arrival time of first process is > 0 
            if final[0][0] !=0 :
                tim+=final[0][0]
                tim+=final[0][1]
            else :
                tim+=final[0][1]
            ct.append(tim) #appending time in completion time list
            while count <=len(cop)-1 : #condition for checking which processes have arrived in memory
                for i in final[1:]: #final[1:] indicates slicing of list 
                    if i[0]<= tim:
                        bt.append(i[1]) #appending burst time
                ind = bt.index(min(bt))
                tim+=final[ind+1][1]
                gc.append(final[ind+1][2])
                final.remove(final[ind+1]) #removing the executed process
                ct.append(tim)
                bt=[]
                count+=1 
            # creating turn around time list
            for i in gc :
                for j in range(0,len(cop)) : 
                    if cop[j][2] == i :
                        tat.append(ct[test]-cop[j][0])
                        test+=1
            test = 0
            # creating waiting time list 
            for i in gc :
                for j in range(0,len(cop)) :
                    if cop[j][2] == i :
                        wt.append(tat[test]-cop[j][1])
                        test+=1
            avg_wt = sum(wt)/len(wt) #finding average waiting time
            avg_tt = sum(tat)/len(tat) #finding average turnaround time
            #creating dataframe from user input values
            df = pd.DataFrame({ 
            'Process': gc,
            'Start': [0] + ct[:-1],
            'Duration': [ct[0]] + [ct[i+1]-ct[i] for i in range(len(ct)-1)]
            })

            # Creating figure and axis object
            fig, ax = plt.subplots(figsize=(10, 5))

            # Setting the y-axis label to 'Process'
            ax.set_ylabel('Process')
            ax.set_xlabel('Completion time')

            # Setting the x-axis limit to the maximum completion time
            ax.set_xlim([0, max(ct)])

            # Plotting the Gantt chart
            ax.barh(df['Process'], df['Duration'], left=df['Start'], height=0.5)

            # Showing the Gantt chart
            plt.show()
            #returning necessary values to html file 
            return render_template("sjf.html",test = len(gc),gc = gc,test1 = len(ct),ct = ct,test2 = len(wt),wt =wt,avg_wt = avg_wt,avg_tt = avg_tt,test3 = len(tat),tat=tat)
    else :
        gc=[]
        return render_template("sjf.html",test = len(gc))

#Routing for dining philosophers problem
@app.route("/dining", methods=['GET', 'POST'])
def dining():
    if request.method == "POST": #Declaring post method
        NUM_PHILOSOPHERS = 5 
        FORKS = [threading.Lock() for i in range(NUM_PHILOSOPHERS)]#Implementation of Threads 

        class Philosopher(threading.Thread):
            def __init__(self, num, canvas):

                threading.Thread.__init__(self)
                self.num = num 
                self.canvas = canvas

            def run(self):#Function for executing program
                for i in range(5):
                    self.think()
                    self.eat()

            def think(self):#Thinking function of philosophers
                self.canvas.itemconfig(
                    self.text_id, text=f"Philosopher {self.num} is thinking.")
                time.sleep(1)

            def eat(self):#Eating function of philosophers
                left_fork = self.num
                FORKS[left_fork].acquire()#Acquiring left chopstick

                right_fork = (self.num + 1) % NUM_PHILOSOPHERS
                FORKS[right_fork].acquire()#Acquiring left chopstick

                self.canvas.itemconfig(
                    self.text_id, text=f"Philosopher {self.num} is eating.")
                time.sleep(1)

                FORKS[left_fork].release()#Releasing left chopstick
                FORKS[right_fork].release()#Releasing right chopstick
                self.canvas.itemconfig(
                    self.text_id, text=f"Philosopher {self.num} finished eating.")

        class App:#Main Function
            def __init__(self, master):
                self.canvas = tk.Canvas(master, width=600, height=600)#Creating canvas for tkinter
                self.canvas.pack()
                self.philosophers = []
                for i in range(NUM_PHILOSOPHERS):
                    x = 300 + 200 * \
                        math.cos(2 * math.pi * i / NUM_PHILOSOPHERS)
                    y = 300 + 200 * \
                        math.sin(2 * math.pi * i / NUM_PHILOSOPHERS)
                    text_id = self.canvas.create_text(
                        x, y, text=f"Philosopher {i}")
                    self.philosophers.append(Philosopher(i, self.canvas))
                    self.philosophers[i].text_id = text_id
                self.start_button = tk.Button(
                    master, text="Start", command=self.start)
                self.start_button.pack()

            def start(self):#Starting function
                self.start_button.config(state=tk.DISABLED)
                for philosopher in self.philosophers:
                    philosopher.start()

        root = tk.Tk()
        app = App(root)
        root.mainloop()#Exiting the loop
        return render_template("dp.html")
    else:
        return render_template("dp.html")

@app.route("/look-clook", methods=['GET'])#Routing to look-clook.html
def lookclook():
    return render_template("look-clook.html")

@app.route("/look", methods=["GET", "POST"])#Submitting data from look.html
def look():
    if request.method == "POST":
        pointer = request.form['pointer'] #getting value of current pointer from user
        values = request.form['values'] #getting frame values from user
        queue = values.split(" ") #splitting the string entered by user in list
        print(queue)
        current_pointer = int(pointer) #converting current pointer to int from str
        print(type(current_pointer))
        queue.sort()#sort functions sorts the queue in ascending order
        forward = [int(num) for num in queue if int(num) > current_pointer] #list comprehension
        forward.sort()
        backward = [int(num) for num in queue if int(num) < current_pointer]
        new_backward = [num for num in backward[::-1]]#[::-1] used to reverse the elements of list
        movement_list = forward+new_backward #creating final movement list
        total_movements = (forward[-1]-current_pointer)+(forward[-1]-new_backward[-1]) #calculating total head movements
        print(movement_list)
        print(total_movements)
        count = 0
        test = Turtle()#Creating a Turtle object
        screen = Screen()#Creating a Screen object
        screen.colormode(255)
        color_choice = ["black", "red"]#Color choices for simulator
        screen.screensize(500, 500)#Setting a screen size
        test.speed(1)#Setting animation speed
        test.pensize(5)#Setting pen size
        test.color("blue")#Color of pen till reaching starting counter
        test.write("0")#Write function is used to add text to the screen of turtle
        test.goto(current_pointer, 0)
        test.penup()#Disables the Turtle's functionality to draw on the screen
        test.goto(current_pointer, 15)#Used to send the turtle to specific coordinates
        test.write(str(current_pointer))
        test.goto(current_pointer, 0)
        test.pendown()#Enables the Turtle's functionality to draw on the screen
        
        #Function for choosing pen color
        def pen_color_choice(count):
            if count <= len(forward):
                y = 0
                up = 15
                down = -15
            else:
                y = -50
                up = -30
                down = -70
            if count % 2 == 0:
                test.penup()
                test.goto(num, up)
                test.write(str(num), align="left")
                test.goto(num, y)
                test.pendown()
            else:
                test.penup()
                test.goto(num, down)
                test.write(str(num), align="left")
                test.goto(num, y)
                test.pendown()
        #Moving forward
        for num in forward:
            color_line = color_choice[count % 2]
            test.color(color_line)
            test.goto(num, 0)
            count += 1
            pen_color_choice(count)
        test.right(150)
        #Moving Backward
        for num in backward:
            color_line = color_choice[count % 2]
            test.color(color_line)
            test.goto(num, -50)
            count += 1
            pen_color_choice(count)
        test.penup()
        test.hideturtle()
        test.speed(0)
        test.goto(0, 230)
        #Adding the start pointer and total movements
        test.write(f"Start Pointer : {current_pointer}\nTotal head movements : {total_movements}", align="center", font=(
            "courier", 15, "bold"))
        screen.exitonclick()
        return render_template("look.html")
    else:
        return render_template("look.html")
    
#This is the code for clook the comments can be interpreted same as the above
@app.route("/clook", methods=["GET", "POST"])
def clook():
    if request.method == "POST":
        pointer = request.form['pointer']
        values = request.form['values']
        queue = values.split(" ")
        new_queue = [int(num) for num in queue]
        new_queue.sort()
        current_pointer = int(pointer)
        forward = [num for num in new_queue if num > current_pointer]
        backward = [num for num in new_queue if num < current_pointer]
        movement_list = forward+backward
        total_movements = (forward[-1]-current_pointer)+(forward[-1]-backward[0])+(backward[-1]-backward[0])
        print(movement_list)
        print(total_movements)
        count = 0
        test = Turtle()
        test._RUNNING=True
        screen = Screen()
        screen.colormode(255)
        color_choice = ["black", "red"]
        screen.screensize(500, 500)
        test.speed(1)
        test.pensize(5)
        test.color("blue")
        test.write("0")
        test.goto(current_pointer, 0)
        test.penup()
        test.goto(current_pointer, 15)
        test.write(str(current_pointer))
        test.goto(current_pointer, 0)
        test.pendown()

        def pen_color_choice(count):
            if count <= len(forward):
                y = 0
                up = 15
                down = -15
            else:
                y = -50
                up = -30
                down = -70
            if count % 2 == 0:
                test.penup()
                test.goto(num, up)
                test.write(str(num), align="left")
                test.goto(num, y)
                test.pendown()
            else:
                test.penup()
                test.goto(num, down)
                test.write(str(num), align="left")
                test.goto(num, y)
                test.pendown()
        for num in forward:
            color_line = color_choice[count % 2]
            test.color(color_line)
            test.goto(num, 0)
            count += 1
            pen_color_choice(count)
        test.right(150)
        for num in backward:
            color_line = color_choice[count % 2]
            test.color(color_line)
            test.goto(num, -50)
            count += 1
            pen_color_choice(count)
        test.penup()
        test.hideturtle()
        test.speed(0)
        test.goto(0, 230)
        test.write(f"Start Pointer : {current_pointer}\nTotal head movements : {total_movements}", align="center", font=(
            "courier", 15, "bold"))
        screen.exitonclick()
        return render_template("clook.html")
    else:
        return render_template("clook.html")
    
#Routing for fifo page replacement algorithm
@app.route("/fifo",methods = ["GET","POST"])
def fifo() :
    if request.method == "POST":
        frames = int(request.form.get("frames"))#Getting data of number of frames from html form
        ref = request.form.get("references").split(",")#Getting reference string from html form 
        #spliting the string from " " so we can get all numbers in the form of a list
        new_ref = [int(num) for num in ref]#converts the elements of ref in integer
        final_list = []#List which will contain information of all list at every step 
        list = [] #stores the current status of code
        status = []#stores wheather the data was a page fault or a hit
        hit=0
        miss=0
        count=0
        for ele in new_ref :
            if ele not in list :
                if len(list) <= frames-1 :#Makes sure number of elements in the list are not more than frames
                    miss+=1#Incremeant the miss counter
                    list.append(ele)#Adding the element in the list
                    a = list.copy()#Making a shallow copy of list
                    status.append("Miss")#Since element not in list so Miss is appended in status list
                    final_list.append(a)#Appending list in final_list 
                    print(list)
                #Procedure if element is not in list and the list is full i.e len(list)==Frames
                else :
                    list.remove(list[count%frames])
                    #Removing the first element that came to make space for the new element
                    list.insert(count%frames, ele)
                    #Inserting the element at the index of removed element
                    count+=1
                    miss+=1
                    b = list.copy()
                    final_list.append(b)
                    status.append("Miss")
                    print(list)
            else :
                c = list.copy()
                final_list.append(c)
                status.append("Hit")#Since element is in the list so Hit is appended
                print(list)
                hit+=1
        hit_ratio = '%.2f'  %((hit/len(ref))*100)#Makes the ratio to 2 decimal places
        miss_ratio = '%.2f' %((miss/len(ref))*100)#Makes the ratio to 2 decimal places
        print(final_list)
        print(f"Total hits : {hit}")
        print(f"Total miss : {miss}")
        print(f"hit ratio : {hit_ratio}")
        print(f"miss ratio : {miss_ratio}")

        #The data you want to send back to the html file is entered after the html file 
        #you want to render is specified in this case final_list,hit etc. 
        return render_template("fifo.html", final_list=final_list, hit=hit, miss=miss, hit_ratio=hit_ratio, miss_ratio=miss_ratio,status=status,len=len)
    else:
        return render_template("fifo.html",len=len)

#Running the app
if __name__ == "__main__":
    app.run(debug=True)
