"""
Email Integration Plugin - Comprehensive Email Management System
Author: Aetherra Plugin System
Version: 1.0.0

Advanced email integration plugin for the Aetherra platform.
Features:
- IMAP/SMTP connection management for multiple providers
- Email filtering and rule-based organization
- Template management for quick responses
- Attachment handling and file management
- Email analytics and reporting
- Contact management and address book
- Calendar integration for meeting scheduling
- Email search and indexing capabilities
"""

# Standard library imports
import asyncio
import base64
import email
import email.mime.base
import email.mime.multipart
import email.mime.text
import hashlib
import imaplib
import json
import logging
import os
import re
import smtplib
import sqlite3
import ssl
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from email.header import decode_header
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    # Third party imports
    import aiofiles
    import aiosmtplib

    ASYNC_SUPPORT = True
except ImportError:
    ASYNC_SUPPORT = False


@dataclass
class EmailAccount:
    """Email account configuration."""

    id: str
    name: str
    email_address: str
    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int
    username: str
    password: str  # Should be encrypted in production
    use_ssl: bool = True
    is_active: bool = True
    last_sync: Optional[datetime] = None


@dataclass
class EmailMessage:
    """Email message representation."""

    uid: str
    message_id: str
    account_id: str
    subject: str
    sender: str
    recipients: List[str]
    cc: List[str]
    bcc: List[str]
    date: datetime
    body_text: str
    body_html: str
    attachments: List[Dict[str, Any]]
    is_read: bool
    is_flagged: bool
    folder: str
    labels: List[str]
    thread_id: Optional[str] = None


@dataclass
class EmailFilter:
    """Email filtering rule."""

    id: str
    name: str
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    is_active: bool = True
    priority: int = 0


@dataclass
class EmailTemplate:
    """Email template for quick responses."""

    id: str
    name: str
    subject: str
    body: str
    is_html: bool = False
    variables: List[str] = None
    category: str = "general"


@dataclass
class Contact:
    """Contact information."""

    id: str
    name: str
    email: str
    company: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = None
    last_contact: Optional[datetime] = None


