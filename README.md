# wplive2local
This script was made to make wordpress migration easier, by automating the
following steps:
* create backup of current local database
* reset local database by deleting and recreating it
* do a mysqldump on production site and distibute it into local database
* set wordpress siteurl and other absolute urls correctly according to local
  url
* set local admin password to configured password across all sites in
  configuration to make login easier

You need python package 'bunch' installed

You need to create a configuration file in your home directory named
.wplive2local_conf

in the format:
```
# Local configuration
local:
    mysql: 'mysql'
    mysqldump: 'mysqldump'
    db_user: 'root'
    db_password: 'root'
    site_password: 'password'

# Sites configurations
sites:
    jyllandsakvariet:
        local:
            db: 'dbname'
            wp_table_prefix: 'wp_' # Optional
            url: 'http://localhost/amazingsite.com'
            backup_path: '/tmp/amazingsite_backup'
        production:
            ssh_user: 'root'
            ssh_address: 'http://amazingsite.com'
            db_user: 'root'
            db_password: 'password'# Optional
            host: 'localhost'
            url: 'http://amazingsite.com'
            db: 'dbname'
```

## Two switches exist:
* --init, no initial backup is made. Use the first time only.
* --lock-tables-false, for avoiding mysql table lock when dumping database.
