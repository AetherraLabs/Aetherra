# core/memory.py
import os
import json
from datetime import datetime
import re

MEMORY_FILE = "memory_store.json"

class NeuroMemory:
    def __init__(self):
        self.memory = []
        self.load()

    def load(self):
        """Load memories from persistent storage"""
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r") as f:
                self.memory = json.load(f)

    def save(self):
        """Save memories to persistent storage"""
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)

    def remember(self, text, tags=None, category="general"):
        """Store text in memory with optional tags and category"""
        if tags is None:
            tags = ["general"]
        
        memory_entry = {
            "text": text,
            "timestamp": str(datetime.now()),
            "tags": tags,
            "category": category
        }
        
        self.memory.append(memory_entry)
        self.save()

    def recall(self, tags=None, category=None, limit=None):
        """Recall memories, optionally filtered by tags or category"""
        if tags is None and category is None:
            memories = [m["text"] for m in self.memory]
        else:
            filtered_memories = []
            for m in self.memory:
                # Check if memory matches tag filter
                tag_match = tags is None or any(tag in m.get("tags", []) for tag in tags)
                # Check if memory matches category filter
                category_match = category is None or m.get("category") == category
                
                if tag_match and category_match:
                    filtered_memories.append(m["text"])
            memories = filtered_memories
        
        # Apply limit if specified
        if limit and len(memories) > limit:
            memories = memories[-limit:]
        
        return memories
    
    def search(self, query, case_sensitive=False):
        """Search memories by content"""
        results = []
        search_flags = 0 if case_sensitive else re.IGNORECASE
        
        try:
            pattern = re.compile(query, search_flags)
        except re.error:
            # If regex compilation fails, treat as literal string
            query_lower = query.lower() if not case_sensitive else query
            for m in self.memory:
                text_to_search = m["text"].lower() if not case_sensitive else m["text"]
                if query_lower in text_to_search:
                    results.append(m["text"])
            return results
        
        # Use regex search
        for m in self.memory:
            if pattern.search(m["text"]):
                results.append(m["text"])
        
        return results
    
    def get_tags(self):
        """Get all unique tags from memory"""
        all_tags = set()
        for m in self.memory:
            all_tags.update(m.get("tags", []))
        return sorted(list(all_tags))
    
    def get_categories(self):
        """Get all unique categories from memory"""
        categories = set()
        for m in self.memory:
            categories.add(m.get("category", "general"))
        return sorted(list(categories))
    
    def get_memory_summary(self):
        """Get a summary of memory organization"""
        return {
            "total_memories": len(self.memory),
            "tags": self.get_tags(),
            "categories": self.get_categories()
        }
    
    def patterns(self):
        """Analyze patterns in memory organization"""
        tag_frequency = {}
        category_frequency = {}
        temporal_patterns = []
        
        for m in self.memory:
            # Tag patterns
            for tag in m.get("tags", []):
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            
            # Category patterns
            category = m.get("category", "general")
            category_frequency[category] = category_frequency.get(category, 0) + 1
            
            # Temporal patterns
            temporal_patterns.append(m.get("timestamp", ""))
        
        return {
            "tag_frequency": tag_frequency,
            "category_frequency": category_frequency,
            "temporal_patterns": temporal_patterns,
            "most_frequent_tags": sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_frequent_categories": sorted(category_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def get_memories_by_timeframe(self, hours=24):
        """Get memories from the last N hours"""
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []
        
        for m in self.memory:
            try:
                memory_time = datetime.fromisoformat(m.get("timestamp", "").replace("Z", "+00:00"))
                if memory_time >= cutoff_time:
                    recent_memories.append(m["text"])
            except (ValueError, AttributeError):
                # Skip memories with invalid timestamps
                continue
        
        return recent_memories
    
    def delete_memories_by_tag(self, tag):
        """Delete memories containing a specific tag"""
        original_count = len(self.memory)
        self.memory = [m for m in self.memory if tag not in m.get("tags", [])]
        deleted_count = original_count - len(self.memory)
        
        if deleted_count > 0:
            self.save()
        
        return deleted_count
    
    def get_memory_stats(self):
        """Get detailed statistics about memory usage"""
        if not self.memory:
            return "No memories stored"
        
        patterns = self.patterns()
        recent_count = len(self.get_memories_by_timeframe(24))
        
        stats = f"""Memory Statistics:
📊 Total memories: {len(self.memory)}
🕐 Recent (24h): {recent_count}
🏷️  Unique tags: {len(self.get_tags())}
📂 Categories: {len(self.get_categories())}

Top Tags: {', '.join([f'{tag}({count})' for tag, count in patterns['most_frequent_tags'][:3]])}
Top Categories: {', '.join([f'{cat}({count})' for cat, count in patterns['most_frequent_categories'][:3]])}"""
        
        return stats
    
    def pattern_analysis(self, pattern, frequency_threshold="weekly", timeframe_days=30):
        """Analyze memory patterns and their frequency"""
        from datetime import datetime, timedelta
        
        # Calculate timeframe
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        # Find memories matching the pattern
        matching_memories = []
        for m in self.memory:
            try:
                memory_date = datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00").split("+")[0])
                if memory_date >= cutoff_date:
                    if pattern.lower() in m["text"].lower():
                        matching_memories.append(m)
            except (ValueError, KeyError):
                # Skip memories with invalid timestamps
                continue
        
        # Calculate frequency
        frequency_count = len(matching_memories)
        
        # Determine if pattern meets frequency threshold
        frequency_map = {
            "daily": frequency_count >= timeframe_days * 0.8,  # 80% of days
            "weekly": frequency_count >= timeframe_days / 7,  # At least weekly
            "monthly": frequency_count >= 1,  # At least once per month
            "rare": frequency_count >= 1  # At least once
        }
        
        meets_threshold = frequency_map.get(frequency_threshold, False)
        
        return {
            "pattern": pattern,
            "matches": frequency_count,
            "timeframe_days": timeframe_days,
            "frequency_threshold": frequency_threshold,
            "meets_threshold": meets_threshold,
            "matching_memories": matching_memories,
            "analysis": f"Pattern '{pattern}' found {frequency_count} times in {timeframe_days} days"
        }
    
    def get_pattern_frequency(self, pattern, timeframe_days=30):
        """Get the frequency of a pattern in memory"""
        analysis = self.pattern_analysis(pattern, "rare", timeframe_days)
        return analysis["matches"]
    
    def detect_recurring_patterns(self, min_frequency=3, timeframe_days=30):
        """Detect recurring patterns in memory automatically"""
        from collections import defaultdict
        from datetime import datetime, timedelta
        
        # Extract common phrases and terms
        phrase_patterns = defaultdict(int)
        
        cutoff_date = datetime.now() - timedelta(days=timeframe_days)
        
        for m in self.memory:
            try:
                memory_date = datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00").split("+")[0])
                if memory_date >= cutoff_date:
                    text = m["text"].lower()
                    
                    # Extract 2-3 word phrases
                    words = re.findall(r'\b\w+\b', text)
                    for i in range(len(words) - 1):
                        phrase = " ".join(words[i:i+2])
                        phrase_patterns[phrase] += 1
                    
                    for i in range(len(words) - 2):
                        phrase = " ".join(words[i:i+3])
                        phrase_patterns[phrase] += 1
            except (ValueError, KeyError):
                continue
        
        # Filter by minimum frequency
        recurring = {
            "phrases": {phrase: count for phrase, count in phrase_patterns.items() 
                       if count >= min_frequency},
            "analysis_date": str(datetime.now()),
            "timeframe_days": timeframe_days,
            "min_frequency": min_frequency
        }
        
        return recurring
    
    def pattern(self, pattern_name, frequency="weekly"):
        """Check if a pattern meets the frequency threshold - simplified interface"""
        analysis = self.pattern_analysis(pattern_name, frequency)
        return analysis["meets_threshold"]