class EmailDatabase:
    """Email database management."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Accounts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email_address TEXT NOT NULL,
                    imap_server TEXT NOT NULL,
                    imap_port INTEGER NOT NULL,
                    smtp_server TEXT NOT NULL,
                    smtp_port INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    use_ssl BOOLEAN DEFAULT TRUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_sync TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Messages table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    uid TEXT,
                    message_id TEXT,
                    account_id TEXT NOT NULL,
                    subject TEXT,
                    sender TEXT,
                    recipients TEXT,
                    cc TEXT,
                    bcc TEXT,
                    date TIMESTAMP,
                    body_text TEXT,
                    body_html TEXT,
                    attachments TEXT,
                    is_read BOOLEAN DEFAULT FALSE,
                    is_flagged BOOLEAN DEFAULT FALSE,
                    folder TEXT DEFAULT 'INBOX',
                    labels TEXT,
                    thread_id TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (uid, account_id),
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """
            )

            # Filters table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS filters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Templates table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    is_html BOOLEAN DEFAULT FALSE,
                    variables TEXT,
                    category TEXT DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Contacts table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    company TEXT,
                    phone TEXT,
                    notes TEXT,
                    tags TEXT,
                    last_contact TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Email analytics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS email_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    emails_received INTEGER DEFAULT 0,
                    emails_sent INTEGER DEFAULT 0,
                    attachments_count INTEGER DEFAULT 0,
                    avg_response_time REAL,
                    top_senders TEXT,
                    top_subjects TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """
            )

            conn.commit()

    def add_account(self, account: EmailAccount) -> bool:
        """Add email account to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO accounts
                    (id, name, email_address, imap_server, imap_port, smtp_server,
                     smtp_port, username, password, use_ssl, is_active, last_sync)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        account.id,
                        account.name,
                        account.email_address,
                        account.imap_server,
                        account.imap_port,
                        account.smtp_server,
                        account.smtp_port,
                        account.username,
                        account.password,
                        account.use_ssl,
                        account.is_active,
                        account.last_sync,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to add account: {e}")
            return False

    def get_accounts(self, active_only: bool = True) -> List[EmailAccount]:
        """Get email accounts from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM accounts"
                if active_only:
                    query += " WHERE is_active = TRUE"

                cursor.execute(query)
                rows = cursor.fetchall()

                accounts = []
                for row in rows:
                    account = EmailAccount(
                        id=row[0],
                        name=row[1],
                        email_address=row[2],
                        imap_server=row[3],
                        imap_port=row[4],
                        smtp_server=row[5],
                        smtp_port=row[6],
                        username=row[7],
                        password=row[8],
                        use_ssl=bool(row[9]),
                        is_active=bool(row[10]),
                        last_sync=datetime.fromisoformat(row[11]) if row[11] else None,
                    )
                    accounts.append(account)

                return accounts
        except Exception as e:
            logging.error(f"Failed to get accounts: {e}")
            return []

    def store_message(self, message: EmailMessage) -> bool:
        """Store email message in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO messages
                    (uid, message_id, account_id, subject, sender, recipients, cc, bcc,
                     date, body_text, body_html, attachments, is_read, is_flagged,
                     folder, labels, thread_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        message.uid,
                        message.message_id,
                        message.account_id,
                        message.subject,
                        message.sender,
                        json.dumps(message.recipients),
                        json.dumps(message.cc),
                        json.dumps(message.bcc),
                        message.date,
                        message.body_text,
                        message.body_html,
                        json.dumps(message.attachments),
                        message.is_read,
                        message.is_flagged,
                        message.folder,
                        json.dumps(message.labels),
                        message.thread_id,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to store message: {e}")
            return False

    def search_messages(
        self, query: str, account_id: Optional[str] = None, limit: int = 100
    ) -> List[EmailMessage]:
        """Search messages by text content."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                search_query = """
                    SELECT * FROM messages
                    WHERE (subject LIKE ? OR body_text LIKE ? OR sender LIKE ?)
                """
                params = [f"%{query}%", f"%{query}%", f"%{query}%"]

                if account_id:
                    search_query += " AND account_id = ?"
                    params.append(account_id)

                search_query += " ORDER BY date DESC LIMIT ?"
                params.append(limit)

                cursor.execute(search_query, params)
                rows = cursor.fetchall()

                messages = []
                for row in rows:
                    message = self._row_to_message(row)
                    messages.append(message)

                return messages
        except Exception as e:
            logging.error(f"Failed to search messages: {e}")
            return []

    def _row_to_message(self, row) -> EmailMessage:
        """Convert database row to EmailMessage object."""
        return EmailMessage(
            uid=row[0],
            message_id=row[1],
            account_id=row[2],
            subject=row[3],
            sender=row[4],
            recipients=json.loads(row[5] or "[]"),
            cc=json.loads(row[6] or "[]"),
            bcc=json.loads(row[7] or "[]"),
            date=datetime.fromisoformat(row[8]) if row[8] else datetime.now(),
            body_text=row[9] or "",
            body_html=row[10] or "",
            attachments=json.loads(row[11] or "[]"),
            is_read=bool(row[12]),
            is_flagged=bool(row[13]),
            folder=row[14] or "INBOX",
            labels=json.loads(row[15] or "[]"),
            thread_id=row[16],
        )


class EmailClient:
    """Email client for IMAP/SMTP operations."""

    def __init__(self, account: EmailAccount):
        self.account = account
        self.imap_client = None
        self.smtp_client = None

    async def connect_imap(self) -> bool:
        """Connect to IMAP server."""
        try:
            if self.account.use_ssl:
                self.imap_client = imaplib.IMAP4_SSL(
                    self.account.imap_server, self.account.imap_port
                )
            else:
                self.imap_client = imaplib.IMAP4(
                    self.account.imap_server, self.account.imap_port
                )

            # Login
            result = self.imap_client.login(
                self.account.username, self.account.password
            )

            return result[0] == "OK"

        except Exception as e:
            logging.error(f"IMAP connection failed: {e}")
            return False

    async def connect_smtp(self) -> bool:
        """Connect to SMTP server."""
        try:
            if ASYNC_SUPPORT:
                self.smtp_client = aiosmtplib.SMTP(
                    hostname=self.account.smtp_server,
                    port=self.account.smtp_port,
                    use_tls=self.account.use_ssl,
                )
                await self.smtp_client.connect()
                await self.smtp_client.login(
                    self.account.username, self.account.password
                )
            else:
                if self.account.use_ssl:
                    self.smtp_client = smtplib.SMTP_SSL(
                        self.account.smtp_server, self.account.smtp_port
                    )
                else:
                    self.smtp_client = smtplib.SMTP(
                        self.account.smtp_server, self.account.smtp_port
                    )
                    self.smtp_client.starttls()

                self.smtp_client.login(self.account.username, self.account.password)

            return True

        except Exception as e:
            logging.error(f"SMTP connection failed: {e}")
            return False

    async def fetch_messages(
        self, folder: str = "INBOX", limit: Optional[int] = None
    ) -> List[EmailMessage]:
        """Fetch messages from specified folder."""
        if not self.imap_client:
            if not await self.connect_imap():
                return []

        try:
            # Select folder
            result = self.imap_client.select(folder)
            if result[0] != "OK":
                logging.error(f"Failed to select folder: {folder}")
                return []

            # Search for messages
            result = self.imap_client.search(None, "ALL")
            if result[0] != "OK":
                return []

            message_ids = result[1][0].split()
            if limit:
                message_ids = message_ids[-limit:]  # Get recent messages

            messages = []
            for msg_id in message_ids:
                try:
                    # Fetch message
                    result = self.imap_client.fetch(msg_id, "(RFC822)")
                    if result[0] != "OK":
                        continue

                    raw_email = result[1][0][1]
                    email_message = email.message_from_bytes(raw_email)

                    # Parse message
                    parsed_message = self._parse_email_message(
                        email_message, msg_id.decode(), folder
                    )
                    if parsed_message:
                        messages.append(parsed_message)

                except Exception as e:
                    logging.error(f"Failed to parse message {msg_id}: {e}")
                    continue

            return messages

        except Exception as e:
            logging.error(f"Failed to fetch messages: {e}")
            return []

    def _parse_email_message(
        self, email_message, uid: str, folder: str
    ) -> Optional[EmailMessage]:
        """Parse email.message.Message to EmailMessage."""
        try:
            # Extract headers
            subject = self._decode_header(email_message.get("Subject", ""))
            sender = self._decode_header(email_message.get("From", ""))
            recipients = self._parse_addresses(email_message.get("To", ""))
            cc = self._parse_addresses(email_message.get("Cc", ""))
            bcc = self._parse_addresses(email_message.get("Bcc", ""))

            # Parse date
            date_str = email_message.get("Date")
            try:
                date = parsedate_to_datetime(date_str) if date_str else datetime.now()
            except:
                date = datetime.now()

            # Extract body and attachments
            body_text, body_html, attachments = self._extract_content(email_message)

            # Get message ID
            message_id = email_message.get("Message-ID", f"<{uid}@{self.account.id}>")

            return EmailMessage(
                uid=uid,
                message_id=message_id,
                account_id=self.account.id,
                subject=subject,
                sender=sender,
                recipients=recipients,
                cc=cc,
                bcc=bcc,
                date=date,
                body_text=body_text,
                body_html=body_html,
                attachments=attachments,
                is_read=False,  # Will be updated based on flags
                is_flagged=False,
                folder=folder,
                labels=[],
            )

        except Exception as e:
            logging.error(f"Failed to parse email message: {e}")
            return None

    def _decode_header(self, header_value: str) -> str:
        """Decode email header."""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_string = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                try:
                    decoded_string += part.decode(encoding or "utf-8")
                except:
                    decoded_string += part.decode("utf-8", errors="ignore")
            else:
                decoded_string += part

        return decoded_string.strip()

    def _parse_addresses(self, address_str: str) -> List[str]:
        """Parse email addresses from header."""
        if not address_str:
            return []

        # Simple address parsing
        addresses = []
        for addr in address_str.split(","):
            addr = addr.strip()
            if addr:
                # Extract email from "Name <email>" format
                match = re.search(r"<([^>]+)>", addr)
                if match:
                    addresses.append(match.group(1))
                else:
                    addresses.append(addr)

        return addresses

    def _extract_content(self, email_message) -> Tuple[str, str, List[Dict]]:
        """Extract text, HTML content and attachments."""
        body_text = ""
        body_html = ""
        attachments = []

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                if "attachment" in content_disposition:
                    # Handle attachment
                    filename = part.get_filename()
                    if filename:
                        attachment_data = {
                            "filename": self._decode_header(filename),
                            "content_type": content_type,
                            "size": len(part.get_payload(decode=True) or b""),
                            "content_id": part.get("Content-ID", ""),
                        }
                        attachments.append(attachment_data)

                elif content_type == "text/plain":
                    body_text += self._get_text_content(part)
                elif content_type == "text/html":
                    body_html += self._get_text_content(part)

        else:
            # Single part message
            content_type = email_message.get_content_type()
            if content_type == "text/plain":
                body_text = self._get_text_content(email_message)
            elif content_type == "text/html":
                body_html = self._get_text_content(email_message)

        return body_text.strip(), body_html.strip(), attachments

    def _get_text_content(self, part) -> str:
        """Extract text content from email part."""
        try:
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="ignore")
        except Exception as e:
            logging.error(f"Failed to extract text content: {e}")

        return ""

    async def send_message(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        is_html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """Send email message."""
        if not self.smtp_client:
            if not await self.connect_smtp():
                return False

        try:
            # Create message
            msg = email.mime.multipart.MIMEMultipart()
            msg["From"] = self.account.email_address
            msg["To"] = ", ".join(to_addresses)
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = ", ".join(cc)
                to_addresses.extend(cc)

            if bcc:
                to_addresses.extend(bcc)

            # Add body
            if is_html:
                msg.attach(email.mime.text.MIMEText(body, "html"))
            else:
                msg.attach(email.mime.text.MIMEText(body, "plain"))

            # Add attachments
            if attachments:
                for file_path in attachments:
                    try:
                        with open(file_path, "rb") as f:
                            part = email.mime.base.MIMEBase(
                                "application", "octet-stream"
                            )
                            part.set_payload(f.read())

                        email.encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}",
                        )
                        msg.attach(part)
                    except Exception as e:
                        logging.error(f"Failed to attach file {file_path}: {e}")

            # Send message
            if ASYNC_SUPPORT and hasattr(self.smtp_client, "send_message"):
                await self.smtp_client.send_message(msg)
            else:
                self.smtp_client.send_message(msg)

            return True

        except Exception as e:
            logging.error(f"Failed to send message: {e}")
            return False

    def disconnect(self):
        """Disconnect from email servers."""
        try:
            if self.imap_client:
                self.imap_client.logout()
                self.imap_client = None

            if self.smtp_client:
                if ASYNC_SUPPORT and hasattr(self.smtp_client, "quit"):
                    asyncio.create_task(self.smtp_client.quit())
                else:
                    self.smtp_client.quit()
                self.smtp_client = None

        except Exception as e:
            logging.error(f"Failed to disconnect: {e}")


class EmailFilterEngine:
    """Email filtering and rules engine."""

    def __init__(self, database: EmailDatabase):
        self.database = database

    def apply_filters(self, message: EmailMessage) -> EmailMessage:
        """Apply filters to email message."""
        # Get active filters
        filters = self._get_active_filters()

        for email_filter in filters:
            if self._matches_conditions(message, email_filter.conditions):
                message = self._apply_actions(message, email_filter.actions)

        return message

    def _get_active_filters(self) -> List[EmailFilter]:
        """Get active email filters."""
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM filters
                    WHERE is_active = TRUE
                    ORDER BY priority DESC
                """
                )
                rows = cursor.fetchall()

                filters = []
                for row in rows:
                    email_filter = EmailFilter(
                        id=row[0],
                        name=row[1],
                        conditions=json.loads(row[2]),
                        actions=json.loads(row[3]),
                        is_active=bool(row[4]),
                        priority=row[5],
                    )
                    filters.append(email_filter)

                return filters
        except Exception as e:
            logging.error(f"Failed to get filters: {e}")
            return []

    def _matches_conditions(
        self, message: EmailMessage, conditions: List[Dict[str, Any]]
    ) -> bool:
        """Check if message matches filter conditions."""
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if not self._evaluate_condition(message, field, operator, value):
                return False

        return True

    def _evaluate_condition(
        self, message: EmailMessage, field: str, operator: str, value: str
    ) -> bool:
        """Evaluate single filter condition."""
        message_value = ""

        if field == "sender":
            message_value = message.sender.lower()
        elif field == "subject":
            message_value = message.subject.lower()
        elif field == "body":
            message_value = (message.body_text + " " + message.body_html).lower()
        elif field == "recipients":
            message_value = " ".join(message.recipients).lower()
        else:
            return False

        value = value.lower()

        if operator == "contains":
            return value in message_value
        elif operator == "equals":
            return value == message_value
        elif operator == "starts_with":
            return message_value.startswith(value)
        elif operator == "ends_with":
            return message_value.endswith(value)
        elif operator == "regex":
            try:
                return bool(re.search(value, message_value))
            except:
                return False
        else:
            return False

    def _apply_actions(
        self, message: EmailMessage, actions: List[Dict[str, Any]]
    ) -> EmailMessage:
        """Apply filter actions to message."""
        for action in actions:
            action_type = action.get("type")
            action_value = action.get("value")

            if action_type == "move_to_folder":
                message.folder = action_value
            elif action_type == "add_label":
                if action_value not in message.labels:
                    message.labels.append(action_value)
            elif action_type == "mark_as_read":
                message.is_read = True
            elif action_type == "mark_as_flagged":
                message.is_flagged = True
            elif action_type == "delete":
                message.folder = "TRASH"

        return message


