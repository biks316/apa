from django.db import models
from django.views.decorators.http import require_GET
from django.http import JsonResponse
# --- AJAX autocomplete endpoint ---
@require_GET
def autocomplete_suggestions(request):
	"""Return up to 10 suggestions for autocomplete, matching topic/title/summary."""
	q = request.GET.get('q', '').strip()
	page = int(request.GET.get('page', '1'))
	if len(q) < 3:
		return JsonResponse({'results': [], 'has_next': False})
	# Search in topic, title, summary
	docs = FetchedDocument.objects.select_related('topic').filter(
		models.Q(topic__name__icontains=q) |
		models.Q(title__icontains=q) |
		models.Q(summary__icontains=q)
	).order_by('-fetched_at')
	# Pagination
	start = (page - 1) * 10
	end = start + 10
	results = []
	for doc in docs[start:end]:
		results.append(doc.topic.name if doc.topic else doc.title or doc.summary)
	has_next = docs.count() > end
	return JsonResponse({'results': results, 'has_next': has_next})
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils.text import slugify
from .models import FetchedDocument, Topic, RichContent

import hashlib
import logging

try:
	import wikipedia
except Exception:  # keep broad so missing package doesn't break import-time
	wikipedia = None
	logging.getLogger(__name__).warning("wikipedia package not available; fetch_item will error if called")


# Create your views here.


def index(request):
	"""Basic index placeholder for the app."""
	return JsonResponse({"status": "ok", "app": "generate_store"})



# --- Helper functions ---

def fetch_wikipedia_summary(topic, max_sentences=5):
	"""Fetch summary from Wikipedia, handle errors, and return (chunks, page_url, error)."""
	if wikipedia is None:
		return None, None, {"error": "wikipedia package not installed on server."}
	try:
		summary = wikipedia.summary(topic, sentences=max_sentences)
		sentences = summary.split('. ')
		chunks = [s.strip() + ('.' if not s.strip().endswith('.') else '') for s in sentences if len(s.strip()) > 20]
	except wikipedia.exceptions.DisambiguationError as e:
		return None, None, {"error": "Topic is ambiguous.", "options": e.options[:10]}
	except wikipedia.exceptions.PageError:
		return None, None, {"error": "Topic not found on Wikipedia."}
	except Exception as e:
		logging.getLogger(__name__).exception("Unexpected error fetching wikipedia summary")
		return None, None, {"error": "Unexpected error", "detail": str(e)}
	# get page URL if possible
	try:
		page = wikipedia.page(topic)
		page_url = page.url
	except Exception:
		page_url = None
	return chunks, page_url, None

def store_chunks_in_db(topic, topic_slug, chunks, page_url):
	"""Store each chunk as a FetchedDocument, dedup by hash. Returns (created, skipped)."""
	topic_obj, _ = Topic.objects.get_or_create(name=topic, defaults={"slug": topic_slug})
	created = []
	skipped = 0
	for i, chunk in enumerate(chunks):
		h = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
		if FetchedDocument.objects.filter(content_hash=h).exists():
			skipped += 1
			continue
		doc = FetchedDocument.objects.create(
			topic=topic_obj,
			title=f"{topic} (part {i+1})",
			summary=(chunk[:1000] if len(chunk) > 1000 else chunk),
			content=chunk,
			source_url=page_url or "",
			source_type="wikipedia",
			content_hash=h,
			is_processed=False,
		)
		created.append({"id": doc.pk, "title": doc.title})
	return created, skipped

def fetch_item(request):
	"""Endpoint for fetching Wikipedia info and storing in DB only if not present."""
	topic = request.GET.get("topic") or request.POST.get("topic")
	if not topic:
		return JsonResponse({"error": "Missing 'topic' parameter."}, status=400)
	max_sentences = request.GET.get("max_sentences") or request.POST.get("max_sentences")
	try:
		max_sentences = int(max_sentences) if max_sentences is not None else 5
	except ValueError:
		max_sentences = 5
	topic_slug = slugify(topic)

	# Check if topic already exists in DB
	topic_obj = Topic.objects.filter(name=topic).first()
	if topic_obj:
		docs = FetchedDocument.objects.filter(topic=topic_obj).order_by('-fetched_at')
		if docs.exists():
			print(f"[INFO] Topic '{topic}' found in database. Returning cached data.")
			data = [
				{
					"id": d.pk,
					"title": d.title,
					"summary": d.summary,
					"content": d.content,
					"source_url": d.source_url,
					"fetched_at": d.fetched_at.isoformat(),
				} for d in docs
			]
			return JsonResponse({"from_db": True, "count": len(data), "documents": data})

	# If not present, fetch from Wikipedia
	print(f"[INFO] Topic '{topic}' not found in database. Fetching fresh data from Wikipedia.")
	chunks, page_url, error = fetch_wikipedia_summary(topic, max_sentences)
	if error:
		return JsonResponse(error, status=400 if 'ambiguous' in error.get('error','').lower() or 'not found' in error.get('error','').lower() else 500)
	created, skipped = store_chunks_in_db(topic, topic_slug, chunks, page_url)
	return JsonResponse({"from_db": False, "created": len(created), "skipped_duplicates": skipped, "documents": created})


from django.apps import apps

def get_model_urls(app_label):
	"""Return a list of (model_name, url) for all models in the app."""
	model_urls = []
	for model in apps.get_app_config(app_label).get_models():
		name = model._meta.verbose_name_plural.title()
		# convention: url is /generate/<model_name_plural>/
		url = f"/generate/{model._meta.model_name}s/"
		model_urls.append((name, url))
	return model_urls

def list_documents(request):
	"""Render a template showing all FetchedDocument records and unique topics for filtering, plus dynamic sidebar."""
	documents = FetchedDocument.objects.select_related('topic').order_by('-fetched_at')
	topics = Topic.objects.order_by('name').values_list('name', flat=True).distinct()
	sidebar_tables = get_model_urls('generate_store')
	return render(request, 'generate_store/documents_list.html', {
		'documents': documents,
		'topics': topics,
		'sidebar_tables': sidebar_tables,
	})


def richcontent_list(request):
	"""Render a list of RichContent entries."""
	items = RichContent.objects.select_related('topic').order_by('-created_at')
	return render(request, 'generate_store/richcontent_list.html', {'items': items})


def richcontent_detail(request, pk: int):
	"""Render a single RichContent entry."""
	item = get_object_or_404(RichContent, pk=pk)
	return render(request, 'generate_store/richcontent_detail.html', {'item': item})


def document_detail(request, pk: int):
	"""Return a small JSON representation of a single document."""
	doc = get_object_or_404(FetchedDocument, pk=pk)
	return JsonResponse({
		"id": doc.pk,
		"title": doc.title,
		"summary": doc.summary,
		"content": doc.content,
		"source_url": doc.source_url,
		"fetched_at": doc.fetched_at.isoformat(),
	})
