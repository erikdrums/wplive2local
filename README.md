# wplive2local

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
