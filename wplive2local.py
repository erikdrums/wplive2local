#!/usr/bin/python

import sys
import os
import os.path
import syslog
import errno
import logging
import subprocess
import yaml
from bunch import Bunch

def main(argv):
    HOME_PATH = os.path.expanduser('~')
    CONFIG_PATH = os.path.join(HOME_PATH, '.wplive2local_conf')
    initial = False

    try:
        configurations = yaml.load(open(CONFIG_PATH).read())
        conf = Bunch.fromDict(configurations)
        local = conf.local
        sites = conf.sites
    except IOError:
        print "NO SETTINGS FILE"
        sys.exit()    
    print argv, argv[0]
    try:
        site = argv[0]
        site_conf = sites[site]
        site_local = site_conf.local
        site_production = site_conf.production
    except KeyError:
        print "This is not a configured site"
        sys.exit()    

    print local
    print "Begin Migration"


    def _build_query(user, password, runtype='mysql', host='localhost', database=None):
        if database is None:
            database = ''
        return "{} -u{} -p{} {} -h{}".format(runtype, user, password, database, host)

    def _build_query_command(user, password, query_command, runtype='mysql', 
                                                    host='localhost', database=None):
        query = _build_query(user, password, runtype, host, database)
        return "{} -e '{}'".format(query, query_command)


    def _run_query(user, password, query, runtype='mysql', host='localhost', database=None):
        print _build_query_command(user, password, query, runtype, host, database)
        os.popen(_build_query_command(user, password, query, runtype, host, database))

    def local_db_dump():
        dump_query = " --opt -c " + site_local.db + " > " + site_local.backup_path + ".sql"
        query_command = "{} -e --opt -c {} > {}.sql".format(
                    _build_query(local.db_user, local.db_password, local.mysqldump), 
                                                site_local.db, site_local.backup_path)
        os.popen(query_command)
    
    def local_db_drop():
        dump_query = "drop database {}".format(site_local.db)
        _run_query(local.db_user, local.db_password, dump_query, local.mysql)    

    def local_db_create():
        dump_query = "create database {}".format(site_local.db)
        _run_query(local.db_user, local.db_password, dump_query, local.mysql)    

    
    def production_dump_to_local():
        production_query = _build_query(site_production.db_user, 
            site_production.db_password, 'mysqldump', database=site_production.db)
        local_query = _build_query(local.db_user, local.db_password, 
                                                    local.mysql, database=site_local.db)
        command = "ssh {}@{} '{} | gzip -9' | gzip -d | {}".format(
            site_production.ssh_user, site_production.ssh_address, production_query, 
                                                                        local_query)
        
        os.popen(command)


    def local_update_urls():
        query = _build_query(local.db_user, local.db_password, local.mysql, 
                                                                database=site_local.db)
        query_command = """ "UPDATE wp_options \
            SET option_value = replace(option_value, '{0}', '{1}')\
            WHERE option_name = 'home' OR option_name = 'siteurl';\
            UPDATE wp_posts SET guid = replace(guid, '{0}', '{1}');\
            UPDATE wp_posts SET post_content = replace(post_content, '{0}', '{1}');\
            UPDATE wp_postmeta SET meta_value = replace(meta_value, '{0}', '{1}');";\
        """.format(site_production.url, site_local.url)
        os.popen("{} -Bse {}".format(query, query_command))    


    def local_set_password():
        query = """UPDATE wp_users SET user_pass = MD5("{}") WHERE ID=1 LIMIT 1;
                                                """.format(local.site_password, '{}')
        _run_query(local.db_user, local.db_password, query, local.mysql, 
                                                                database=site_local.db)   

    if '--init' in argv:
        initial = True

    if not initial:
        local_db_dump()
        local_db_drop()

    local_db_create()
    production_dump_to_local()
    local_update_urls()
    local_set_password()

    print "SUCCESS"
 
if __name__ == "__main__":
  main(sys.argv[1:])
