-- Local development database setup for Nexora (run once as the postgres superuser):
--   psql -U postgres -h localhost -f infra/local/create_local_db.sql
-- Creates a non-superuser application role plus a dev and a test database.
-- The password below is for local development only. Never reuse it anywhere else.

\set ON_ERROR_STOP on

SELECT 'CREATE ROLE nexora LOGIN PASSWORD ''nexora_local_dev'' NOSUPERUSER NOCREATEDB NOCREATEROLE'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'nexora')\gexec

SELECT 'CREATE DATABASE nexora OWNER nexora'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nexora')\gexec

SELECT 'CREATE DATABASE nexora_test OWNER nexora'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'nexora_test')\gexec

\echo 'Done: role nexora, databases nexora and nexora_test'
