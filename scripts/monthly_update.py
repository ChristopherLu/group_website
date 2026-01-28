#!/usr/bin/env python3
"""
Interactive Monthly Website Update Script

This script helps you perform monthly updates to your academic group website:
1. Update publications from DBLP
2. Manage research highlights
3. Update team members (add newcomers, move leavers to alumni)

Usage:
    python scripts/monthly_update.py [--all | --publications | --highlights | --team]

Requirements:
    pip install pyyaml rich inquirer
"""

import os
import sys
import argparse
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

# Add _cite to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "_cite"))

import yaml
from yaml.loader import SafeLoader

try:
    import inquirer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install pyyaml rich inquirer")
    sys.exit(1)

console = Console()

# Paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
CITATIONS_FILE = PROJECT_ROOT / "_data" / "citations.yaml"
HIGHLIGHTS_FILE = PROJECT_ROOT / "_data" / "highlights.yaml"
SOURCES_FILE = PROJECT_ROOT / "_data" / "sources.yaml"
MEMBERS_DIR = PROJECT_ROOT / "_members"
ALUMNI_DIR = MEMBERS_DIR / "alumni"
CITE_DIR = PROJECT_ROOT / "_cite"


def load_yaml(path):
    """Load YAML file safely"""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf8") as f:
        data = yaml.load(f, Loader=SafeLoader)
        return data if data else []


