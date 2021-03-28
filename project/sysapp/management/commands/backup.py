from django.core.management.base import BaseCommand
from fabric.api import env

env.host_string = 'eden.webfactional.com'
env.user = 'lobofarm'
env.password = 'lobofarm.000'

OutPath = "/tmp/"
SQLDumpFName = "diocles_dbdump.sql"
SQLDumpGZFName = SQLDumpFName + ".gz"
BackupFPath = OutPath + SQLDumpGZFName
RemotePath = "/home/lobofarm/bup"


#**************************************************************************************************


class Command(BaseCommand):
    args = '<backup ...>'
    help = 'Dump database and copy to remote server'

    #----------------------------------------------------------------------------------------------

    def dump_database(self):
        from subprocess import call
        import project.settings

        out_dump_fname = OutPath + SQLDumpFName

        dump_cmd = "mysqldump -u %(user)s -p%(pass)s %(dbname)s > %(out_fpath)s" % (
            {
                "user": project.settings.local.DATABASES["default"]["USER"],
                "pass": project.settings.local.DATABASES["default"]["PASSWORD"],
                "dbname": project.settings.local.DATABASES["default"]["NAME"],
                "out_fpath": out_dump_fname,
            }
        )

        gzip_cmd = "gzip %(fname)s" % (
            {
                "fname": out_dump_fname,
            }
        )

        call(dump_cmd, shell=True)
        call(gzip_cmd, shell=True)

    #----------------------------------------------------------------------------------------------

    def rotate_old_backups(self):
        from fabric.operations import run
        try:
            run("mv %(path)s/%(fname)s.4 %(path)s/%(fname)s.5" % ({"path": RemotePath, "fname": SQLDumpGZFName}))
        except:
            pass
        try:
            run("mv %(path)s/%(fname)s.3 %(path)s/%(fname)s.4" % ({"path": RemotePath, "fname": SQLDumpGZFName}))
        except:
            pass
        try:
            run("mv %(path)s/%(fname)s.2 %(path)s/%(fname)s.3" % ({"path": RemotePath, "fname": SQLDumpGZFName}))
        except:
            pass
        try:
            run("mv %(path)s/%(fname)s.1 %(path)s/%(fname)s.2" % ({"path": RemotePath, "fname": SQLDumpGZFName}))
        except:
            pass
        try:
            run("mv %(path)s/%(fname)s %(path)s/%(fname)s.1" % ({"path": RemotePath, "fname": SQLDumpGZFName}))
        except:
            pass


    #----------------------------------------------------------------------------------------------

    def upload_backup(self):
        from fabric.operations import put
        put("/tmp/" + SQLDumpGZFName, RemotePath)

    #----------------------------------------------------------------------------------------------

    def remove_local_files(self):
        from subprocess import call
        call("rm %s%s" % (OutPath, SQLDumpFName), shell=True)
        call("rm %s%s" % (OutPath, SQLDumpGZFName), shell=True)

    #----------------------------------------------------------------------------------------------

    def handle(self, *args, **options):
        self.remove_local_files()
        self.dump_database()
        self.rotate_old_backups()
        self.upload_backup()
        self.remove_local_files()

    #----------------------------------------------------------------------------------------------


#**************************************************************************************************
