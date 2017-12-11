def sedvalue(str_src, str_dest, conf_file):
    try:
        run('sed -i "s/{src_string}/{dest_string}/g" {filedir}'
            .format(src_string=str_src, dest_string=str_dest, filedir=conf_file)
        )
        Logger.writelog("[OK] Sed {src_string}, to {dest_string}, in {filedir}"
            .format(src_string=str_src, dest_string=str_dest, filedir=conf_file)
        )
    except BaseException as e:
        Logger.writelog("[ERROR] Sed {src_string}, to {dest_string}, in {filedir} ({error})"
                        .format(src_string=str_src, dest_string=str_dest, filedir=conf_file, error=e)
        )
        if EXITONERROR:
            print("Error found: {error}".format(error=e))
            exit(1)


def copyfiles(conf_root, files_list):
    for file in files_list:
        try:
            put(conf_root+file[0], file[1], mode=file[2])
            Logger.writelog("[OK] Copy {srcfile}, to {destfile}, with chmod {chmod}".format(
                srcfile=conf_root+file[0], destfile=file[1], chmod=file[2]
                )
            )
        except BaseException as e:
            Logger.writelog("[ERROR] Copy {srcfile}, to {destfile}, with chmod {chmod} ({error})".format(
                srcfile=conf_root+file[0], destfile=file[1], chmod=file[2], error=e
                )
            )
            if EXITONERROR:
                print("Error found: {error}".format(error=e))
                exit(1)

class Logs:
    def __init__(self, logfiledir):
        self.logfiles = logfiledir
        self.file = open(self.logfiles, "w")

    def writelog(self, text):
        self.file.write(text+"\n")

    def closefile(self):
        self.file.close()

