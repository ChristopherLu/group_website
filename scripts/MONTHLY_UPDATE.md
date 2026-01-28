# Monthly Website Update Guide

This guide describes how to perform monthly updates to your academic group website.

## Quick Start

```bash
# Install dependencies (first time only)
pip install -r scripts/requirements.txt

# Run the interactive update tool
python scripts/monthly_update.py
```

## What Gets Updated

### 1. Publications

Publications are fetched from multiple sources and merged into `_data/citations.yaml`:

- **DBLP** - Configured in `_data/dblp.yaml` with your author PID
- **ORCID** - Configured in `_data/orcid.yaml`
- **Google Scholar** - Configured in `_data/google-scholar.yaml`
- **Manual entries** - Added to `_data/sources.yaml`
- **BibTeX import** - Via bibtex-to-manubot tool

### 2. Research Highlights

Highlights are manually curated in `_data/highlights.yaml`. These appear prominently on the research page with:
- Custom images
- Custom descriptions
- Featured positioning

### 3. Team Members

Team member profiles are stored in `_members/`:
- Current members: `_members/*.md`
- Alumni: `_members/alumni/*.md`

## Usage Options

### Interactive Mode (Recommended)

```bash
python scripts/monthly_update.py
```

This launches an interactive menu where you can:
- Update publications from DBLP
- Import from BibTeX files
- Add/remove/reorder research highlights
- Add new team members
- Move members to alumni

### Direct Commands

```bash
# Jump to publications
python scripts/monthly_update.py --publications

# Jump to highlights
python scripts/monthly_update.py --highlights

# Jump to team management
python scripts/monthly_update.py --team

# Just run citation update
python scripts/monthly_update.py --cite
```

## Publication Sources

### DBLP (Recommended)

Your DBLP profile is configured in `_data/dblp.yaml`:

```yaml
- author_id: "154/4313"  # Your DBLP PID
```

Find your PID: Go to your DBLP page (e.g., `https://dblp.org/pid/154/4313.html`), the PID is `154/4313`.

### BibTeX Import

For publications not in DBLP, you can import from BibTeX:

1. Export BibTeX from your source (Google Scholar, conference site, etc.)
2. Run the update tool and select "Import from BibTeX file"
3. The tool uses [bibtex-to-manubot](https://github.com/ChristopherLu/bibtex-to-manubot)

Install bibtex-to-manubot:
```bash
pip install git+https://github.com/ChristopherLu/bibtex-to-manubot.git
```

### Manual Entries

Add publications manually to `_data/sources.yaml`:

```yaml
- id: doi:10.1234/example
  # Optional overrides:
  title: "Custom Title"
  description: "Custom description"
```

## Managing Highlights

Highlights appear on the Research page with rich formatting. To add a highlight:

1. Run `python scripts/monthly_update.py --highlights`
2. Select "Add a new highlight"
3. Choose from your publications
4. Add a description and image path

Highlight images should be placed in `images/works/` (recommended size: 800x400px).

## Managing Team Members

### Adding New Members

1. Run `python scripts/monthly_update.py --team`
2. Select "Add a new team member"
3. Fill in the details

The script creates a file like `_members/2026-01-firstname-lastname.md`.

Don't forget to add their photo to `images/member_photos/`.

### Moving to Alumni

1. Run `python scripts/monthly_update.py --team`
2. Select "Move a member to alumni"
3. Choose the member

The file is moved from `_members/` to `_members/alumni/`.

## File Structure

```
_data/
├── citations.yaml      # Auto-generated (DO NOT EDIT)
├── highlights.yaml     # Manually curated highlights
├── sources.yaml        # Manual publication entries
├── dblp.yaml          # DBLP configuration
├── orcid.yaml         # ORCID configuration
└── types.yaml         # Publication type definitions

_members/
├── chris-lu.md        # PI profile
├── 2024-10-name.md    # Current members
└── alumni/
    └── 2023-06-name.md # Alumni profiles

_cite/
├── cite.py            # Citation generation script
└── plugins/
    ├── dblp.py        # DBLP plugin
    ├── orcid.py       # ORCID plugin
    └── ...
```

## Using with Claude Code

You can also use Claude Code as an interactive assistant for updates:

```
> Help me with my monthly website update

> Add the new paper "Title" to my highlights

> Create a profile for new PhD student John Doe

> Move Jane Smith to alumni - she graduated last month
```

Claude Code can read and modify the relevant files directly.

## Troubleshooting

### Citations not updating

1. Check that your DBLP PID is correct in `_data/dblp.yaml`
2. Clear the cache: `rm -rf _cite/.cache`
3. Run manually: `cd _cite && python cite.py`

### BibTeX import fails

1. Ensure bibtex-to-manubot is installed
2. Check your BibTeX file is valid
3. Try converting manually first

### Missing publication

Some publications may not have DOIs. Add them manually to `_data/sources.yaml`:

```yaml
- title: "Paper without DOI"
  authors:
    - Author One
    - Author Two
  publisher: "Conference Name"
  date: "2025-01-15"
  link: "https://example.com/paper"
```
