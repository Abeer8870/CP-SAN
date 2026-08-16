TOOL_REGISTRY = {
    "read_file": {
        "description": "Reads contents of a single specified file",
        "allowed_params": {
            "path": {
                "type": "string",
                "scope": "Read a specific file path provided by user",
                "forbidden_patterns": [
                    # System files
                    "/etc/passwd", "/etc/shadow", "/etc/sudoers",
                    "/etc/hosts", "/etc/crontab", "/etc/ssh",
                    # Credential files
                    ".env", "credentials", "secret", "private_key",
                    ".pem", ".key", "token", "api_key",
                    # Database files
                    "database.yml", "database.yaml", "db_credentials",
                    ".sqlite", "db.json",
                    # Shell config
                    ".bashrc", ".profile", ".bash_history",
                    # Windows equivalents
                    "win.ini", "system32", "sam", "ntds",
                    # Generic sensitive
                    "password", "passwd", "auth", "login",
                    "config/secrets", "id_rsa", "authorized_keys"
                    # Log files — add these
                    "/var/log", "/var/backups","/var/lib","webserver.log",     
                    "security-audit", "app-error.log","db_backup",".sql", 
                    "access.log", "error.log", "system.log"             
                ]
            }
        },
        "risk_level": "medium"
    },
    "send_email": {
        "description": "Sends email to a specified recipient",
        "allowed_params": {
            "to": {
                "type": "string",
                "scope": "Email address explicitly provided by user",
                "forbidden_patterns": [
                    # Obvious external
                    "attacker", "evil", "hack", "exfil",
                    "malware", "exploit",
                    # Generic external indicators
                    "archive.com", "backup-external", "remote-log",
                    "collection", "harvest"
                ]
            },
            "body": {
                "type": "string",
                "scope": "Message content related to user task only",
                "forbidden_patterns": [
                    "password", "passwd", "token", "secret",
                    "credential", "api_key", "private_key",
                    "auth_token", "access_key", "db_password",
                    "connection_string", "ssh_key", "/var/log",
                    "auth.log", "system configuration",
                    "user list", "internal data"
                ]
            }
        },
        "risk_level": "high"
    },
    "execute_command": {
        "description": "Runs a shell command explicitly requested by user",
        "allowed_params": {
            "command": {
                "type": "string",
                "scope": "Only commands directly requested by user",
                "forbidden_patterns": [
                    # Destructive
                    "rm -rf", "mkfs", "dd if=",
                    "shred", "wipefs",
                    # Network exfil
                    "curl", "wget", "nc ", "netcat",
                    "ncat", "socat", "telnet",
                    # Reverse shells
                    "bash -i", "/dev/tcp", "python -c",
                    "perl -e", "ruby -e", "php -r",
                    # Privilege
                    "chmod 777", "chmod +s", "chown root",
                    "sudo su", "passwd root",
                    # Persistence
                    "crontab", "@reboot", "systemctl enable",
                    "update-rc.d", "chkconfig",
                    # Collection
                    "tar -czf /home", "zip -r /home",
                    "find / -name", "locate password",
                    # Encoding/obfuscation
                    "base64 -d", "base64 --decode",
                    "eval", "exec(",
                    # Package abuse
                    "pip install", "npm install",
                    "apt-get install", "yum install"
                ]
            }
        },
        "risk_level": "critical"
    },
    "write_file": {
        "description": "Writes content to a specified file path",
        "allowed_params": {
            "path": {
                "type": "string",
                "scope": "File path explicitly provided by user",
                "forbidden_patterns": [
                    # System paths
                    "/etc/", "/usr/", "/bin/", "/sbin/",
                    "/lib/", "/boot/", "/sys/", "/proc/","/home/user/.",
                    # Persistence paths
                    "crontab", ".bashrc", ".profile",
                    ".bash_profile", ".bash_logout",
                    "/etc/init.d/", "/etc/rc",
                    "startup", "autostart",
                    # Windows persistence
                    "startup", "appdata/roaming/microsoft/windows/start menu",
                    "system32",
                    # Sensitive locations
                    # Sensitive locations
                    "/root/", "/var/log/",
                    "authorized_keys", ".ssh/",
                    "/home/user/.",    # hidden files in home only
                ]
            },
            "content": {
                "type": "string",
                "scope": "Content directly provided by user",
                "forbidden_patterns": [
                    "curl attacker", "wget attacker",
                    "bash -i", "nc -e", "reverse shell",
                    "/bin/bash", "chmod +x",
                    "NOPASSWD", "ALL=(ALL)",
                    "credential", "password:",
                    "api_key:", "token:", "secret:"
                ]
            }
        },
        "risk_level": "high"
    },
    "list_directory": {
        "description": "Lists files in a directory specified by user",
        "allowed_params": {
            "path": {
                "type": "string",
                "scope": "Directory explicitly specified by user",
                "forbidden_patterns": [
                    # System directories
                    "/etc", "/root", "/var/log",
                    "/proc", "/sys", "/boot",
                    "/var/backups","/var/lib",
                    # Sensitive directories
                    "private", "secret", ".ssh",
                    "credentials", "backup/",
                    # User data
                    "/home/user/.","/home/$","/root", "users/","users/system",
                    # Windows sensitive
                    "system32", "windows/",
                    "appdata", "programdata"
                ]
            }
        },
        "risk_level": "low"
    }
}