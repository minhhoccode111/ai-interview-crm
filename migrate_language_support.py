#!/usr/bin/env python3
"""
Database migration script to add language support fields
Run this script to add language preference fields to existing database
"""

import sqlite3
import os
from datetime import datetime


def migrate_database():
    """Add language support fields to existing database"""
    # Check multiple possible database locations
    possible_paths = [
        "interview.db",
        "instance/interview.db",
        os.path.join("instance", "interview.db"),
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break

    if not db_path:
        print("Database file not found in any of the expected locations:")
        for path in possible_paths:
            print(f"  - {path}")
        print("Creating new database with language support...")
        return

    print(f"Found database at: {db_path}")
    print("Starting database migration for language support...")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]

        cursor.execute("PRAGMA table_info(interviews)")
        interview_columns = [column[1] for column in cursor.fetchall()]

        # Add preferred_language column to users table if it doesn't exist
        if "preferred_language" not in user_columns:
            print("Adding preferred_language column to users table...")
            cursor.execute(
                """
                ALTER TABLE users
                ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'en'
            """
            )
            print("✓ Added preferred_language column to users table")
        else:
            print("✓ preferred_language column already exists in users table")

        # Add language column to interviews table if it doesn't exist
        if "language" not in interview_columns:
            print("Adding language column to interviews table...")
            cursor.execute(
                """
                ALTER TABLE interviews
                ADD COLUMN language VARCHAR(5) DEFAULT 'en'
            """
            )
            print("✓ Added language column to interviews table")
        else:
            print("✓ language column already exists in interviews table")

        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")

        # Show current table schemas
        print("\n📋 Updated table schemas:")

        print("\nUsers table:")
        cursor.execute("PRAGMA table_info(users)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")

        print("\nInterviews table:")
        cursor.execute("PRAGMA table_info(interviews)")
        for column in cursor.fetchall():
            print(f"  - {column[1]} ({column[2]})")

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Migration error: {e}")
    finally:
        if conn:
            conn.close()


def create_backup():
    """Create a backup of the current database"""
    # Check multiple possible database locations
    possible_paths = [
        "interview.db",
        "instance/interview.db",
        os.path.join("instance", "interview.db"),
    ]

    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break

    if db_path:
        backup_path = f'interview_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
        import shutil

        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backup created: {backup_path}")
        return backup_path
    return None


if __name__ == "__main__":
    print("🚀 AI Interview CRM - Language Support Migration")
    print("=" * 50)

    # Create backup first
    backup_file = create_backup()
    if backup_file:
        print(f"📦 Backup created: {backup_file}")

    # Run migration
    migrate_database()

    print("\n🎉 Migration complete! You can now use multi-language features.")
    print("\nSupported languages:")
    print("  🇺🇸 English (en)")
    print("  🇻🇳 Vietnamese (vi)")
    print("\nRestart your application to use the new features.")
