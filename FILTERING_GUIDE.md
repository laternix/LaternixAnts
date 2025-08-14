# Keyword Filtering Guide for Evergabe Scraper

## Overview
The scraper uses an intelligent filtering system to find relevant results while avoiding false matches.

## How It Works

### 1. **Whole Word Matching** (Enabled by Default)
When `use_word_boundaries: true` in config.yaml, the scraper matches whole words only.

**Examples:**
- ✅ "LED" matches: "LED-Beleuchtung", "LED Straßenlampen", "Neue LED"  
- ❌ "LED" does NOT match: "Lederverarbeitung", "lediglich", "Schmiede"

- ✅ "Mast" matches: "Lichtmast", "Mast-Beleuchtung", "neuer Mast"
- ❌ "Mast" does NOT match: "Masterstudium", "Master", "Webmaster"

### 2. **Inclusion Keywords** 
Results must contain at least ONE of these keywords to be included:

```yaml
filter_keywords:
  - "straßen"
  - "lampe"
  - "leuchte"
  - "led"
  - "beleuchtung"
  - "licht"
  - "mast"
  - "laternen"
```

### 3. **Exclusion Keywords**
Results containing ANY of these keywords are automatically excluded:

```yaml
exclude_keywords:
  - "leder"        # Excludes leather-related results
  - "lediglich"    # Excludes "merely/only" contexts
  - "master"       # Excludes master's degree programs
  - "masterstudium"
  - "semester"     # Excludes academic contexts
```

## Configuration Options

### In config.yaml:

```yaml
search:
  # Keywords that MUST appear (at least one)
  filter_keywords:
    - "led"
    - "beleuchtung"
    - "straßenleuchte"
    
  # Enable whole word matching (recommended)
  use_word_boundaries: true
  
  # Keywords that cause exclusion
  exclude_keywords:
    - "leder"
    - "master"
```

### Behavior Examples:

| Search Result | With Word Boundaries | Without Word Boundaries | Excluded? |
|--------------|---------------------|------------------------|-----------|
| "LED-Straßenbeleuchtung" | ✅ Matches | ✅ Matches | No |
| "Lederverarbeitung" | ❌ No match | ✅ Matches (LED in LeDer) | No/Yes |
| "Masterstudium" | ❌ No match | ✅ Matches (mast) | Yes (excluded) |
| "Lichtmast installation" | ✅ Matches | ✅ Matches | No |
| "Nur lediglich eine Info" | ❌ No match | ❌ No match | Yes (excluded) |

## Tips for Better Results

1. **Use Specific Terms**: Instead of just "LED", also include "LED-Beleuchtung", "LED-Leuchte"

2. **Add Context Keywords**: Include terms like:
   - "straßenbeleuchtung"
   - "öffentliche beleuchtung"
   - "verkehrsweg"
   - "gehweg"

3. **Exclude Common False Positives**: Add to exclude_keywords:
   - Academic terms: "bachelor", "master", "semester", "studium"
   - Unrelated: "leder", "kleidung", "textil"
   - Context words: "lediglich", "jedoch", "allerdings"

4. **Test Your Configuration**: Run with `--test` flag to check filtering:
   ```bash
   python3 run.py --test --max-pages 1
   ```

## Troubleshooting

**Too many false positives?**
- Enable `use_word_boundaries: true`
- Add more exclude_keywords

**Missing relevant results?**
- Check if word boundaries are too strict
- Add more variations to filter_keywords
- Consider compound words: "straßenleuchte" vs "straßen" + "leuchte"

**Want substring matching for specific terms?**
- Set `use_word_boundaries: false` (but be aware of false positives)
- Or use more specific search terms

## Advanced: Custom Patterns

For complex matching needs, you can modify the scraper code to add custom regex patterns:

```python
# Example: Match LED followed by a number (LED50, LED-100, etc.)
pattern = r'\bLED[-\s]?\d+\b'
```

Contact support if you need help with advanced filtering patterns.