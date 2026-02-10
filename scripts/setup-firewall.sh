#!/bin/bash
# Firewall rules for PostgreSQL - Block external access
# This script configures iptables to block external access to port 5432

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "This script must be run as root"
  exit 1
fi

echo "Configuring firewall rules for PostgreSQL..."

# Drop incoming connections to PostgreSQL from external interfaces
iptables -A INPUT -p tcp --dport 5432 -i eth0 -j DROP
iptables -A INPUT -p tcp --dport 5432 -i ens+ -j DROP

# Allow localhost (keep local access working)
iptables -A INPUT -p tcp --dport 5432 -i lo -j ACCEPT
iptables -A INPUT -p tcp --dport 5432 -i docker0 -j ACCEPT

# Allow established/related connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Drop everything else
iptables -P INPUT -j DROP

# Save rules
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4

echo ""
echo "Firewall rules configured:"
echo "  - Blocked external access to PostgreSQL (port 5432)"
echo "  - Allowed local access (lo, docker0)"
echo "  - Allowed established connections"
echo ""
echo "Rules saved to /etc/iptables/rules.v4"
echo "Restart will apply these rules on reboot"
echo ""
echo "To remove these rules later:"
echo "  sudo iptables -F"
echo "  sudo rm /etc/iptables/rules.v4"
