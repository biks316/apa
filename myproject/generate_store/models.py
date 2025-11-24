from django.db import models
from django.utils import timezone


# Models to store fetched data and metadata for efficient retrieval by topic


class Topic(models.Model):
	"""A simple topic/category to group fetched items.

	Keeping topics as a separate model allows efficient joins and
	normalization when many documents share the same topic.
	"""

	name = models.CharField(max_length=200, unique=True)
	slug = models.SlugField(max_length=200, unique=True)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now, editable=False)

	class Meta:
		ordering = ["name"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return self.name


class FetchedDocument(models.Model):
	"""Stores a single fetched item (web page, snippet, file) together with metadata.

	Fields chosen to allow efficient filtering by topic, source, and time.
	A JSONField named `metadata` allows storing arbitrary provider-specific
	information (headers, response status, MIME type, etc.).
	"""

	topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name="documents")
	title = models.CharField(max_length=1000, blank=True)
	summary = models.TextField(blank=True)
	content = models.TextField(blank=True)
	source_url = models.URLField(max_length=2000, blank=True, db_index=True)
	source_type = models.CharField(max_length=100, blank=True, help_text="e.g. 'web', 'pdf', 'docx', 'api'")
	author = models.CharField(max_length=300, blank=True)
	language = models.CharField(max_length=10, blank=True, db_index=True)

	# Optional JSON blob for arbitrary metadata (response headers, crawl info, etc.)
	metadata = models.JSONField(default=dict, blank=True)

	# a hash of the content to avoid duplicates and speed lookups
	content_hash = models.CharField(max_length=128, blank=True, db_index=True)

	fetched_at = models.DateTimeField(default=timezone.now, db_index=True)
	last_accessed = models.DateTimeField(null=True, blank=True)

	# small flag to indicate post-processing status (e.g. indexed, embedded)
	is_processed = models.BooleanField(default=False, db_index=True)

	# small free-form tags column; for heavy tag usage consider a separate Tag model
	tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")

	# store a small serialized embedding or pointer to it; keep optional and DB-agnostic
	embedding = models.JSONField(null=True, blank=True, help_text="Optional vector embedding as list of floats")

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-fetched_at"]
		indexes = [
			models.Index(fields=["topic", "fetched_at"]),
			models.Index(fields=["source_url"]),
			models.Index(fields=["content_hash"]),
		]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.title or self.source_url or self.pk}"

	def mark_accessed(self) -> None:
		"""Update last_accessed timestamp for simple LRU-like tracking."""
		self.last_accessed = timezone.now()
		self.save(update_fields=["last_accessed"])
