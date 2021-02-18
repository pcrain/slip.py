#!/usr/bin/python
import sys, os, sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))

class Migrator(object):
    def __init__(self,config):
        self.new_version = config.SITE_VERSION
        self.old_version = None
        self.db_location = config.SQLALCHEMY_DATABASE_URI.replace("sqlite:///","")

    def run(self):
        conn = sqlite3.connect(self.db_location)
        c    = conn.cursor()

        #Get the app version currently associated with the database
        c.execute("SELECT * FROM settings WHERE name == 'appversion'")
        f = { d[0] : i for i,d in enumerate(c.description) } #Map of field names to numbers
        for m in c.fetchall():            #Working with results of SELECT
          self.old_version = m[f["name"]]
          break
        if self.old_version is None:
          self.old_version = "0.6.5"

        #Run appropriate migrations
        print(f"Upgrading {self.db_location} from {self.old_version} to {self.new_version}")

        #TODO:
          # Put migrations in a list with associated versions
          # if the old_version < cur_Version, back up database
          # while old_version < migration:
          #   perform_migration
          #   update_version

        #Commite changes and close
        # conn.commit()
        conn.close()
