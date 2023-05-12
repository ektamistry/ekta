import random
from tkinter import *
import copy
import time
from threading import Thread
import sqlite3

margin = 20
side = 50
width = 490
height = 490

class SudokuSolver:
    def __init__(self, b):
        self.newgrid = copy.deepcopy(b)
        self.sudoku(self.newgrid, 0, 0)

    def init(self):
        return self.newgrid

    @staticmethod
    def check(newgrid, row, col, num):
        for i in range(9):
            if newgrid[i][col] == num or newgrid[row][i] == num:
                return False

        for i in range(3):
            for j in range(3):
                if newgrid[i + (row - row % 3)][j + (col - col % 3)] == num:
                    return False
        return True

    def sudoku(self, newgrid, row, col):
        if row == 8 and col == 9:
            return True

        if col == 9:
            row = row + 1
            col = 0

        if newgrid[row][col] > 0:
            return self.sudoku(newgrid, row, col + 1)

        for i in range(1, 10):
            if self.check(newgrid, row, col, i):
                newgrid[row][col] = i
                if self.sudoku(newgrid, row, col + 1):
                    return True
            newgrid[row][col] = 0


class GUI(Frame):
    def __init__(self, parent, b):
        global stop
        self.board = b
        Frame.__init__(self, parent)
        self.parent = parent
        self.canvas = Canvas(parent, width=width, height=height)
        self.canvas.pack(side=TOP)
        self.canvas.place(y=50)
        self.deleteBtn = Button(parent, text="Delete", command=self.delNum, width=9)
        self.deleteBtn.config(font=("Helvetica", 20))
        self.deleteBtn.place(y=525)
        self.checkBtn = Button(parent, text="Check", command=self.checkVictory, width=9)
        self.checkBtn.config(font=("Helvetica", 20))
        self.checkBtn.place(x=350, y=525)
        self.showBtn = Button(parent, text="Show Answer", command=self.displayAnswer, width=12)
        self.showBtn.config(font=("Helvetica", 20))
        self.showBtn.place(x=155, y=525)
        t = StringVar()
        t.set("00:00:00")
        lb = Label(parent, textvariable=t, font="Times 40 bold")
        lb.place(x=160, y=0)
        self.row, self.col = -1, -1
        self.draw_grid()
        obj = SudokuSolver(b)
        self.solved = obj.init()
        self.canvas.bind("<Button-1>", self.cellClicked)
        self.canvas.bind("<Key>", self.keyPressed)
        thread = Thread(target=lambda: stopwatch(t))
        thread.setDaemon(True)
        try:
            thread.start()
        except RuntimeError:
            stop = False
            thread.join()

    def draw_grid(self):
        for i in range(10):
            color = "#0000ff" if i % 3 == 0 else "#808080"
            x0 = margin + i * side
            y0 = margin
            x1 = margin + i * side
            y1 = height - margin
            self.canvas.create_line(x0, y0, x1, y1, fill=color)
            x0 = margin
            y0 = margin + i * side
            x1 = width - margin
            y1 = margin + i * side
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

        for i in range(9):
            for j in range(9):
                num = self.board[i][j]
                if num != 0:
                    x = margin + j * side + side / 2
                    y = margin + i * side + side / 2
                    self.canvas.create_text(x, y, text=num, tags="solid")

    def cellClicked(self, event):
        x, y = event.x, event.y
        if margin < x < width - margin and margin < y < height - margin:
            self.canvas.focus_set()
            row, col = (y - margin) // side, (x - margin) // side
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.board[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = margin + self.col * side + 1
            y0 = margin + self.row * side + 1
            x1 = margin + (self.col + 1) * side - 1
            y1 = margin + (self.row + 1) * side - 1
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tags="cursor")

    def updateBoard(self, row, col, num, flag):
        if row >= 0 and col >= 0:
            if flag:
                x = margin + self.col * side + side / 2
                y = margin + self.row * side + side / 2
                self.canvas.create_text(x, y, text=num, fill="green", tags="solid")
                self.board[self.row][self.col] = num
            else:
                x = margin + self.col * side + side / 2
                y = margin + self.row * side + side / 2
                self.canvas.create_text(x, y, text=num, fill="red", tags="wrong")
                self.board[self.row][self.col] = num

    def delNum(self):
        self.canvas.delete("wrong")
        if self.row >= 0 and self.col >= 0:
            self.board[self.row][self.col] = 0

    def displayAnswer(self):
        self.canvas.delete("wrong")
        self.canvas.delete("solid")
        for i in range(9):
            for j in range(9):
                x = margin + j * side + side / 2
                y = margin + i * side + side / 2
                num = self.solved[i][j]
                self.canvas.create_text(x, y, text=num, fill="green", tags="solved")
        self.board = self.solved

    def checkVictory(self):
        if self.solved == self.board:
            global total_time, stop
            stop = False
            x1 = width // 2 - 150
            x2 = width // 2 + 150
            y1 = height // 2 - 150
            y2 = height // 2 + 150
            self.canvas.create_oval(x1, y1, x2, y2, fill="dark orange")
            x = y = width // 2
            text = "Victory!! You Win!!\nSolved in: " + total_time
            self.canvas.create_text(x, y, text=text, fill="white", font=("Arial", 16))
        else:
            x1 = width // 2 - 150
            x2 = width // 2 + 150
            y1 = height // 2 - 150
            y2 = height // 2 + 150
            self.canvas.create_oval(x1, y1, x2, y2, fill="red", tags="wrong")
            x = y = width // 2
            self.canvas.create_text(x, y, text="Try Again!!\nPress Delete", fill="white", font=("Arial", 16), tags="wrong")

    def keyPressed(self, event):
        num = int(event.char)
        if event.char in "123456789":
            if self.solved[self.row][self.col] == num:
                self.updateBoard(self.row, self.col, num, True)
            else:
                self.updateBoard(self.row, self.col, num, False)

def stopwatch(t):
    global total_time, stop
    while stop:
        d = str(t.get())
        h, m, s = map(int, d.split(":"))
        h = int(h)
        m = int(m)
        s = int(s)
        if s < 59:
            s += 1
        elif s == 59:
            s = 0
            if m < 59:
                m += 1
            elif m == 59:
                m = 0
                h += 1
        if h < 10:
            h = str(0) + str(h)
        else:
            h = str(h)
        if m < 10:
            m = str(0) + str(m)
        else:
            m = str(m)
        if s < 10:
            s = str(0) + str(s)
        else:
            s = str(s)
        d = h + ":" + m + ":" + s
        t.set(d)
        time.sleep(1)
        total_time = d
    t.set("")

if __name__ == "__main__":
    global total_time, stop
    stop = True
    r = random.randint(1, 100000)
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM users where id = ?''', (r,))
    puzzle = c.fetchall()
    m = puzzle[0][1]
    g = []
    for j in range(9):
        row = []
        for i in range(9):
            if m[j*9 + i] == ".":
                row.append(0)
            else:
                row.append(int(m[j * 9 + i]))
        g.append(row)
    window = Tk()
    GUI(window, g)
    window.geometry("%dx%d" % (width, height + 90))
    window.resizable(False, False)
    window.mainloop()
