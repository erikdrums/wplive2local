# wplive2local
This script was made to make wordpress migration easier, by automating the
following steps:

1. Create backup of current local database
2. Reset local database by deleting and recreating it
3. Do a mysqldump on production site and distibute it into local database
4. Set wordpress siteurl and other absolute urls correctly according to local
  url
5. Set local admin password to configured password across all sites in
  configuration to make login easier

You need two python packages:
sudo pip install PyYAML bunch

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
    amazingsite:
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
    other_amazingsite:
        local:
            ...
        production
            ...
```

## Two switches exist:
* --init, no initial backup is made. Use the first time only.
* --lock-tables-false, for avoiding mysql table lock when dumping database.
