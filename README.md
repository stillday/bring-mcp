# bring-mcp

MCP Server für [Bring!](https://www.getbring.com/) Shopping-Listen — nutzbar in Claude Code, Claude Desktop und allen anderen MCP-kompatiblen Clients.

## Installation & Nutzung

### Claude Code (einmalig global einrichten)

```bash
claude mcp add \
  -e BRING_EMAIL=deine@email.com \
  -e BRING_PASSWORD=deinPasswort \
  --scope user \
  bring -- uvx --from git+https://github.com/stillday/bring-mcp bring-mcp
```

### Claude Desktop App

Konfigurationsdatei öffnen:
- **Linux:** `~/.config/Claude/claude_desktop_config.json`
- **Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Eintragen:
```json
{
  "mcpServers": {
    "bring": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/stillday/bring-mcp", "bring-mcp"],
      "env": {
        "BRING_EMAIL": "deine@email.com",
        "BRING_PASSWORD": "deinPasswort"
      }
    }
  }
}
```

> **Hinweis:** Dein Bring!-Konto braucht ein direktes Passwort (nicht nur Google-Login).  
> In der Bring! App: Profil → Konto → Passwort festlegen.

## Verfügbare Tools

| Tool | Beschreibung |
|------|-------------|
| `get_lists` | Alle Einkaufslisten abrufen |
| `get_list_items` | Artikel einer Liste anzeigen |
| `add_item` | Artikel hinzufügen |
| `remove_item` | Artikel entfernen |
| `complete_item` | Als gekauft markieren |
| `add_items_bulk` | Mehrere Artikel auf einmal hinzufügen |

## Beispiele

- *"Zeig mir meine Einkaufsliste"*
- *"Füge Milch und Brot zum Wocheneinkauf hinzu"*
- *"Was steht noch auf der Markt-Liste?"*
- *"Markiere Äpfel als gekauft"*
