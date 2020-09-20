#!/usr/bin/env python3

from itinerary.migration import Migration

__all__ = ['auto_migrate']


def auto_migrate(conn, **kwargs):
    migration = Migration(conn, kwargs)
    migration.migrate()