def save_yaml(path, data, header_comment=None):
    """Save data to YAML file"""
    yaml.Dumper.ignore_aliases = lambda *args: True
    with open(path, "w", encoding="utf8") as f:
        if header_comment:
            f.write(f"# {header_comment}\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def run_citation_update():
    """Run the citation generation script"""
    console.print("\n[bold blue]Running citation update...[/bold blue]")
    # Run from project root since cite.py uses Path.cwd() for finding data files
    result = subprocess.run(
        ["python", "_cite/cite.py"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        console.print("[green]Citations updated successfully![/green]")
    else:
        console.print(f"[red]Error updating citations:[/red]\n{result.stderr}")
    return result.returncode == 0


# ============================================================================
# PUBLICATIONS MANAGEMENT
# ============================================================================

def show_publications_summary():
    """Display current publications summary"""
    citations = load_yaml(CITATIONS_FILE)
    highlights = load_yaml(HIGHLIGHTS_FILE)

    # Group by year
    by_year = {}
    for pub in citations:
        year = pub.get("date", "")[:4] or "Unknown"
        by_year.setdefault(year, []).append(pub)

    table = Table(title="Current Publications Summary")
    table.add_column("Year", style="cyan")
    table.add_column("Count", style="green")

    for year in sorted(by_year.keys(), reverse=True):
        table.add_row(year, str(len(by_year[year])))

    table.add_row("─" * 10, "─" * 5)
    table.add_row("[bold]Total[/bold]", f"[bold]{len(citations)}[/bold]")
    table.add_row("[yellow]Highlights[/yellow]", f"[yellow]{len(highlights)}[/yellow]")

    console.print(table)


def update_publications_menu():
    """Interactive menu for updating publications"""
    console.print(Panel("[bold]Publications Update[/bold]", style="blue"))
    show_publications_summary()

    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=[
                ("Fetch new publications from DBLP (run cite.py)", "dblp"),
                ("Show recent publications", "show_recent"),
                ("Back to main menu", "back"),
            ],
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    action = answer["action"]

    if action == "dblp":
        update_from_dblp()
    elif action == "show_recent":
        show_recent_publications()


def update_from_dblp():
    """Update publications using DBLP plugin"""
    console.print("\n[bold]Updating from DBLP...[/bold]")

    # Load current citations for comparison
    old_citations = load_yaml(CITATIONS_FILE)
    old_ids = {c.get("id") for c in old_citations if c.get("id")}

    # Run the citation update
    if run_citation_update():
        # Compare with new citations
        new_citations = load_yaml(CITATIONS_FILE)
        new_ids = {c.get("id") for c in new_citations if c.get("id")}

        added = new_ids - old_ids
        if added:
            console.print(f"\n[green]Found {len(added)} new publication(s):[/green]")
            for pub in new_citations:
                if pub.get("id") in added:
                    console.print(f"  • {pub.get('title', 'Untitled')[:60]}...")
        else:
            console.print("\n[yellow]No new publications found.[/yellow]")


def show_recent_publications(limit=10):
    """Show the most recent publications"""
    citations = load_yaml(CITATIONS_FILE)

    # Sort by date
    sorted_pubs = sorted(
        citations,
        key=lambda x: x.get("date", "") or "",
        reverse=True
    )[:limit]

    table = Table(title=f"Recent {limit} Publications")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Venue", style="green", max_width=20)

    for pub in sorted_pubs:
        table.add_row(
            pub.get("date", "N/A")[:10],
            (pub.get("title", "Untitled") or "Untitled")[:50],
            (pub.get("publisher", "") or "")[:20]
        )

    console.print(table)


# ============================================================================
# HIGHLIGHTS MANAGEMENT
# ============================================================================

def manage_highlights_menu():
    """Interactive menu for managing research highlights"""
    console.print(Panel("[bold]Research Highlights Management[/bold]", style="yellow"))

    highlights = load_yaml(HIGHLIGHTS_FILE)
    citations = load_yaml(CITATIONS_FILE)

    # Show current highlights
    console.print("\n[bold]Current Highlights:[/bold]")
    if highlights:
        for i, h in enumerate(highlights, 1):
            console.print(f"  {i}. {h.get('title', 'Untitled')[:60]}")
    else:
        console.print("  [dim]No highlights configured[/dim]")

    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=[
                ("Add a new highlight", "add"),
                ("Remove a highlight", "remove"),
                ("Reorder highlights", "reorder"),
                ("Edit highlight description/image", "edit"),
                ("Back to main menu", "back"),
            ],
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    action = answer["action"]

    if action == "add":
        add_highlight(citations, highlights)
    elif action == "remove":
        remove_highlight(highlights)
    elif action == "reorder":
        reorder_highlights(highlights)
    elif action == "edit":
        edit_highlight(highlights)


def add_highlight(citations, highlights):
    """Add a new publication to highlights"""
    # Get IDs of current highlights
    highlight_ids = {h.get("id") for h in highlights}

    # Filter out already highlighted publications
    available = [c for c in citations if c.get("id") not in highlight_ids]

    if not available:
        console.print("[yellow]All publications are already highlighted![/yellow]")
        return

    # Sort by date (most recent first)
    available.sort(key=lambda x: x.get("date", "") or "", reverse=True)

    # Create choices
    choices = [
        (f"{p.get('date', 'N/A')[:4]} - {p.get('title', 'Untitled')[:50]}", p)
        for p in available[:30]  # Limit to recent 30
    ]

    questions = [
        inquirer.List(
            "publication",
            message="Select a publication to highlight",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    pub = answer["publication"]

    # Ask for additional highlight info
    detail_questions = [
        inquirer.Text(
            "description",
            message="Enter a short description for the highlight",
            default=pub.get("description", ""),
        ),
        inquirer.Text(
            "image",
            message="Image path (e.g., images/works/paper.png)",
            default=pub.get("image", ""),
        ),
    ]

    details = inquirer.prompt(detail_questions)
    if not details:
        return

    # Create highlight entry
    highlight = {
        "id": pub.get("id"),
        "title": pub.get("title"),
        "authors": pub.get("authors", []),
        "publisher": pub.get("publisher", ""),
        "date": pub.get("date", ""),
        "link": pub.get("link", ""),
        "type": pub.get("type", "paper-conference"),
    }

    if details["description"]:
        highlight["description"] = details["description"]
    if details["image"]:
        highlight["image"] = details["image"]

    highlights.append(highlight)

    # Save
    save_yaml(
        HIGHLIGHTS_FILE,
        highlights,
        "Featured/highlighted publications with custom images and descriptions\n# This file is manually maintained and won't be overwritten by auto-generation"
    )
    console.print(f"[green]Added '{pub.get('title')[:40]}...' to highlights![/green]")


def remove_highlight(highlights):
    """Remove a publication from highlights"""
    if not highlights:
        console.print("[yellow]No highlights to remove.[/yellow]")
        return

    choices = [(h.get("title", "Untitled")[:60], i) for i, h in enumerate(highlights)]

    questions = [
        inquirer.List(
            "index",
            message="Select highlight to remove",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    removed = highlights.pop(answer["index"])
    save_yaml(
        HIGHLIGHTS_FILE,
        highlights,
        "Featured/highlighted publications with custom images and descriptions\n# This file is manually maintained and won't be overwritten by auto-generation"
    )
    console.print(f"[green]Removed '{removed.get('title')[:40]}...' from highlights.[/green]")


def reorder_highlights(highlights):
    """Reorder highlights"""
    if len(highlights) < 2:
        console.print("[yellow]Need at least 2 highlights to reorder.[/yellow]")
        return

    console.print("\nCurrent order:")
    for i, h in enumerate(highlights, 1):
        console.print(f"  {i}. {h.get('title', 'Untitled')[:50]}")

    questions = [
        inquirer.Text(
            "new_order",
            message="Enter new order (e.g., '3,1,2' to move 3rd to first)",
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    try:
        new_indices = [int(x.strip()) - 1 for x in answer["new_order"].split(",")]
        if len(new_indices) != len(highlights):
            raise ValueError("Must include all items")
        if sorted(new_indices) != list(range(len(highlights))):
            raise ValueError("Invalid indices")

        new_highlights = [highlights[i] for i in new_indices]
        save_yaml(
            HIGHLIGHTS_FILE,
            new_highlights,
            "Featured/highlighted publications with custom images and descriptions\n# This file is manually maintained and won't be overwritten by auto-generation"
        )
        console.print("[green]Highlights reordered![/green]")

    except (ValueError, IndexError) as e:
        console.print(f"[red]Invalid order: {e}[/red]")


def edit_highlight(highlights):
    """Edit a highlight's description or image"""
    if not highlights:
        console.print("[yellow]No highlights to edit.[/yellow]")
        return

    choices = [(h.get("title", "Untitled")[:60], i) for i, h in enumerate(highlights)]

    questions = [
        inquirer.List(
            "index",
            message="Select highlight to edit",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    highlight = highlights[answer["index"]]

    edit_questions = [
        inquirer.Text(
            "description",
            message="Description",
            default=highlight.get("description", ""),
        ),
        inquirer.Text(
            "image",
            message="Image path",
            default=highlight.get("image", ""),
        ),
    ]

    edits = inquirer.prompt(edit_questions)
    if not edits:
        return

    if edits["description"]:
        highlight["description"] = edits["description"]
    elif "description" in highlight:
        del highlight["description"]

    if edits["image"]:
        highlight["image"] = edits["image"]
    elif "image" in highlight:
        del highlight["image"]

    save_yaml(
        HIGHLIGHTS_FILE,
        highlights,
        "Featured/highlighted publications with custom images and descriptions\n# This file is manually maintained and won't be overwritten by auto-generation"
    )
    console.print("[green]Highlight updated![/green]")


# ============================================================================
# TEAM MEMBER MANAGEMENT
# ============================================================================

def manage_team_menu():
    """Interactive menu for managing team members"""
    console.print(Panel("[bold]Team Member Management[/bold]", style="green"))

    # Show current members
    members = list(MEMBERS_DIR.glob("*.md"))
    alumni = list(ALUMNI_DIR.glob("*.md")) if ALUMNI_DIR.exists() else []

    console.print(f"\n[bold]Current Team:[/bold] {len(members)} members")
    console.print(f"[bold]Alumni:[/bold] {len(alumni)} members")

    # Show member names
    for member_file in sorted(members):
        info = parse_member_file(member_file)
        role = info.get("role", "member")
        console.print(f"  • {info.get('name', member_file.stem)} [{role}]")

    questions = [
        inquirer.List(
            "action",
            message="What would you like to do?",
            choices=[
                ("Add a new team member", "add"),
                ("Move a member to alumni", "to_alumni"),
                ("Edit a member's profile", "edit"),
                ("View all alumni", "view_alumni"),
                ("Back to main menu", "back"),
            ],
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    action = answer["action"]

    if action == "add":
        add_team_member()
    elif action == "to_alumni":
        move_to_alumni(members)
    elif action == "edit":
        edit_team_member(members)
    elif action == "view_alumni":
        view_alumni(alumni)


def parse_member_file(path):
    """Parse a member markdown file and extract front matter"""
    with open(path, "r", encoding="utf8") as f:
        content = f.read()

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            front_matter = yaml.load(parts[1], Loader=SafeLoader) or {}
            bio = parts[2].strip()
            return {**front_matter, "_bio": bio, "_path": path}

    return {"_bio": content, "_path": path}


def add_team_member():
    """Add a new team member"""
    console.print("\n[bold]Add New Team Member[/bold]")

    questions = [
        inquirer.Text("name", message="Full name"),
        inquirer.List(
            "role",
            message="Role",
            choices=[
                ("PhD Student", "phd"),
                ("Postdoc", "postdoc"),
                ("Master's Student", "masters"),
                ("Undergraduate", "undergrad"),
                ("Visiting Researcher", "visiting"),
                ("Research Assistant", "programmer"),
            ],
        ),
        inquirer.Text("email", message="Email (optional)"),
        inquirer.Text("homepage", message="Homepage URL (optional)"),
        inquirer.Editor("bio", message="Biography (press Enter to open editor)"),
    ]

    answers = inquirer.prompt(questions)
    if not answers:
        return

    # Generate filename
    now = datetime.now()
    name_slug = answers["name"].lower().replace(" ", "-").replace(".", "")
    filename = f"{now.year}-{now.month:02d}-{name_slug}.md"

    # Build front matter
    front_matter = {
        "name": answers["name"],
        "role": answers["role"],
    }

    # Add optional fields
    links = {}
    if answers.get("email"):
        links["email"] = answers["email"]
    if answers.get("homepage"):
        links["home-page"] = answers["homepage"]
    if links:
        front_matter["links"] = links

    # Create file content
    content = "---\n"
    content += yaml.dump(front_matter, default_flow_style=False, sort_keys=False, allow_unicode=True)
    content += "---\n\n"
    content += answers.get("bio", "").strip() + "\n"

    # Write file
    member_path = MEMBERS_DIR / filename
    with open(member_path, "w", encoding="utf8") as f:
        f.write(content)

    console.print(f"\n[green]Created member profile: {filename}[/green]")
    console.print(f"[dim]Don't forget to add a photo to images/member_photos/[/dim]")


def move_to_alumni(members):
    """Move a team member to alumni"""
    if not members:
        console.print("[yellow]No members to move.[/yellow]")
        return

    # Filter out PI
    movable = []
    for m in members:
        info = parse_member_file(m)
        if info.get("role") != "principal-investigator":
            movable.append((info.get("name", m.stem), m))

    if not movable:
        console.print("[yellow]No members available to move to alumni.[/yellow]")
        return

    questions = [
        inquirer.List(
            "member",
            message="Select member to move to alumni",
            choices=movable,
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    member_path = answer["member"]

    # Ensure alumni directory exists
    ALUMNI_DIR.mkdir(exist_ok=True)

    # Move file
    new_path = ALUMNI_DIR / member_path.name
    shutil.move(str(member_path), str(new_path))

    console.print(f"[green]Moved {member_path.name} to alumni/[/green]")


def edit_team_member(members):
    """Edit a team member's profile"""
    if not members:
        console.print("[yellow]No members to edit.[/yellow]")
        return

    choices = []
    for m in members:
        info = parse_member_file(m)
        choices.append((info.get("name", m.stem), m))

    questions = [
        inquirer.List(
            "member",
            message="Select member to edit",
            choices=choices,
        )
    ]

    answer = inquirer.prompt(questions)
    if not answer:
        return

    member_path = answer["member"]
    console.print(f"\n[dim]Opening {member_path} in your default editor...[/dim]")
    console.print("[dim]Edit the file manually, then save and close.[/dim]")

    # Open in default editor
    editor = os.environ.get("EDITOR", "nano")
    subprocess.run([editor, str(member_path)])


def view_alumni(alumni):
    """View all alumni members"""
    if not alumni:
        console.print("[yellow]No alumni found.[/yellow]")
        return

    table = Table(title="Alumni")
    table.add_column("Name", style="cyan")
    table.add_column("Role", style="green")

    for alumni_file in sorted(alumni):
        info = parse_member_file(alumni_file)
        table.add_row(
            info.get("name", alumni_file.stem),
            info.get("role", "member")
        )

    console.print(table)


# ============================================================================
# MAIN MENU
# ============================================================================

def main_menu():
    """Main interactive menu"""
    console.print(Panel(
        "[bold]Academic Website Monthly Update Tool[/bold]\n"
        "[dim]Update publications, highlights, and team members[/dim]",
        style="blue"
    ))

    while True:
        questions = [
            inquirer.List(
                "section",
                message="What would you like to update?",
                choices=[
                    ("📚 Publications (DBLP)", "publications"),
                    ("⭐ Research Highlights", "highlights"),
                    ("👥 Team Members", "team"),
                    ("🔄 Run full citation update", "cite"),
                    ("❌ Exit", "exit"),
                ],
            )
        ]

        answer = inquirer.prompt(questions)
        if not answer or answer["section"] == "exit":
            console.print("\n[dim]Goodbye![/dim]")
            break

        section = answer["section"]

        if section == "publications":
            update_publications_menu()
        elif section == "highlights":
            manage_highlights_menu()
        elif section == "team":
            manage_team_menu()
        elif section == "cite":
            run_citation_update()

        console.print()  # Add spacing


def main():
    parser = argparse.ArgumentParser(
        description="Interactive monthly website update tool"
    )
    parser.add_argument(
        "--publications", "-p",
        action="store_true",
        help="Jump directly to publications update"
    )
    parser.add_argument(
        "--highlights", "-r",
        action="store_true",
        help="Jump directly to highlights management"
    )
    parser.add_argument(
        "--team", "-t",
        action="store_true",
        help="Jump directly to team management"
    )
    parser.add_argument(
        "--cite", "-c",
        action="store_true",
        help="Just run the citation update script"
    )

    args = parser.parse_args()

    # Jump to specific section if requested
    if args.publications:
        update_publications_menu()
    elif args.highlights:
        manage_highlights_menu()
    elif args.team:
        manage_team_menu()
    elif args.cite:
        run_citation_update()
    else:
        main_menu()


if __name__ == "__main__":
    main()
