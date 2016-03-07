from time import sleep, strftime, localtime
from Tkinter import *
#import MySQLdb
import mysql.connector
import urllib
import csv
import string


class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        self.mysqlinfo_label = Label(frame, text='MySQL fields:')
        self.mysqlinfo_label.grid(row=0)

        self.label_host = Label(frame, text='Host:')
        self.label_host.grid(row=1)

        host_text = StringVar()
        host_text.set("127.0.0.1")

        self.entry_host = Entry(frame, textvariable=host_text)
        self.entry_host.grid(row=1, column=1)

        self.label_user = Label(frame, text='User:')
        self.label_user.grid(row=2)

        user_text = StringVar()
        user_text.set("root")

        self.entry_user = Entry(frame, textvariable=user_text)
        self.entry_user.grid(row=2, column=1)

        self.label_password = Label(frame, text='Password:')
        self.label_password.grid(row=3)

        self.entry_password = Entry(frame, show="*")
        self.entry_password.grid(row=3, column=1)

        self.label_database = Label(frame, text='Database:')
        self.label_database.grid(row=4)

        database_text = StringVar()
        database_text.set("stocks")

        self.entry_database = Entry(frame, textvariable=database_text)
        self.entry_database.grid(row=4, column=1)

        self.label_empty = Label(frame, text='')
        self.label_empty.grid(row=5)

        self.label_twscontractinfo = Label(frame, text='Yahoo info:')
        self.label_twscontractinfo.grid(row=9)

        self.label_symbol = Label(frame, text='Symbol:')
        self.label_symbol.grid(row=10)

        self.entry_symbol = Entry(frame)
        self.entry_symbol.grid(row=10, column=1)

        self.label_startmonth = Label(frame, text='Start Month:')
        self.label_startmonth.grid(row=11)

        self.entry_startmonth = Entry(frame)
        self.entry_startmonth.grid(row=11, column=1)

        self.label_startday = Label(frame, text='Start Day')
        self.label_startday.grid(row=12)

        self.entry_startday = Entry(frame)
        self.entry_startday.grid(row=12, column=1)

        self.label_startyear = Label(frame, text='Start Year:')
        self.label_startyear.grid(row=13)

        self.entry_startyear = Entry(frame)
        self.entry_startyear.grid(row=13, column=1)

        self.label_empty = Label(frame, text='')
        self.label_empty.grid(row=14)

        self.button_download = Button(frame, text="Download", command=self.tws_connect)
        self.button_download.grid(row=15, column=1)

        self.button_import = Button(frame, text="Import", command=self.mysql_connect)
        self.button_import.grid(row=16, column=1)

        self.label_empty = Label(frame, text='')
        self.label_empty.grid(row=17)


    def tws_connect(self):
        print "downloading csv file from yahoo..."

        #split symbol string

        #raw_symbol_input = "%s" % (str(self.entry_symbol.get()))
        new_symbolinput = string.split(self.entry_symbol.get(), ',')

        #print raw_symbol_input
        print new_symbolinput

        for i in new_symbolinput:
            print i

        for i in new_symbolinput:
            print "downloading..." + i
            webFile = urllib.urlopen("http://ichart.finance.yahoo.com/table.csv?s=" + i + "&a=" + self.entry_startmonth.get() + '&b=' + self.entry_startday.get() + "&c=" + self.entry_startyear.get())
            fileName = i + ".csv"
            localFile = open(fileName.split('/')[-1], 'w')
            localFile.write(webFile.read())
            webFile.close()
            localFile.close()

            fieldnames = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
            fileName2 = "csv/" + i + "2.csv"
            with open(fileName, 'rb') as csvinput:
                with open(fileName2, 'wb') as csvoutput:
                    csvwriter = csv.DictWriter(csvoutput, fieldnames, delimiter=',')
                    csvwriter.writeheader()
                    for row in csv.DictReader(csvinput):
                        row['Symbol'] = i
                        csvwriter.writerow(row)


    def mysql_connect(self):
        print "connecting to mysql..."

        print "MySQL host: " + self.entry_host.get()
        print "MySQL user: " + self.entry_user.get()
        print "MySQL database: " + self.entry_database.get()

        db = mysql.connector.connect(host=self.entry_host.get(), user=self.entry_user.get(),passwd=self.entry_password.get(), db=self.entry_database.get())
        cur = db.cursor()

        #split symbol string

        #raw_symbol_input = "%s" % (str(self.entry_symbol.get()))
        new_symbolinput2 = string.split(self.entry_symbol.get(), ',')

        for i in new_symbolinput2:

            cur.execute("load data local infile 'C://Users//ryan//Desktop//market//yahoo_import_v0.1 - Copy//csv//" + i + "2.csv' into table `stocks`.`stocks_yahoo_prev` fields terminated by ',' lines terminated by '\n' ignore 1 lines (`symbol`,`date`,`open`,`high`,`low`,`close`,`volume`,`adj_close`);")
            db.commit()

            print "contract info..."
            print "Symbol: " + i

root = Tk()
root.title('Historical Data: Download and Import')
app = App(root)

root.mainloop()