# Code Spire - Project Plan

## Project Overview

**Code Spire** is a roguelike deck-building game inspired by Slay the Spire, where players use custom programming language snippets as "cards" to attack enemies and defend against their attacks. The core of the project is a working compiler that processes player-written code during gameplay.

---

## Part 1: Custom Programming Language Specification

### Language Name
**"Codex"** - The programming language of the Spire

### Phase 1: Language Design (Required Elements)

#### Custom Data Types
| Type Name | Description | Example Values |
|-----------|-------------|----------------|
| `bolt` | Numeric/integer type | `42`, `100`, `-5` |
| `scroll` | String/text type | `"hello"`, `"attack"` |
| `flag` | Boolean type | `true`, `false` |

#### Custom Assignment Operator
- Symbol: `~` (tilde)
- Example: `bolt power ~ 10`

#### Custom Statement Delimiter
- Symbol: `.` (period)
- Example: `bolt damage ~ 25.`

#### Custom Output Keyword
- Keyword: `speak`
- Example: `speak "Hello Spire".`

### Extended Language Features (Bonus)

#### Arithmetic Operations
```
bolt x ~ 10 + 5.
bolt y ~ x * 2.
bolt z ~ (10 - 3) / 2.
```

#### Comparison Operators
- `==` equals
- `!=` not equals  
- `>` greater than
- `<` less than
- `>=` greater or equal
- `<=` less or equal

#### Control Structures (Bonus)
- If statements: `TEST condition FAIL ... PASS ... CLOSE.`
- While loops: `REPEAT ... UNTIL condition BREAK.`

---

## Part 2: Game Mechanics Design

### Core Game Loop
```
┌────────────────────────────────────────────┐
│              CODE SPIRE GAME                │
├────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐    ┌──────────┐              │
│  │ PLAYER   │    │  ENEMY   │              │
│  │ HP: 80   │    │ HP: varies│              │
│  │ Energy:10│    │ Intent:  │              │
│  │ Deck: 10 │    │ Attack  │              │
│  └────┬─────┘    │ varies  │              │
│       │         └────┬─────┘              │
│       │              │                     │
│       ▼              ▼                     │
│  ┌────────────────────────────────┐        │
│  │      HAND (5 Code Cards)       │        │
│  │  Draw 5 cards from deck each   │        │
│  │  turn. Used cards go to discard│        │
│  └────────────────────────────────┘        │
│       │         │         │               │
│       └─────────┴─────────┘               │
│                 │                          │
│                 ▼                          │
│         ┌─────────────┐                    │
│         │ COMPILE &   │                    │
│         │ EXECUTE     │                    │
│         └──────┬──────┘                    │
│                │                            │
│                ▼                            │
│         ┌─────────────┐                    │
│         │ BATTLE      │                    │
│         │ RESOLUTION  │                    │
│         └─────────────┘                    │
└────────────────────────────────────────────┘
```

### Deck/Hand Management System

**Starting Deck (10 cards):**
- 3x Quick Strike (1 mana) - Deal 4 damage
- 2x Minor Block (1 mana) - Gain 4 block  
- 2x Standard Strike (2 mana) - Deal 6 damage
- 1x Double Tap (2 mana) - Deal 10 damage
- 1x Standard Shield (2 mana) - Gain 6 block
- 1x Prepare Dialogue (2 mana) - Utility

**Turn Structure:**
1. **Draw Phase:** Draw 5 cards from deck into hand
2. **Play Phase:** Play cards (used cards go to discard pile)
3. **End Turn:** Remaining hand cards go to discard pile, deck reshuffles if needed
4. **Next Turn:** Draw from deck again

### Card Library - Organized by Tier

#### TIER 1 - Starter Cards (Available from start)
| Card Name | Code | Effect | Cost |
|-----------|------|--------|------|
| Quick Strike | `bolt dmg ~ 4.` | Deal 4 damage | 1 |
| Poke | `bolt dmg ~ 3.` | Deal 3 damage | 1 |
| Tap | `bolt dmg ~ 5.` | Deal 5 damage | 1 |
| Minor Block | `bolt def ~ 4.` | Gain 4 block | 1 |
| Guard | `bolt def ~ 5.` | Gain 5 block | 1 |
| Minor Heal | `bolt heal ~ 5.` | Restore 5 HP | 1 |
| Standard Strike | `bolt dmg ~ 6.` | Deal 6 damage | 2 |
| Standard Shield | `bolt def ~ 6.` | Gain 6 block | 2 |
| Double Tap | `bolt dmg ~ 5 + 5.` | Deal 10 damage | 2 |
| Minor Recovery | `bolt heal ~ 8.` | Restore 8 HP | 2 |

