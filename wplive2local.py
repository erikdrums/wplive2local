#!/usr/bin/python

#http://spin.atomicobject.com/2011/08/08/remote-mysqldump-with-no-temp-files/

import sys
import string
import shutil
import getopt
import os
import os.path
import syslog
import errno
import logging
import tempfile
import datetime
import subprocess


def main(argv):

    print "Begin Migration"
    initial = False

    production_ssh_user = ''
    production_ssh_address = ''
    production_db_user = ''
    production_db_password = ''
    production_host = ''
    production_url = ''
    production_db = ''
    dbbackup_path = ''

    local_mysql = ''
    local_mysqldump = ''
    local_db_user = ''
    local_db_password = ''
    local_db = ''
    local_site_password = ''
    local_url = ''

    def build_query(user, password, runtype='mysql', host='localhost', database=None):
        if database is None:
            database = ''
        return "{} -u{} -p{} {} -h{}".format(runtype, user, password, database, host)

    def build_query_command(user, password, query_command, runtype='mysql', host='localhost', database=None):
        query = build_query(user, password, runtype, host, database)
        return "{} -e '{}'".format(query, query_command)


    def run_query(user, password, query, runtype='mysql', host='localhost', database=None):
        #logging.info("Dump db, %s to %s." % (production_db, dbbackup_path))
        print build_query_command(user, password, query, runtype, host, database)
        os.popen(build_query_command(user, password, query, runtype, host, database))

    def local_db_dump():
        #dump_cmd += " -e --opt -c " + production_db + " > " + dbbackup_path + ".sql"
        dump_query = " --opt -c " + local_db + " > " + dbbackup_path + ".sql"

        
        query_command = "{} -e --opt -c {} > {}.sql".format(build_query(local_db_user, local_db_password, local_mysqldump), 
                                                                        local_db, dbbackup_path)
        os.popen(query_command)
    
    def local_db_drop():
        #dump_cmd = "{} -u{} -p{} -h{} -e 'drop database {}'".format(local_mysql, production_ssh_user, 
        #                                                    production_mysql_password, production_host, local_db)
        dump_query = "drop database {}".format(local_db)
        run_query(local_db_user, local_db_password, dump_query, local_mysql)    

    def local_db_create():
        #dump_cmd = "{} -u{} -p{} -h{} -e 'create database {}'".format(local_mysql, production_ssh_user, 
        #                                                    production_mysql_password, production_host, local_db)
        dump_query = "create database {}".format(local_db)
        run_query(local_db_user, local_db_password, dump_query, local_mysql)    

    
    def production_dump_to_local():
        #dump_cmd = "ssh root@188.226.130.116 'mysqldump -uroot -pGV5AEoUEmd -hlocalhost jylland | \
        #gzip -9' | gzip -d | /Applications/MAMP/Library/bin/mysql -uroot -proot jyllandsakvariet"
        production_query = build_query(production_db_user, production_db_password, 'mysqldump', database=production_db)
        local_query = build_query(local_db_user, local_db_password, local_mysql, database=local_db)
        command = "ssh {}@{} '{} | gzip -9' | gzip -d | {}".format(
            production_ssh_user, production_ssh_address, production_query, local_query)
        #print command
        os.popen(command)


    def local_update_urls():
        """
        /Applications/MAMP/Library/bin/mysql -uroot -proot jyllandsakvariet -Bse \
        "UPDATE wp_options SET option_value = replace(option_value, 'http://jyllandsakvariet.dk', 'http://localhost:8888/jyllandsakvariet/wordpress') \
        WHERE option_name = 'home' OR option_name = 'siteurl';\
        UPDATE wp_posts SET guid = replace(guid, 'http://jyllandsakvariet.dk','http://localhost:8888/jyllandsakvariet/wordpress');\
        UPDATE wp_posts SET post_content = replace(post_content, 'http://jyllandsakvariet.dk', 'http://localhost:8888/jyllandsakvariet/wordpress');\
        UPDATE wp_postmeta SET meta_value = replace(meta_value,'http://jyllandsakvariet.dk','http://localhost:8888/jyllandsakvariet/wordpress');";



            "UPDATE wp_options SET option_value = replace(option_value, '{0}', '{1}')\
            WHERE option_name = 'home' OR option_name = 'siteurl';\
            UPDATE wp_posts SET guid = replace(guid, '{0}', '{1}');\
            UPDATE wp_posts SET post_content = replace(post_content, '{0}', '{1}');\
            UPDATE wp_postmeta SET meta_value = replace(meta_value, '{0}', '{1}');";\


        """
        query = build_query(local_db_user, local_db_password, local_mysql, database=local_db)
        query_command = """ "UPDATE wp_options SET option_value = replace(option_value, '{0}', '{1}')\
            WHERE option_name = 'home' OR option_name = 'siteurl';\
            UPDATE wp_posts SET guid = replace(guid, '{0}', '{1}');\
            UPDATE wp_posts SET post_content = replace(post_content, '{0}', '{1}');\
            UPDATE wp_postmeta SET meta_value = replace(meta_value, '{0}', '{1}');";\
        """.format(production_url, local_url)
        #print '{} -Bse {}'.format(query, query_command)
        os.popen("{} -Bse {}".format(query, query_command))    


    def local_set_password():
        #dump_cmd = '{} -u{} -p{} {} -h{} -e  "{}"'.format(local_mysql, production_ssh_user, 
        #                                                    production_mysql_password, local_db, production_host, mysql_query)
        query = """UPDATE wp_users SET user_pass = MD5("{}") WHERE ID=1 LIMIT 1;""".format(local_site_password, '{}')
        #print query
        run_query(local_db_user, local_db_password, query, local_mysql, database=local_db)   

    print argv

    if '--init' in argv:
        initial = True

    if not initial:
        local_db_dump()
        local_db_drop()

    local_db_create()
    production_dump_to_local()
    local_update_urls()
    #local_set_password()

    print "SUCCESS"

if __name__ == "__main__":
  main(sys.argv[1:])