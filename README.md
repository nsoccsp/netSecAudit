# nSocCSP - Network Security Operations Dashboard

A comprehensive network security monitoring and operations dashboard built with Streamlit.

## Features Overview

### 1. Security Event Monitoring

- Real-time security event tracking
- Event severity classification
- Historical event analysis
- Alert management and notification system

### 2. Network Traffic Analysis

- Protocol-level traffic monitoring
- Bandwidth utilization tracking
- Geographic traffic flow visualization
- Anomaly detection

### 3. System Performance

- CPU, memory, and disk usage monitoring
- Network interface statistics
- Service availability tracking
- Performance trend analysis

### 4. Network Topology

- Interactive network map
- Device relationship visualization
- Dynamic topology updates
- Layer 2/3 mapping capabilities

### 5. Device Inventory Management

- Comprehensive device tracking
- Multi-vendor support
  - Cisco devices (CDP)
  - Mikrotik devices (MDP)
  - General network devices (LLDP)
- Automated device discovery
- Compliance monitoring

### 6. Incident Response

- Automated incident creation
- Response workflow management
- Integration with security tools
- Incident tracking and reporting

## Network Discovery Protocols

The system supports multiple network discovery protocols:

- **LLDP (Link Layer Discovery Protocol)**

  - Industry-standard protocol
  - Vendor-neutral device discovery
  - Layer 2 neighbor detection

- **CDP (Cisco Discovery Protocol)**

  - Cisco-proprietary protocol
  - Detailed Cisco device information
  - Network topology mapping

- **MDP (Mikrotik Discovery Protocol)**
  - Mikrotik-specific protocol
  - RouterOS device discovery
  - Neighbor information collection

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 16
- Network monitoring tools:
  - nmap
  - tcpdump
  - wireshark
- System libraries:
  - cairo
  - ffmpeg
  - freetype
  - gtk3
  - imagemagick
  - pkg-config

## Installation

1. Clone the repository:

```bash
git clone https://github.com/nsoccsp/netSecAudit.git
cd netSecAudit
```

2. Install system dependencies (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install -y postgresql python3 python3-pip python3-dev libpq-dev build-essential nmap tcpdump wireshark
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install Virtual Environment and Python dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -r pyproject.toml
```

3. 1. Locally: Create database and admin user to initialize

```Bash
sudo -u postgres psql <<EOF
CREATE DATABASE netsecaudit;
CREATE USER nsocadmin WITH PASSWORD 'nsocadmin';
GRANT ALL PRIVILEGES ON DATABASE netsecaudit TO nsocadmin;
\c netsecaudit
GRANT ALL PRIVILEGES ON SCHEMA public TO nsocadmin;
EOF
```
3. 2. In Github Codespace: Create the database and user manually

```Bash
sudo service postgresql start
sudo sed -i 's/peer/trust/g' /etc/postgresql/*/main/pg_hba.conf && sudo service postgresql restart
```
```Bash
psql -U postgres <<EOF
CREATE DATABASE netsecaudit;
CREATE USER nsocadmin WITH PASSWORD 'nsocadmin';
GRANT ALL PRIVILEGES ON DATABASE netsecaudit TO nsocadmin;
\c netsecaudit
GRANT ALL PRIVILEGES ON SCHEMA public TO nsocadmin;
EOF
```
# Make sure you are connected to the database on Codespace:

```Bash
psql -U nsocadmin -d netsecaudit -c "\conninfo"
```

# Export environment variables

export DATABASE_URL="postgresql://nsocadmin:nsocadmin@127.0.0.1:5432/netsecaudit"

# Check the PostgreSQL logs

```Bash
sudo tail -f /var/log/postgresql/postgresql-*.log
```

4. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:

```bash
python seed_data.py
```

# Verify tables were created

```Bash
psql $DATABASE_URL -c "\dt"
```

## Running the Application

1. Start the application:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 5000
```

2. Access the web interface at `http://localhost:5000`

## Development

The application is structured as follows:

- `app.py`: Main application entry point
- `pages/`: Individual dashboard pages
- `components/`: Reusable UI components
- `database/`: Database models and utilities
- `data/`: Data generation and mock utilities

## Security Considerations

- Keep API keys and credentials secure in `.env`
- Regular security audits recommended
- Monitor system logs for unauthorized access
- Update dependencies regularly

## Troubleshooting

Common issues and solutions:

1. Database Connection:

   - Verify PostgreSQL is running
   - Check credentials in `.env`
   - Ensure database exists

2. Network Discovery:

   - Check interface permissions
   - Verify protocol support on network
   - Monitor firewall rules

3. Performance Issues:
   - Check system resources
   - Monitor database queries
   - Review log files
