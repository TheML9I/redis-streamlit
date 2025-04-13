# redis-streamlit

Redis-Streamlit is a web-based application built with Streamlit that provides an intuitive interface for interacting with a Redis database. It allows users to perform CRUD operations on various Redis data types, monitor Redis server performance, and explore server statistics in real-time.

## Features

- **Write Data**: Add and manage data in Redis, including Strings, Hashes, Lists, Sets, and Sorted Sets.
- **Read Data**: View and retrieve data stored in Redis, with support for inspecting key types and TTLs.
- **Monitoring**: Monitor Redis server performance, including memory usage, command statistics, and keyspace information.
- **Server Info**: Explore detailed Redis server information, including version, uptime, and persistence settings.
- **Backup Support**: Automated Redis backups using a custom script for RDB and AOF files.
- **Prometheus Integration**: Redis Exporter for monitoring Redis metrics with Prometheus.

## Architecture

The project is containerized using Docker and orchestrated with Docker Compose. It includes the following services:
- **Redis**: A high-availability Redis instance with custom configuration.
- **Streamlit App**: A Python-based web application for interacting with Redis.
- **Redis Exporter**: Exposes Redis metrics for Prometheus monitoring.
- **Redis Backup**: Automates periodic backups of Redis data.

## Getting Started

### Prerequisites
- Docker and Docker Compose installed on your system.

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd redis-streamlit

