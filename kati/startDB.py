import setupDB

DB = setupDB.DB_connect("downloadedVideos")

# DB.setupDB()

# values = ["Custom Block Loader | Tkinter Loading Animation",
#          "https://www.youtube.com/watch?v=nl0mePCxoGU",
#          "7.67 MB",
#          "720p",
#          "Pythonista Empire",
#          12174
#          ]
#
# DB.insert_data(values=values)
data = DB.get_data()

for row in data:
    print(row)

DB.close_conn()
