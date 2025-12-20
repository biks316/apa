import wikipedia

class WikipediaService:
    @staticmethod
    def get_summary_chunks(topic, max_sentences=10):
        try:
            summary = wikipedia.summary(topic, sentences=max_sentences)
            sentences = summary.split('. ')
            chunks = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]
            return chunks
        except wikipedia.exceptions.DisambiguationError as e:
            return [f"Topic is ambiguous. Try one of these: {', '.join(e.options[:5])}"]
        except wikipedia.exceptions.PageError:
            return ["Topic not found on Wikipedia."]
        except Exception as e:
            return [f"An error occurred: {str(e)}"]