#### TIER 2 - Standard Cards (Floor 3+)
| Card Name | Code | Effect | Cost |
|-----------|------|--------|------|
| Heavy Bolt | `bolt dmg ~ 10 + 4.` | Deal 14 damage | 3 |
| Reinforce | `bolt def ~ 10 + 4.` | Gain 14 block | 3 |
| First Aid | `bolt heal ~ 12.` | Restore 12 HP | 3 |
| Loop Jab | `REPEAT true UNTIL bolt dmg ~ 4. BREAK.` | Looped jab (roll 1d3) | 3 |
| Power Strike | `bolt dmg ~ 6 + 4.` | Deal 10 damage | 3 |
| Fortify | `bolt def ~ 8 + 4.` | Gain 12 block | 3 |
| Recovery | `bolt heal ~ 8 + 6.` | Restore 14 HP | 3 |
| Strength Up | `bolt pow ~ 2.` | Gain 2 strength | 2 |
| Power Surge | `bolt pow ~ 3.` | Gain 3 strength | 3 |

#### TIER 3 - Powerful Cards (Floor 6+)
| Card Name | Code | Effect | Cost |
|-----------|------|--------|------|
| Heavy Strike | `bolt dmg ~ 14.` | Deal 14 damage | 4 |
| Iron Wall | `bolt def ~ 14.` | Gain 14 block | 4 |
| Surge | `bolt pow ~ 4.` | Gain 4 strength | 4 |
| Critical Hit | `bolt dmg ~ 8 * 3.` | Deal 24 damage | 4 |
| Loop Flurry | `REPEAT true UNTIL bolt dmg ~ 3. BREAK.` | Looped flurry (roll 1d5) | 4 |
| Mega Strike | `bolt dmg ~ 12 + 12.` | Deal 24 damage | 4 |
| Mega Shield | `bolt def ~ 12 + 12.` | Gain 24 block | 4 |
| Grand Heal | `bolt heal ~ 20.` | Restore 20 HP | 4 |

### Reward System

After clearing each floor, player chooses 1 of 3 random cards from the available pool:
- **Floor 1-2:** Only Tier 1 cards available
- **Floor 3-5:** Tier 1 + Tier 2 cards available
- **Floor 6+:** All tiers available

### Enemy Types

| Enemy | HP (Base) | Attack Pattern | Description |
|-------|-----------|----------------|-------------|
| Minor Glitch | 12 | Light (6-8 dmg) | Weak foe |
| Stray Bug | 16 | Light (6-8 dmg) | Annoying but fragile |
| Loose Pointer | 18 | Medium (8-12 dmg) | Slightly stronger |
| Stack Phantom | 20 | Medium (8-12 dmg) | Haunts deep floors |
| The Compiler | 120+ | Special (15-20 dmg) | Boss on Floor 15 |

### Player Stats
- **Starting HP:** 80
- **Starting Energy:** 10 per turn
- **Hand Size:** 5 cards per turn
- **Max Floors:** 15

---

## Implementation Status

### Completed Features:
- ✅ Custom CODEX language compiler (Lexer, Parser, Semantic Analyzer)
- ✅ Deck/Hand management with proper draw/discard cycling
- ✅ Card library with 25+ cards organized by tier
- ✅ Progressive card unlocking based on floor
- ✅ Card selection rewards after each floor
- ✅ Drag-and-drop card selection in GUI
- ✅ Code editor for customizing card snippets
- ✅ Battle system with enemy AI
- ✅ Dice-based damage rolls based on card cost
- ✅ Loop attacks with random repeat rolls
- ✅ Dialogue/Speak mechanic (2-turn preparation)
- ✅ Strength buff system
- ✅ Block/Defense system with reduction

### UI Features:
- Player stats panel showing HP, Energy, Block, Strength
- Enemy stats panel showing HP and next intent
- Hand display with 5 fanned cards
- Code snippet editor
- Compiler output and battle log
- Deck/Discard pile counters

---

## File Structure
```
STPTRY/
├── code_spire.py          # Main game file (compiler + game + GUI)
├── codex_cheat_sheet.txt # Language reference
├── plans/
│   └── code_spire_plan.md # This file
└── README.md             # Project documentation
```
