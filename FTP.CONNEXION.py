# source = "montest.py"
# source_file = open(source, 'rb')
# ftp.storbinary('STOR'+source, source_file)
# ftp.retrbinary('RETR'+destination, dest_file.write, 1024)

# mdp = python123
import ftplib


host = "127.0.0.1"
user = "AdminAS"  #  login()  ?
password = "python123"
ftp = ftplib.FTP(host, user, password)


# ftp.mkd("test1")
print(ftp.getwelcome())


source = "Mytest.txt" # pour transmettre un fichier en read binary
source_file = open(source, 'rb') # read binary
ftp.storbinary('STOR '+source, source_file)
source_file.close()
ftp.rename(source,"Version2.txt")

# retelecahrger le fichier, en write binary
destination = "Version2.txt"
dest_file = open(destination, "wb")
ftp.retrbinary("RETR " + destination, dest_file.write, 1024)
## ftp.delete("Version2.py")
dest_file.close()




print(ftp.dir())


ftp.quit()
ftp.close()