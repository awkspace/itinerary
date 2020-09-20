#!/usr/bin/env python3

import logging
import os
import psycopg2
import time
from psycopg2 import sql


class Migration:

    def __init__(self, conn, config):

        if not config:
            config = {}

        self.conn = conn
        self.config = config

        if 'lock_id' not in self.config:
            self.config['lock_id'] = 0
        if 'path' not in self.config:
            self.config['path'] = 'migrations'
        if 'version_table' not in self.config:
            self.config['version_table'] = '_version'

        self.version_table = sql.Identifier(
            self.config['version_table'])

    def migrate(self):
        self.acquire_lock()
        try:
            self.load_migrations()
            version = self.get_db_version()
            self.run_migrations_from(version)
        finally:
            self.release_lock()

    def acquire_lock(self):
        with self.conn.cursor() as cur:
            while True:
                try:
                    cur.execute(
                        "select pg_try_advisory_lock(%s)",
                        (self.config['lock_id'],))
                    self.conn.commit()
                    if cur.fetchone()[0] is True:
                        break
                    else:
                        time.sleep(1)
                except psycopg2.OperationalError:
                    time.sleep(1)

    def release_lock(self):
        with self.conn.cursor() as cur:
            cur.execute(
                "select pg_advisory_unlock(%s)", (self.config['lock_id'],))
            self.conn.commit()

    def get_db_version(self):
        with self.conn.cursor() as cur:
            cur.execute(
                sql.SQL("create table if not exists {} (version int)").format(
                    sql.Identifier(self.config['version_table'])))
            self.conn.commit()
            cur.execute(sql.SQL("select version from {}").format(
                sql.Identifier(self.config['version_table'])))
            if cur.rowcount == 0:
                cur.execute(
                    sql.SQL("insert into {} (version) values (0)").format(
                        sql.Identifier(self.config['version_table'])))
                self.conn.commit()
                return 0
            else:
                return cur.fetchone()[0]

    def load_migrations(self):
        sql_dir = self.config['path']
        self.migrations = {}
        for filename in os.listdir(sql_dir):
            try:
                migration_id = int(filename.split('_')[0])
            except ValueError:
                raise RuntimeError(
                    f'Could not parse id from migration file: {filename}')
            if migration_id in self.migrations.keys():
                raise RuntimeError(
                    f'Found two migrations with identical id: {migration_id}')
            with open(os.path.join(sql_dir, filename), 'r') as sql:
                self.migrations.update({
                    migration_id: {
                        'name': filename,
                        'sql': sql.read()
                    }
                })

    def run_migrations_from(self, version):

        for migration_id in sorted(self.migrations.keys()):

            if migration_id <= version:
                continue
            migration = self.migrations[migration_id]

            logging.getLogger('itinerary').info(
                f'Applying migration: {migration["name"]}')

            with self.conn.cursor() as cur:
                try:
                    cur.execute(migration['sql'])
                    statement = sql.SQL("update {} set version = %s").format(
                        sql.Identifier(self.config['version_table']))
                    cur.execute(statement, (migration_id,))
                    self.conn.commit()
                except Exception:
                    self.conn.rollback()
                    raise