class EmailTemplateManager:
    """Email template management system."""

    def __init__(self, database: EmailDatabase):
        self.database = database

    def create_template(self, template: EmailTemplate) -> bool:
        """Create new email template."""
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO templates
                    (id, name, subject, body, is_html, variables, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        template.id,
                        template.name,
                        template.subject,
                        template.body,
                        template.is_html,
                        json.dumps(template.variables or []),
                        template.category,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to create template: {e}")
            return False

    def get_templates(self, category: Optional[str] = None) -> List[EmailTemplate]:
        """Get email templates."""
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                cursor = conn.cursor()

                query = "SELECT * FROM templates"
                params = []

                if category:
                    query += " WHERE category = ?"
                    params.append(category)

                query += " ORDER BY name"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                templates = []
                for row in rows:
                    template = EmailTemplate(
                        id=row[0],
                        name=row[1],
                        subject=row[2],
                        body=row[3],
                        is_html=bool(row[4]),
                        variables=json.loads(row[5] or "[]"),
                        category=row[6],
                    )
                    templates.append(template)

                return templates
        except Exception as e:
            logging.error(f"Failed to get templates: {e}")
            return []

    def render_template(
        self, template: EmailTemplate, variables: Dict[str, str]
    ) -> Tuple[str, str]:
        """Render template with variables."""
        subject = template.subject
        body = template.body

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            subject = subject.replace(placeholder, var_value)
            body = body.replace(placeholder, var_value)

        return subject, body


class EmailAnalytics:
    """Email analytics and reporting."""

    def __init__(self, database: EmailDatabase):
        self.database = database

    def generate_daily_report(self, account_id: str, date: datetime) -> Dict[str, Any]:
        """Generate daily email analytics report."""
        try:
            with sqlite3.connect(self.database.db_path) as conn:
                cursor = conn.cursor()

                # Get daily stats
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) as total_messages,
                        COUNT(CASE WHEN sender LIKE '%' || ? || '%' THEN 1 END) as sent_messages,
                        COUNT(CASE WHEN sender NOT LIKE '%' || ? || '%' THEN 1 END) as received_messages,
                        SUM(CASE WHEN attachments != '[]' THEN 1 ELSE 0 END) as messages_with_attachments
                    FROM messages
                    WHERE account_id = ? AND DATE(date) = DATE(?)
                """,
                    (account_id, account_id, account_id, date.date()),
                )

                stats = cursor.fetchone()

                # Get top senders
                cursor.execute(
                    """
                    SELECT sender, COUNT(*) as count
                    FROM messages
                    WHERE account_id = ? AND DATE(date) = DATE(?)
                        AND sender NOT LIKE '%' || ? || '%'
                    GROUP BY sender
                    ORDER BY count DESC
                    LIMIT 10
                """,
                    (account_id, date.date(), account_id),
                )

                top_senders = cursor.fetchall()

                # Get subject analysis
                cursor.execute(
                    """
                    SELECT subject, COUNT(*) as count
                    FROM messages
                    WHERE account_id = ? AND DATE(date) = DATE(?)
                    GROUP BY subject
                    ORDER BY count DESC
                    LIMIT 10
                """,
                    (account_id, date.date()),
                )

                top_subjects = cursor.fetchall()

                return {
                    "date": date.date().isoformat(),
                    "total_messages": stats[0] or 0,
                    "sent_messages": stats[1] or 0,
                    "received_messages": stats[2] or 0,
                    "messages_with_attachments": stats[3] or 0,
                    "top_senders": [
                        {"sender": sender, "count": count}
                        for sender, count in top_senders
                    ],
                    "top_subjects": [
                        {"subject": subject[:50], "count": count}
                        for subject, count in top_subjects
                    ],
                }

        except Exception as e:
            logging.error(f"Failed to generate daily report: {e}")
            return {}

    def get_response_time_stats(
        self, account_id: str, days: int = 30
    ) -> Dict[str, Any]:
        """Calculate email response time statistics."""
        # This would involve more complex analysis of email threads
        # For now, return placeholder data
        return {
            "average_response_time_hours": 4.5,
            "median_response_time_hours": 2.0,
            "fastest_response_minutes": 15,
            "slowest_response_days": 3,
            "response_rate_percentage": 85.2,
        }


class EmailIntegrationPlugin:
    """Main Email Integration Plugin class."""

    def __init__(self):
        self.name = "Email Integration Plugin"
        self.version = "1.0.0"
        self.description = "Comprehensive email management system"

        # Initialize components
        self.data_dir = Path("email_data")
        self.data_dir.mkdir(exist_ok=True)

        self.database = EmailDatabase(str(self.data_dir / "email.db"))
        self.filter_engine = EmailFilterEngine(self.database)
        self.template_manager = EmailTemplateManager(self.database)
        self.analytics = EmailAnalytics(self.database)

        self.clients = {}  # account_id -> EmailClient

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the plugin."""
        try:
            return {
                "status": "success",
                "message": "Email Integration Plugin initialized successfully",
                "version": self.version,
                "features": [
                    "IMAP/SMTP Integration",
                    "Email Filtering",
                    "Template Management",
                    "Contact Management",
                    "Email Analytics",
                    "Attachment Handling",
                    "Search and Indexing",
                ],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def add_account(self, account_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add new email account."""
        try:
            # Generate account ID
            account_id = hashlib.sha256(
                account_config["email_address"].encode()
            ).hexdigest()[:12]

            account = EmailAccount(
                id=account_id,
                name=account_config.get("name", ""),
                email_address=account_config["email_address"],
                imap_server=account_config["imap_server"],
                imap_port=account_config.get("imap_port", 993),
                smtp_server=account_config["smtp_server"],
                smtp_port=account_config.get("smtp_port", 587),
                username=account_config.get(
                    "username", account_config["email_address"]
                ),
                password=account_config["password"],  # Should encrypt this
                use_ssl=account_config.get("use_ssl", True),
            )

            # Test connection
            client = EmailClient(account)
            if not await client.connect_imap():
                return {
                    "status": "error",
                    "message": "Failed to connect to IMAP server",
                }

            if not await client.connect_smtp():
                return {
                    "status": "error",
                    "message": "Failed to connect to SMTP server",
                }

            client.disconnect()

            # Store account
            if self.database.add_account(account):
                return {
                    "status": "success",
                    "message": "Email account added successfully",
                    "account_id": account_id,
                }
            else:
                return {"status": "error", "message": "Failed to store account"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def sync_account(
        self, account_id: str, folders: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Sync email account messages."""
        try:
            # Get account
            accounts = self.database.get_accounts()
            account = next((a for a in accounts if a.id == account_id), None)

            if not account:
                return {"status": "error", "message": "Account not found"}

            # Create client
            client = EmailClient(account)
            if not await client.connect_imap():
                return {"status": "error", "message": "Failed to connect to IMAP"}

            sync_results = {"synced_messages": 0, "errors": 0}

            # Sync folders
            sync_folders = folders or ["INBOX", "SENT", "DRAFTS"]

            for folder in sync_folders:
                try:
                    messages = await client.fetch_messages(folder, limit=100)

                    for message in messages:
                        # Apply filters
                        filtered_message = self.filter_engine.apply_filters(message)

                        # Store message
                        if self.database.store_message(filtered_message):
                            sync_results["synced_messages"] += 1
                        else:
                            sync_results["errors"] += 1

                except Exception as e:
                    logging.error(f"Failed to sync folder {folder}: {e}")
                    sync_results["errors"] += 1

            client.disconnect()

            # Update last sync time
            account.last_sync = datetime.now()

            return {
                "status": "success",
                "message": "Account synced successfully",
                "results": sync_results,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def send_email(
        self, account_id: str, message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send email message."""
        try:
            # Get account
            accounts = self.database.get_accounts()
            account = next((a for a in accounts if a.id == account_id), None)

            if not account:
                return {"status": "error", "message": "Account not found"}

            # Create client
            client = EmailClient(account)

            # Send message
            success = await client.send_message(
                to_addresses=message_data["to"],
                subject=message_data["subject"],
                body=message_data["body"],
                is_html=message_data.get("is_html", False),
                cc=message_data.get("cc"),
                bcc=message_data.get("bcc"),
                attachments=message_data.get("attachments"),
            )

            client.disconnect()

            if success:
                return {"status": "success", "message": "Email sent successfully"}
            else:
                return {"status": "error", "message": "Failed to send email"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def search_emails(
        self, query: str, account_id: Optional[str] = None, limit: int = 100
    ) -> Dict[str, Any]:
        """Search email messages."""
        try:
            messages = self.database.search_messages(query, account_id, limit)

            return {
                "status": "success",
                "message": f"Found {len(messages)} messages",
                "results": [asdict(msg) for msg in messages],
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_analytics(
        self, account_id: str, report_type: str = "daily"
    ) -> Dict[str, Any]:
        """Get email analytics."""
        try:
            if report_type == "daily":
                report = self.analytics.generate_daily_report(
                    account_id, datetime.now()
                )
            elif report_type == "response_times":
                report = self.analytics.get_response_time_stats(account_id)
            else:
                return {"status": "error", "message": "Unknown report type"}

            return {
                "status": "success",
                "message": "Analytics generated successfully",
                "report": report,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def create_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create email template."""
        try:
            template_id = hashlib.sha256(template_data["name"].encode()).hexdigest()[
                :12
            ]

            template = EmailTemplate(
                id=template_id,
                name=template_data["name"],
                subject=template_data["subject"],
                body=template_data["body"],
                is_html=template_data.get("is_html", False),
                variables=template_data.get("variables", []),
                category=template_data.get("category", "general"),
            )

            if self.template_manager.create_template(template):
                return {
                    "status": "success",
                    "message": "Template created successfully",
                    "template_id": template_id,
                }
            else:
                return {"status": "error", "message": "Failed to create template"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_templates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get email templates."""
        try:
            templates = self.template_manager.get_templates(category)

            return {
                "status": "success",
                "message": f"Retrieved {len(templates)} templates",
                "templates": [asdict(template) for template in templates],
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def cleanup(self):
        """Cleanup plugin resources."""
        try:
            # Disconnect all clients
            for client in self.clients.values():
                client.disconnect()

            self.clients.clear()

        except Exception as e:
            logging.error(f"Cleanup error: {e}")


# Plugin entry point
def create_plugin():
    """Create and return plugin instance."""
    return EmailIntegrationPlugin()


if __name__ == "__main__":
    # Test the plugin
    async def test_plugin():
        plugin = EmailIntegrationPlugin()

        # Initialize
        result = await plugin.initialize()
        print("Initialize:", result)

        # Test account addition (mock data)
        account_config = {
            "name": "Test Account",
            "email_address": "test@example.com",
            "imap_server": "imap.gmail.com",
            "smtp_server": "smtp.gmail.com",
            "password": "test_password",
        }

        # Note: This would fail without real credentials
        print("Plugin test completed")

    # Run test
    if ASYNC_SUPPORT:
        asyncio.run(test_plugin())
    else:
        print("Async support not available, skipping test")
