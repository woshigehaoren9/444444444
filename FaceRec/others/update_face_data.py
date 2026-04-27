from model.connectsqlite import ConnectSqlite

con = ConnectSqlite('./database/database.db')
con.update_face_table(["Alex","82006919",26])