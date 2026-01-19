"""
V2T 2.1 - Database Storage
SQLite database for storing transcription history.
"""
from datetime import datetime
from typing import List, Optional
from peewee import (
    SqliteDatabase, 
    Model, 
    AutoField, 
    CharField, 
    TextField, 
    FloatField, 
    DateTimeField,
    BooleanField
)

from src.utils.constants import DATABASE_FILE


# Initialize database
db = SqliteDatabase(str(DATABASE_FILE))


class BaseModel(Model):
    """Base model with database binding."""
    class Meta:
        database = db


class Transcript(BaseModel):
    """
    Model for storing transcription records.
    """
    id = AutoField()
    title = CharField(default="Enregistrement")
    text = TextField()
    language = CharField(default="fr")
    duration = FloatField(default=0.0)  # Duration in seconds
    is_online = BooleanField(default=True)  # True = Groq, False = Offline
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = "transcripts"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "text": self.text,
            "language": self.language,
            "duration": self.duration,
            "is_online": self.is_online,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class TranscriptStorage:
    """
    Storage manager for transcripts.
    Provides CRUD operations on the database.
    """
    
    def __init__(self):
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize database and create tables if needed."""
        DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
        db.connect(reuse_if_open=True)
        db.create_tables([Transcript], safe=True)
    
    def save(
        self, 
        text: str, 
        language: str = "fr",
        duration: float = 0.0,
        is_online: bool = True,
        title: Optional[str] = None
    ) -> Transcript:
        """
        Save a new transcription to the database.
        Auto-generates title from first words if not provided.
        """
        if not title:
            # Generate title from first few words
            words = text.split()[:5]
            title = " ".join(words)[:50]
            if len(text.split()) > 5:
                title += "..."
        
        transcript = Transcript.create(
            title=title,
            text=text,
            language=language,
            duration=duration,
            is_online=is_online,
            created_at=datetime.now()
        )
        return transcript
    
    def get_all(self, limit: int = 100) -> List[Transcript]:
        """Get all transcripts, newest first."""
        return list(
            Transcript
            .select()
            .order_by(Transcript.created_at.desc())
            .limit(limit)
        )
    
    def get_by_id(self, transcript_id: int) -> Optional[Transcript]:
        """Get a specific transcript by ID."""
        try:
            return Transcript.get_by_id(transcript_id)
        except Transcript.DoesNotExist:
            return None
    
    def delete(self, transcript_id: int) -> bool:
        """Delete a transcript by ID."""
        try:
            transcript = Transcript.get_by_id(transcript_id)
            transcript.delete_instance()
            return True
        except Transcript.DoesNotExist:
            return False
    
    def search(self, query: str, limit: int = 50) -> List[Transcript]:
        """Search transcripts by text content."""
        return list(
            Transcript
            .select()
            .where(Transcript.text.contains(query))
            .order_by(Transcript.created_at.desc())
            .limit(limit)
        )
    
    def update_title(self, transcript_id: int, new_title: str) -> bool:
        """Update the title of a transcript."""
        try:
            transcript = Transcript.get_by_id(transcript_id)
            transcript.title = new_title
            transcript.save()
            return True
        except Transcript.DoesNotExist:
            return False
    
    def count(self) -> int:
        """Get total number of transcripts."""
        return Transcript.select().count()
    
    def clear_all(self) -> int:
        """Delete all transcripts. Returns number deleted."""
        return Transcript.delete().execute()


# Global instance
storage = TranscriptStorage()
