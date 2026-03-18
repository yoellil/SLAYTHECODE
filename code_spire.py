import random
import os
import sys
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

import tkinter as tk
from tkinter import scrolledtext

# ============================================================================
# CODEX LANGUAGE COMPILER
# ============================================================================

class TokenType(Enum):
    # Keywords
    DATATYPE = "DATATYPE"
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    
    # Operators and Delimiters
    ASSIGN_OP = "ASSIGN_OP"  # ~
    DELIMITER = "DELIMITER"  # .
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    
    # Literals
    NUMERIC = "NUMERIC"
    STRING = "STRING"
    CHAR = "CHAR"
    BOOLEAN = "BOOLEAN"
    
    # Arithmetic and Comparison
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    GT = "GT"
    LE = "LE"
    GE = "GE"
    
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.messages = []
        
        self.keywords = {
            'bolt', 'scroll', 'flag', 'digit', 'char', 'dialogue', 'speak', 'TEST', 'FAIL', 'PASS',
            'CLOSE', 'REPEAT', 'UNTIL', 'BREAK', 'true', 'false'
        }
        
        # In-game language datatypes. "digit" is treated as an alias for "bolt".
        self.datatypes = {'bolt', 'scroll', 'flag', 'digit', 'char', 'dialogue'}
    
    def error(self, msg: str):
        self.messages.append(f"[LEXER ERROR at line {self.line}] {msg}")
    
    def log(self, msg: str):
        self.messages.append(f"[LEXER] {msg}")
    
    def current_char(self) -> Optional[str]:
        if self.position >= len(self.code):
            return None
        return self.code[self.position]
    
    def peek(self, offset: int = 1) -> Optional[str]:
        pos = self.position + offset
        if pos >= len(self.code):
            return None
        return self.code[pos]
    
    def advance(self):
        if self.position < len(self.code) and self.code[self.position] == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char().isspace():
            self.advance()
    
    def read_string(self) -> str:
        quote_char = self.current_char()
        self.advance()  # Skip opening quote
        value = ""
        while self.current_char() and self.current_char() != quote_char:
            value += self.current_char()
            self.advance()
        if self.current_char() == quote_char:
            self.advance()  # Skip closing quote
        return value
    
    def read_number(self) -> str:
        value = ""
        while self.current_char() and self.current_char().isdigit():
            value += self.current_char()
            self.advance()
        return value
    
    def read_identifier(self) -> str:
        value = ""
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            value += self.current_char()
            self.advance()
        return value
    
    def tokenize(self) -> List[Token]:
        self.messages.append("--- STARTING LEXICAL ANALYSIS ---")
        
        while self.position < len(self.code):
            self.skip_whitespace()
            
            if self.position >= len(self.code):
                break
            
            char = self.current_char()
            line, col = self.line, self.column
            
            # String literals
            if char in '"\'':
                value = self.read_string()
                if char == "'" and len(value) == 1:
                    token = Token(TokenType.CHAR, value, line, col)
                    self.tokens.append(token)
                    self.log(f"Found '{value}' -> Identified as CHAR_LITERAL")
                else:
                    token = Token(TokenType.STRING, value, line, col)
                    self.tokens.append(token)
                    self.log(f"Found '{value}' -> Identified as STRING_LITERAL")
            
            # Numbers
            elif char.isdigit():
                value = self.read_number()
                token = Token(TokenType.NUMERIC, value, line, col)
                self.tokens.append(token)
                self.log(f"Found '{value}' -> Identified as NUMERIC_LITERAL")
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                value = self.read_identifier()
                if value in self.datatypes:
                    token = Token(TokenType.DATATYPE, value, line, col)
                    self.log(f"Found '{value}' -> Identified as DATATYPE")
                elif value in self.keywords:
                    token = Token(TokenType.KEYWORD, value, line, col)
                    self.log(f"Found '{value}' -> Identified as KEYWORD")
                elif value in ('true', 'false'):
                    token = Token(TokenType.BOOLEAN, value, line, col)
                    self.log(f"Found '{value}' -> Identified as BOOLEAN_LITERAL")
                else:
                    token = Token(TokenType.IDENTIFIER, value, line, col)
                    self.log(f"Found '{value}' -> Identified as IDENTIFIER")
                self.tokens.append(token)
            
            # Operators and delimiters
            elif char == '~':
                self.tokens.append(Token(TokenType.ASSIGN_OP, '~', line, col))
                self.log(f"Found '~' -> Identified as ASSIGN_OPERATOR")
                self.advance()
            elif char == '.':
                self.tokens.append(Token(TokenType.DELIMITER, '.', line, col))
                self.log(f"Found '.' -> Identified as DELIMITER")
                self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
                self.advance()
            elif char == '=' and self.peek() == '=':
                self.tokens.append(Token(TokenType.EQ, '==', line, col))
                self.advance()
                self.advance()
            elif char == '!' and self.peek() == '=':
                self.tokens.append(Token(TokenType.NE, '!=', line, col))
                self.advance()
                self.advance()
            elif char == '<' and self.peek() == '=':
                self.tokens.append(Token(TokenType.LE, '<=', line, col))
                self.advance()
                self.advance()
            elif char == '>' and self.peek() == '=':
                self.tokens.append(Token(TokenType.GE, '>=', line, col))
                self.advance()
                self.advance()
            elif char == '<':
                self.tokens.append(Token(TokenType.LT, '<', line, col))
                self.advance()
            elif char == '>':
                self.tokens.append(Token(TokenType.GT, '>', line, col))
                self.advance()
            else:
                self.error(f"Unknown character: '{char}'")
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        
        unknown_count = sum(1 for t in self.tokens if t.type == TokenType.UNKNOWN)
        if unknown_count == 0:
            self.messages.append("✓ Lexical Analysis Complete. 0 Unknown Tokens.")
        else:
            self.messages.append(f"✓ Lexical Analysis Complete. {unknown_count} Unknown Tokens.")
        
        return self.tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.messages = []
    
    def error(self, msg: str):
        self.messages.append(f"[PARSER ERROR] {msg}")
    
    def log(self, msg: str):
        self.messages.append(f"[PARSER] {msg}")
    
    def current_token(self) -> Token:
        if self.position >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.position]
    
    def peek(self, offset: int = 1) -> Token:
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]
    
    def advance(self):
        self.position += 1
    
    def expect(self, token_type: TokenType) -> bool:
        if self.current_token().type == token_type:
            self.advance()
            return True
        return False
    
    def parse_primary(self) -> Dict[str, Any]:
        token = self.current_token()
        
        if token.type == TokenType.NUMERIC:
            self.advance()
            return {'type': 'LITERAL', 'value_type': 'bolt', 'value': int(token.value)}
        
        elif token.type == TokenType.CHAR:
            self.advance()
            return {'type': 'LITERAL', 'value_type': 'char', 'value': token.value}

        elif token.type == TokenType.STRING:
            self.advance()
            return {'type': 'LITERAL', 'value_type': 'scroll', 'value': token.value}
        
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return {'type': 'LITERAL', 'value_type': 'flag', 'value': token.value == 'true'}
        
        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            return {'type': 'IDENTIFIER', 'name': name}
        
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            if self.current_token().type == TokenType.RPAREN:
                self.advance()
            return expr
        
        elif token.type == TokenType.MINUS:
            self.advance()
            operand = self.parse_primary()
            return {'type': 'UNARY_OP', 'op': '-', 'operand': operand}
        
        return {'type': 'ERROR', 'msg': f'Unexpected token: {token.value}'}
    
    def parse_multiplicative(self) -> Dict[str, Any]:
        left = self.parse_primary()
        
        while self.current_token().type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op_token = self.current_token()
            self.advance()
            right = self.parse_primary()
            left = {'type': 'BINARY_OP', 'op': op_token.value, 'left': left, 'right': right}
        
        return left
    
    def parse_additive(self) -> Dict[str, Any]:
        left = self.parse_multiplicative()
        
        while self.current_token().type in (TokenType.PLUS, TokenType.MINUS):
            op_token = self.current_token()
            self.advance()
            right = self.parse_multiplicative()
            left = {'type': 'BINARY_OP', 'op': op_token.value, 'left': left, 'right': right}
        
        return left
    
    def parse_comparison(self) -> Dict[str, Any]:
        left = self.parse_additive()
        
        while self.current_token().type in (TokenType.EQ, TokenType.NE, TokenType.LT, 
                                             TokenType.GT, TokenType.LE, TokenType.GE):
            op_token = self.current_token()
            self.advance()
            right = self.parse_additive()
            left = {'type': 'BINARY_OP', 'op': op_token.value, 'left': left, 'right': right}
        
        return left
    
    def parse_expression(self) -> Dict[str, Any]:
        return self.parse_comparison()
    
    def parse_assignment(self) -> Dict[str, Any]:
        token = self.current_token()
        
        if token.type == TokenType.DATATYPE:
            datatype = token.value
            self.advance()
            
            id_token = self.current_token()
            if id_token.type != TokenType.IDENTIFIER:
                self.error(f"Expected identifier after type, got {id_token.value}")
                return {'type': 'ERROR'}
            
            identifier = id_token.value
            self.advance()
            
            if self.current_token().type != TokenType.ASSIGN_OP:
                self.error(f"Expected assignment operator ~, got {self.current_token().value}")
                return {'type': 'ERROR'}
            self.advance()
            
            expr = self.parse_expression()
            
            if self.current_token().type != TokenType.DELIMITER:
                self.error(f"Expected delimiter ., got {self.current_token().value}")
                return {'type': 'ERROR'}
            self.advance()
            
            return {
                'type': 'ASSIGNMENT',
                'var_type': datatype,
                'var_name': identifier,
                'value': expr,
                'line': token.line
            }
        
        return {'type': 'ERROR', 'msg': 'Expected type declaration'}
    
    def parse_speak(self) -> Dict[str, Any]:
        token = self.current_token()
        if token.value != 'speak':
            return None
        
        self.advance()
        expr = self.parse_expression()
        
        if self.current_token().type != TokenType.DELIMITER:
            self.error("Expected delimiter . after speak statement")
            return {'type': 'ERROR'}
        self.advance()
        
        return {'type': 'SPEAK', 'value': expr}
    
    def parse_test(self) -> Dict[str, Any]:
        if self.current_token().value != 'TEST':
            return None
        
        self.advance()
        condition = self.parse_expression()
        
        if self.current_token().value != 'FAIL':
            self.error("Expected FAIL after condition in TEST")
            return {'type': 'ERROR'}
        self.advance()
        
        fail_stmt = self.parse_statement()
        
        if self.current_token().value != 'PASS':
            self.error("Expected PASS in TEST statement")
            return {'type': 'ERROR'}
        self.advance()
        
        pass_stmt = self.parse_statement()
        
        if self.current_token().value != 'CLOSE':
            self.error("Expected CLOSE to end TEST statement")
            return {'type': 'ERROR'}
        self.advance()
        
        if self.current_token().type == TokenType.DELIMITER:
            self.advance()
        
        return {
            'type': 'TEST',
            'condition': condition,
            'fail_branch': fail_stmt,
            'pass_branch': pass_stmt
        }
    
    def parse_repeat(self) -> Dict[str, Any]:
        if self.current_token().value != 'REPEAT':
            return None
        
        self.advance()
        condition = self.parse_expression()
        
        if self.current_token().value != 'UNTIL':
            self.error("Expected UNTIL in REPEAT loop")
            return {'type': 'ERROR'}
        self.advance()
        
        body = self.parse_statement()
        
        if self.current_token().value != 'BREAK':
            self.error("Expected BREAK to end REPEAT loop")
            return {'type': 'ERROR'}
        self.advance()
        
        if self.current_token().type == TokenType.DELIMITER:
            self.advance()
        
        return {
            'type': 'REPEAT',
            'condition': condition,
            'body': body
        }
    
    def parse_statement(self) -> Dict[str, Any]:
        token = self.current_token()
        
        if token.type == TokenType.DATATYPE:
            return self.parse_assignment()
        elif token.value == 'speak':
            return self.parse_speak()
        elif token.value == 'TEST':
            return self.parse_test()
        elif token.value == 'REPEAT':
            return self.parse_repeat()
        else:
            self.error(f"Unexpected token at start of statement: {token.value}")
            return {'type': 'ERROR'}
    
    def parse(self) -> List[Dict[str, Any]]:
        self.messages.append("--- STARTING SYNTAX ANALYSIS ---")
        self.log("Checking statement structure...")
        self.log("Expected rule: [DATATYPE] [ID] [ASSIGN] [LITERAL] [DELIM]")
        
        statements = []
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt['type'] != 'ERROR':
                statements.append(stmt)
            else:
                break
        
        if len(self.messages) == 3:
            # Only header and expectations, so structure matched cleanly.
            self.log("Actual structure matches expected rule perfectly.")
            self.messages.append("✓ Syntax Analysis Complete. No structural errors.")
        else:
            self.messages.append("✓ Syntax Analysis Complete.")
        return statements

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.messages = []
        self.errors = []
    
    def error(self, msg: str):
        self.errors.append(msg)
        self.messages.append(f"[SEMANTICS] FATAL ERROR: {msg}")
    
    def log(self, msg: str):
        self.messages.append(f"[SEMANTICS] {msg}")
    
    def check_type_compatibility(self, var_type: str, value: Dict[str, Any]) -> bool:
        value_type = self.infer_type(value)
        # Treat "digit" as numeric alias for "bolt"
        if var_type in ('bolt', 'digit') and value_type in ('bolt', None):
            return True
        elif var_type == 'scroll' and value_type in ('scroll', None):
            return True
        elif var_type == 'dialogue' and value_type in ('scroll', None):
            # Dialogue stores text, but is treated as a distinct beginner-facing type.
            return True
        elif var_type == 'char' and value_type in ('char', None):
            return True
        elif var_type == 'flag' and value_type in ('flag', None):
            return True
        
        return False
    
    def infer_type(self, expr: Dict[str, Any]) -> Optional[str]:
        if expr['type'] == 'LITERAL':
            return expr['value_type']
        elif expr['type'] == 'IDENTIFIER':
            if expr['name'] in self.symbol_table:
                return self.symbol_table[expr['name']]['type']
            return None
        elif expr['type'] == 'BINARY_OP':
            if expr['op'] in ('+', '-', '*', '/'):
                return 'bolt'
            else:
                return 'flag'
        elif expr['type'] == 'UNARY_OP':
            return self.infer_type(expr['operand'])
        
        return None
    
    def analyze(self, ast: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], List[str]]:
        self.messages.append("--- STARTING SEMANTIC ANALYSIS ---")
        self.log("Checking Type Compatibility...")
        
        for stmt in ast:
            if stmt['type'] == 'ASSIGNMENT':
                var_name = stmt['var_name']
                var_type = stmt['var_type']
                value = stmt['value']
                
                if self.check_type_compatibility(var_type, value):
                    value_literal = self.infer_type(value)
                    value_type_str = "Numeric" if value_literal == 'bolt' else ("String" if value_literal == 'scroll' else "Boolean")
                    
                    self.log(f"Variable '{var_name}' is declared as '{var_type}'. Value is '{self.value_to_str(value)}' ({value_type_str}).")
                    self.log("Types match. No coercion needed.")
                    
                    self.symbol_table[var_name] = {
                        'type': var_type,
                        'value': value,
                        'line': stmt['line']
                    }
                    self.log(f"Binding variable '{var_name}' to Symbol Table.")
                else:
                    value_literal = self.infer_type(value)
                    value_str = self.value_to_str(value)
                    self.error(f"Variable '{var_name}' is declared as '{var_type}', but value '{value_str}' is a {self.type_name(value_literal)}.")
                    self.messages.append("[SEMANTICS] Recovery Strategy: Compiler will discard assignment to prevent memory corruption.")
        
        self.messages.append("✓ Semantic Analysis Complete.")
        return self.symbol_table, self.errors
    
    def value_to_str(self, expr: Dict[str, Any]) -> str:
        if expr['type'] == 'LITERAL':
            if expr['value_type'] == 'scroll':
                return f'"{expr["value"]}"'
            return str(expr['value'])
        elif expr['type'] == 'IDENTIFIER':
            return expr['name']
        return str(expr)
    
    def type_name(self, t: str) -> str:
        if t == 'bolt':
            return 'NUMERIC'
        elif t == 'scroll':
            return 'STRING'
        elif t == 'dialogue':
            return 'DIALOGUE'
        elif t == 'char':
            return 'CHAR'
        elif t == 'flag':
            return 'BOOLEAN'
        return 'UNKNOWN'

class CodexCompiler:
    def __init__(self, code: str):
        self.code = code
        self.lexer = Lexer(code)
        self.parser = None
        self.analyzer = None
        self.symbol_table = {}
        self.all_messages = []
    
    def compile(self) -> Tuple[Optional[Dict], List[str]]:
        # Lexical Analysis
        tokens = self.lexer.tokenize()
        self.all_messages.extend(self.lexer.messages)
        
        # Syntax Analysis
        self.parser = Parser(tokens)
        ast = self.parser.parse()
        self.all_messages.extend(self.parser.messages)
        
        # Semantic Analysis
        self.analyzer = SemanticAnalyzer()
        self.symbol_table, errors = self.analyzer.analyze(ast)
        self.all_messages.extend(self.analyzer.messages)
        
        if errors:
            return None, errors
        
        return {'ast': ast, 'symbol_table': self.symbol_table}, []
    
    def get_output(self) -> str:
        return "\n".join(self.all_messages)
    
    def evaluate_expression(self, expr: Dict[str, Any]) -> Any:
        if expr['type'] == 'LITERAL':
            return expr['value']
        
        elif expr['type'] == 'IDENTIFIER':
            name = expr['name']
            if name in self.symbol_table:
                return self.evaluate_expression(self.symbol_table[name]['value'])
            return 0
        
        elif expr['type'] == 'BINARY_OP':
            left = self.evaluate_expression(expr['left'])
            right = self.evaluate_expression(expr['right'])
            op = expr['op']
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return int(left / right) if right != 0 else 0
            elif op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '<':
                return left < right
            elif op == '>':
                return left > right
            elif op == '<=':
                return left <= right
            elif op == '>=':
                return left >= right
        
        elif expr['type'] == 'UNARY_OP':
            operand = self.evaluate_expression(expr['operand'])
            if expr['op'] == '-':
                return -operand
        
        return 0

# ============================================================================
# GAME ENGINE
# ============================================================================

class CardEffect(Enum):
    DAMAGE = "damage"
    BLOCK = "block"
    HEAL = "heal"
    STRENGTH = "strength"
    VULNERABLE = "vulnerable"
    MESSAGE = "message"
    CONDITIONAL = "conditional"
    LOOP = "loop"

@dataclass
class Card:
    name: str
    code: str
    energy_cost: int
    description: str
    card_type: str = "attack"

@dataclass
class CardInstance(Card):
    id: int = field(default_factory=lambda: random.randint(1000, 9999))

class Enemy:
    def __init__(self, name: str, max_hp: int, attack_pattern: str, special: str = ""):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack_pattern = attack_pattern
        self.special = special
        self.is_alive = True
    
    def take_damage(self, damage: int) -> int:
        actual_damage = max(0, damage)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
        return actual_damage
    
    def get_intent(self) -> Dict[str, int]:
        if self.attack_pattern == "light":
            return {'damage': random.randint(6, 8)}
        elif self.attack_pattern == "medium":
            return {'damage': random.randint(8, 12)}
        elif self.attack_pattern == "heavy":
            return {'damage': random.randint(12, 16)}
        elif self.attack_pattern == "special":
            return {'damage': random.randint(15, 20)}
        return {'damage': 5}

class Player:
    def __init__(self, name: str = "Player", max_hp: int = 80):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        # Mana pool per turn (starts low-ish, can be buffed)
        self.max_energy = 10
        self.energy = self.max_energy
        self.deck = []
        self.hand = []
        self.discard_pile = []
        self.strength = 0
        self.block = 0
        self.relics = []
        self.turn_count = 0
        # Persistent buffs gained between floors
        self.damage_bonus = 0
        self.block_bonus = 0
        self.mana_bonus = 0
        # Persistent memory across turns (simple global bindings)
        self.memory: Dict[str, Dict[str, Any]] = {}
        # 2-turn dialogue mechanic: prepare dialogue one turn, use next turn via speak(myText)
        self.prepared_dialogue_name: Optional[str] = None
        self.prepared_dialogue_turn: Optional[int] = None
    
    def take_damage(self, damage: int) -> int:
        mitigated = max(0, damage - self.block)
        self.hp -= mitigated
        self.block = 0
        return mitigated
    
    def gain_block(self, amount: int):
        self.block += amount
    
    def reset_turn(self):
        # Base mana plus any permanent mana bonus
        self.energy = self.max_energy + self.mana_bonus
        for relic in self.relics:
            if relic['name'] == 'Keyboard':
                self.energy += 1
        # Strength buffs only last for a single player turn.
        self.strength = 0
        self.block = 0
        self.turn_count += 1
        
        # Draw cards
        draw_count = 5
        for relic in self.relics:
            if relic['name'] == 'Coffee Cup':
                draw_count += 1
        
        self.draw_cards(draw_count)

        # If dialogue was prepared last turn, inject a temporary Speak card into the hand.
        # Keep hand size at 5 by returning the last drawn card to the deck.
        if (
            self.prepared_dialogue_name
            and self.prepared_dialogue_turn is not None
            and self.turn_count == self.prepared_dialogue_turn + 1
        ):
            speak_code = f"speak ({self.prepared_dialogue_name})."
            speak_card = CardInstance("Speak Dialogue", speak_code, 2, "Use prepared dialogue from last turn", "utility")
            if len(self.hand) >= 5:
                returned = self.hand.pop()  # keep hand at 5
                self.deck.append(returned)
                random.shuffle(self.deck)
            self.hand.insert(0, speak_card)
    
    def draw_cards(self, count: int):
        for _ in range(count):
            if len(self.deck) == 0:
                # Reshuffle discard into deck
                if len(self.discard_pile) > 0:
                    self.deck = self.discard_pile[:]
                    self.discard_pile = []
                    random.shuffle(self.deck)
                else:
                    break
            
            if len(self.deck) > 0:
                card = self.deck.pop()
                self.hand.append(card)
    
    def play_card(self, card_index: int) -> Optional[CardInstance]:
        if 0 <= card_index < len(self.hand):
            card = self.hand.pop(card_index)
            return card
        return None
    
    def is_alive(self) -> bool:
        return self.hp > 0

class Battle:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.log = []
    
    def log_action(self, msg: str):
        self.log.append(msg)
    
    def execute_card(self, card: CardInstance) -> Dict[str, int]:
        compiler = CodexCompiler(card.code)
        result, errors = compiler.compile()
        
        output = {
            'damage': 0,
            'block': 0,
            'heal': 0,
            'strength': 0
        }
        
        if errors:
            # Compilation failed; no combat effect.
            return output
        
        # Merge this snippet's symbol table into persistent memory.
        symbol_table = result['symbol_table']
        merged_memory = dict(self.player.memory)
        merged_memory.update(symbol_table)
        self.player.memory = merged_memory

        # Allow expression evaluation to resolve identifiers from persistent memory.
        compiler.symbol_table = merged_memory
        ast = result['ast']
        
        # Extract values from compiled code
        if 'dmg' in symbol_table:
            damage_val = compiler.evaluate_expression(symbol_table['dmg']['value'])
            output['damage'] = int(damage_val)
        
        if 'damage' in symbol_table:
            damage_val = compiler.evaluate_expression(symbol_table['damage']['value'])
            output['damage'] = int(damage_val)
        
        if 'def' in symbol_table:
            block_val = compiler.evaluate_expression(symbol_table['def']['value'])
            # Only a portion of the declared defense becomes real block:
            # about 33% of the coded value (e.g., 6 -> 2).
            reduced_block = int(block_val * 0.33)
            self.log_action(f"Raw defense value: {block_val} -> effective block: {reduced_block}")
            output['block'] = reduced_block
        
        if 'heal' in symbol_table:
            heal_val = compiler.evaluate_expression(symbol_table['heal']['value'])
            output['heal'] = int(heal_val)
        
        if 'pow' in symbol_table:
            strength_val = compiler.evaluate_expression(symbol_table['pow']['value'])
            output['strength'] = int(strength_val)

        # Dialogue prep: if user binds a dialogue variable, mark it as "prepared" this turn.
        for name, info in symbol_table.items():
            if info.get("type") == "dialogue":
                self.player.prepared_dialogue_name = name
                self.player.prepared_dialogue_turn = self.player.turn_count
                self.log_action(f"Dialogue prepared in memory as '{name}'. Use speak({name}) next turn.")

        # Apply permanent buffs from rewards
        if output['damage'] > 0 and self.player.damage_bonus:
            output['damage'] += self.player.damage_bonus
        if output['block'] > 0 and self.player.block_bonus:
            output['block'] += self.player.block_bonus

        # Convert damage into a dice-based roll depending on how "strong" the card is.
        # We use the card's mana cost to decide the dice:
        # - Cost 2  -> 1d6
        # - Cost 3  -> 2d8
        # - Cost 4+ -> 4d12
        if output['damage'] > 0:
            if card.energy_cost <= 2:
                dice_count, dice_sides = 1, 6
            elif card.energy_cost == 3:
                dice_count, dice_sides = 2, 8
            else:
                dice_count, dice_sides = 4, 12

            rolls = [random.randint(1, dice_sides) for _ in range(dice_count)]
            rolled_damage = sum(rolls)
            self.log_action(
                f"Damage roll: {dice_count}d{dice_sides} -> rolls {rolls} = {rolled_damage}"
            )

            # Temporary strength buff: 50% of current strength as flat bonus.
            strength_bonus = int(self.player.strength * 0.5) if self.player.strength > 0 else 0
            if strength_bonus > 0:
                self.log_action(f"Strength bonus: +{strength_bonus} damage (from {self.player.strength} strength)")
            output['damage'] = rolled_damage + strength_bonus

        # Loop attacks: if the snippet contains a REPEAT statement, roll how many times the attack triggers.
        # Low-level loop cards roll 1d3, higher-level loop cards roll 1d5.
        has_repeat = any(isinstance(stmt, dict) and stmt.get("type") == "REPEAT" for stmt in ast)
        if has_repeat and output["damage"] > 0:
            sides = 3 if card.energy_cost <= 3 else 5
            loop_roll = random.randint(1, sides)
            self.log_action(f"Loop roll: 1d{sides} -> {loop_roll} time(s)")
            output["damage"] *= loop_roll
        
        # Check for persuasive "speak" statements that try to end the battle peacefully.
        speak_text = None
        speak_is_identifier = False
        speak_identifier_name = None
        for stmt in ast:
            if isinstance(stmt, dict) and stmt.get('type') == 'SPEAK':
                # Detect if speak is referencing an identifier (for the 2-turn dialogue mechanic).
                if isinstance(stmt.get("value"), dict) and stmt["value"].get("type") == "IDENTIFIER":
                    speak_is_identifier = True
                    speak_identifier_name = stmt["value"].get("name")
                    speak_text = compiler.evaluate_expression(stmt['value'])
                else:
                    speak_text = compiler.evaluate_expression(stmt['value'])
                break
        
        if speak_text is not None and self.enemy.is_alive:
            # If speak uses an identifier, require it to be a prepared dialogue from the previous turn.
            if speak_is_identifier:
                if (
                    speak_identifier_name is None
                    or self.player.prepared_dialogue_name != speak_identifier_name
                    or self.player.prepared_dialogue_turn is None
                    or self.player.turn_count != self.player.prepared_dialogue_turn + 1
                ):
                    self.log_action("Speak failed: no prepared dialogue from last turn.")
                    return output
                # Consume prepared dialogue after use
                self.player.prepared_dialogue_name = None
                self.player.prepared_dialogue_turn = None

            # Persuasion check: roll a d20.
            # Speak tiers:
            # - 2 mana speak: succeeds on 18+
            # - 4 mana speak: succeeds on 15+
            self.log_action(f'You said: "{speak_text}"')
            roll = random.randint(1, 20)
            threshold = 15 if card.energy_cost >= 4 else 18
            self.log_action(f"Persuasion check: d20 roll = {roll} (need {threshold}+)")
            if roll >= threshold:
                self.enemy.is_alive = False
                self.enemy.hp = 0
                self.log_action("Result: SUCCESS. The enemy leaves the battle peacefully.")
            else:
                self.log_action("Result: FAIL. The enemy is unmoved by your words.")
        
        # Apply relics
        for relic in self.player.relics:
            if relic['name'] == 'Bug Spray' and not relic['used']:
                if self.player.turn_count == 1:
                    output['damage'] *= 2
                    relic['used'] = True
        
        return output
    
    def player_turn(self, cards_to_play: List[int]):
        self.log_action(f"\n=== PLAYER TURN {self.player.turn_count} ===")
        self.log_action(f"Energy: {self.player.energy} | Hand: {len(self.player.hand)} cards")
        
        total_damage = 0
        total_block = 0
        total_heal = 0
        
        for card_idx in sorted(cards_to_play, reverse=True):
            if card_idx >= len(self.player.hand):
                continue
            
            card = self.player.play_card(card_idx)
            if not card:
                continue
            
            if card.energy_cost > self.player.energy:
                self.log_action(f"{card.name} - Not enough energy!")
                self.player.hand.append(card)
                continue
            
            self.player.energy -= card.energy_cost
            self.log_action(f"Playing: {card.name}")
            
            result = self.execute_card(card)
            total_damage += result['damage']
            total_block += result['block']
            total_heal += result['heal']
            
            if result['strength'] > 0:
                self.player.strength += result['strength']
                self.log_action(f"  +{result['strength']} Strength")
            
            if result['damage'] > 0:
                self.log_action(f"  Damage: {result['damage']}")
            
            self.player.discard_pile.append(card)
        
        if total_damage > 0:
            actual_damage = self.enemy.take_damage(total_damage)
            self.log_action(f"Total Damage: {actual_damage}")
        
        if total_block > 0:
            self.player.gain_block(total_block)
            self.log_action(f"Total Block: {total_block}")
        
        if total_heal > 0:
            self.player.hp = min(self.player.max_hp, self.player.hp + total_heal)
            self.log_action(f"Total Heal: {total_heal}")
    
    def enemy_turn(self):
        self.log_action(f"\n=== ENEMY TURN ===")
        intent = self.enemy.get_intent()
        damage = intent['damage']
        
        self.log_action(f"{self.enemy.name} attacks for {damage} damage!")
        actual_damage = self.player.take_damage(damage)
        
        if self.player.block > 0:
            self.log_action(f"{self.player.block} damage blocked")
    
    def execute_round(self, player_cards: List[int]):
        self.player_turn(player_cards)
        
        if not self.enemy.is_alive:
            self.log_action(f"\nVictory! {self.enemy.name} defeated!")
            return True
        
        self.enemy_turn()
        
        if not self.player.is_alive():
            self.log_action(f"\nDefeat! You were defeated!")
            return False
        
        return None  # Battle continues
    
    def get_log(self) -> str:
        return "\n".join(self.log)

class Game:
    def __init__(self):
        self.player = Player()
        self.current_floor = 1
        self.max_floor = 15
        self.enemy_templates = self.generate_enemy_templates()
        self.setup_starting_deck()
        self.battle = None
        self.enemies_remaining_on_floor = random.randint(1, 3)
    
    def setup_starting_deck(self):
        # Start with a simple "snippet" deck (attacks, defense, and a speak attempt).
        starter_cards = [
            CardInstance("Snippet Strike", "bolt dmg ~ 6.", 2, "Deal 6 damage", "attack"),
            CardInstance("Snippet Strike", "bolt dmg ~ 6.", 2, "Deal 6 damage", "attack"),
            CardInstance("Snippet Strike", "bolt dmg ~ 6.", 2, "Deal 6 damage", "attack"),
            CardInstance("Snippet Shield", "bolt def ~ 6.", 2, "Gain 6 block", "defense"),
            CardInstance("Prepare Dialogue", 'dialogue myText ~ "your own text here".', 2, "Prepare dialogue (enables Speak next turn)", "utility"),
        ]
        
        self.player.deck = starter_cards[:]
        random.shuffle(self.player.deck)
    
    def generate_enemy_templates(self) -> List[Tuple[str, int, str, str]]:
        # Base enemy templates: name, base_hp, pattern, description.
        return [
            ("Minor Glitch", 12, "light", "Weak foe"),
            ("Stray Bug", 16, "light", "Annoying but fragile"),
            ("Loose Pointer", 18, "medium", "Slightly stronger"),
            ("Stack Phantom", 20, "medium", "Haunts deep floors"),
        ]
    
    def get_next_enemy(self) -> Enemy:
        # Scale enemy HP and difficulty by floor so higher floors are tougher.
        if self.current_floor >= self.max_floor and self.enemies_remaining_on_floor <= 0:
            base_hp = 120
            scaled_hp = base_hp + (self.current_floor - 1) * 6
            return Enemy("The Compiler", scaled_hp, "special", "Boss - Has multiple phases")

        template = random.choice(self.enemy_templates)
        name, base_hp, pattern, desc = template
        # Each floor adds a bit more HP
        scaled_hp = base_hp + (self.current_floor - 1) * 4
        return Enemy(name, scaled_hp, pattern, desc)
    
    def start_battle(self) -> Battle:
        # Start a fresh battle; player always begins at full mana and HP for each fight.
        self.player.hp = self.player.max_hp
        self.player.reset_turn()
        enemy = self.get_next_enemy()
        self.battle = Battle(self.player, enemy)
        return self.battle

# ============================================================================
# CARD LIBRARY
# ============================================================================

CARD_LIBRARY = [
    # Cheaper options (but still cost at least 2 mana)
    CardInstance("Bolt Strike", "bolt dmg ~ 6.", 2, "Deal 6 damage", "attack"),
    CardInstance("Guard", "bolt def ~ 6.", 2, "Gain 6 block", "defense"),

    # Medium-cost, stronger effects
    CardInstance("Heavy Bolt", "bolt dmg ~ 10 + 4.", 3, "Deal 14 damage", "attack"),
    CardInstance("Reinforce", "bolt def ~ 10 + 4.", 3, "Gain 14 block", "defense"),
    CardInstance("First Aid", "bolt heal ~ 12.", 3, "Restore 12 HP", "power"),
    CardInstance("Loop Jab", "REPEAT true UNTIL bolt dmg ~ 4. BREAK.", 3, "Looped jab (roll 1d3 repeats)", "attack"),

    # Expensive, powerful options
    CardInstance("Critical Hit", "bolt dmg ~ 8 * 3.", 4, "Deal 24 damage", "attack"),
    CardInstance("Iron Wall", "bolt def ~ 10 * 2.", 4, "Gain 20 block", "defense"),
    CardInstance("Surge", "bolt pow ~ 4.", 4, "Gain 4 strength", "power"),
    CardInstance("Loop Flurry", "REPEAT true UNTIL bolt dmg ~ 3. BREAK.", 4, "Looped flurry (roll 1d5 repeats)", "attack"),

    # Two-turn dialogue -> speak mechanic (Speak card is injected into hand only after prepare)
    CardInstance("Prepare Dialogue", 'dialogue myText ~ "your own text here".', 2, "Prepare dialogue (enables Speak next turn)", "utility"),
]

# ============================================================================
# MAIN GAME LOOP
# ============================================================================

def display_game_state(game: Game, battle: Optional[Battle] = None):
    print("\n" + "=" * 60)
    print(f"FLOOR {game.current_floor}/{game.max_floor}")
    print("=" * 60)
    
    if battle:
        print("\nPLAYER")
        print(f"   HP: {battle.player.hp}/{battle.player.max_hp}")
        print(f"   Energy: {battle.player.energy}/{battle.player.max_energy}")
        print(f"   Block: {battle.player.block}")
        print(f"   Strength: {battle.player.strength}")
        
        print(f"\nENEMY: {battle.enemy.name}")
        print(f"   HP: {battle.enemy.hp}/{battle.enemy.max_hp}")
        
        print(f"\nHAND ({len(battle.player.hand)} cards):")
        for i, card in enumerate(battle.player.hand):
            print(f"   [{i}] {card.name} (Cost: {card.energy_cost})")


# ============================================================================
# TKINTER GUI: OLD-SCHOOL DND TERMINAL + TURN-BASED DECK PLAY
# ============================================================================


def format_symbol_table(symbol_table: Dict[str, Any]) -> str:
    if not symbol_table:
        return "(symbol table empty)"

    def normalize_lang_type(t: str) -> str:
        # Show the language's own type names in the table (bolt/scroll/flag).
        # "digit" is an alias of bolt.
        if t == "digit":
            return "bolt"
        return str(t)

    def type_width_bytes(lang_type: str) -> int:
        # Memory widths (bytes) by language datatype.
        # bolt/digit behave like ints, scroll like chars, flag like bool.
        if lang_type == "bolt":
            return 4
        if lang_type == "scroll":
            return 1
        if lang_type == "dialogue":
            return 1
        if lang_type == "char":
            return 1
        if lang_type == "flag":
            return 1
        return 4

    # No explicit scoping in CODEX right now, so everything is level 0.
    level = 0
    offset = 0
    rows: List[Tuple[str, str, int, int, int]] = []
    for name, info in symbol_table.items():
        lang_type = normalize_lang_type(info.get("type", "?"))
        width = type_width_bytes(lang_type)
        rows.append((name, lang_type, level, width, offset))
        offset += width

    lines = []
    lines.append("GENERATING SYMBOL TABLE...")
    lines.append("")
    lines.append(f"{'NAME':<14}{'TYPE':<8}{'LVL':<6}{'WIDTH':<8}{'OFFSET':<8}")
    lines.append("-" * 44)
    for name, t, lvl, width, off in rows:
        lines.append(f"{name:<14}{t:<8}{lvl:<6}{width:<8}{off:<8}")
    lines.append("-" * 44)
    lines.append(f"Total Global Memory Required (Level {level}): {offset} Bytes")
    return "\n".join(lines)


class CodeSpireGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CODE SPIRE - Snippet Spire")
        self.root.geometry("1200x800")

        self.game = Game()
        self.battle = self.game.start_battle()

        self.selected_card_index: Optional[int] = None
        self.dragging_idx: Optional[int] = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.card_home_positions: Dict[int, Tuple[int, int]] = {}
        self.drag_ghost: Optional[tk.Toplevel] = None
        self.drag_ghost_running = False

        # Layout: top frame = battlefield, then hand bar, then bottom frame = code + compiler output
        self.top_frame = tk.Frame(self.root, bg="#201a16", height=260)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.hand_frame = tk.Frame(self.root, bg="#181818", height=190)
        self.hand_frame.pack(side=tk.TOP, fill=tk.X, expand=False)

        self.bottom_frame = tk.Frame(self.root, bg="#120f0b")
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Top-left: player info
        self.player_frame = tk.Frame(self.top_frame, bg="#2c2420", bd=2, relief=tk.GROOVE)
        self.player_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.player_label = tk.Label(self.player_frame, text="PLAYER", font=("Courier New", 18, "bold"), fg="#f0d090", bg="#2c2420")
        self.player_label.pack(anchor="nw", padx=6, pady=4)

        self.player_stats = tk.Label(self.player_frame, text="", font=("Courier New", 12), fg="#f8f8f8", bg="#2c2420", justify=tk.LEFT)
        self.player_stats.pack(anchor="nw", padx=6, pady=4)

        # Top-right: enemy and floor info
        self.enemy_frame = tk.Frame(self.top_frame, bg="#241c26", bd=2, relief=tk.GROOVE)
        self.enemy_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.floor_label = tk.Label(self.enemy_frame, text="", font=("Courier New", 14, "bold"), fg="#c0b0ff", bg="#241c26")
        self.floor_label.pack(anchor="ne", padx=6, pady=4)

        self.enemy_label = tk.Label(self.enemy_frame, text="", font=("Courier New", 16, "bold"), fg="#ffb0b0", bg="#241c26")
        self.enemy_label.pack(anchor="nw", padx=6, pady=4)

        self.enemy_stats = tk.Label(self.enemy_frame, text="", font=("Courier New", 12), fg="#f8f8f8", bg="#241c26", justify=tk.LEFT)
        self.enemy_stats.pack(anchor="nw", padx=6, pady=4)
        # Click enemy panel to "play" the selected card (simple drag-to-enemy feel).
        self.enemy_frame.bind("<Button-1>", lambda e: self.play_selected_card())
        self.enemy_label.bind("<Button-1>", lambda e: self.play_selected_card())
        self.enemy_stats.bind("<Button-1>", lambda e: self.play_selected_card())

        # Hand display (interactive cards)
        self.hand_label = tk.Label(
            self.hand_frame,
            text="SNIPPET HAND (5 PER TURN) - drag a card onto the enemy",
            font=("Courier New", 12, "bold"),
            fg="#e0e0e0",
            bg="#181818",
        )
        self.hand_label.pack(anchor="w", padx=6, pady=2)

        self.hand_canvas = tk.Canvas(self.hand_frame, height=145, bg="#181818", highlightthickness=0)
        self.hand_canvas.pack(fill=tk.X, padx=6, pady=(0, 6))
        self.hand_canvas.bind("<ButtonPress-1>", self.on_hand_press)
        self.hand_canvas.bind("<B1-Motion>", self.on_hand_drag)
        self.hand_canvas.bind("<ButtonRelease-1>", self.on_hand_release)
        # Ensure release works even when the mouse leaves the canvas while dragging.
        self.root.bind("<ButtonRelease-1>", self._on_global_release)

        # Bottom-left: code editor
        self.code_frame = tk.Frame(self.bottom_frame, bg="#1a1410", bd=2, relief=tk.GROOVE)
        self.code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.code_label = tk.Label(self.code_frame, text="CODE SNIPPET (edit, then Play Card)", font=("Courier New", 12, "bold"), fg="#f0d090", bg="#1a1410")
        self.code_label.pack(anchor="nw", padx=4, pady=2)

        # Smaller editor so the hand feels like a real "deck" area.
        self.code_text = scrolledtext.ScrolledText(self.code_frame, height=6, font=("Courier New", 11), bg="#120c08", fg="#f8f8f8", insertbackground="#f8f8f8")
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Controls under code
        self.control_frame = tk.Frame(self.code_frame, bg="#1a1410")
        self.control_frame.pack(fill=tk.X, padx=4, pady=4)

        self.play_button = tk.Button(self.control_frame, text="Play Selected Card", command=self.play_selected_card, bg="#403020", fg="#f8f8f8")
        self.play_button.pack(side=tk.LEFT, padx=4)

        self.end_turn_button = tk.Button(self.control_frame, text="End Turn", command=self.end_turn, bg="#303840", fg="#f8f8f8")
        self.end_turn_button.pack(side=tk.LEFT, padx=4)

        # Bottom-right: compiler output + symbol table + battle log
        self.output_frame = tk.Frame(self.bottom_frame, bg="#101622", bd=2, relief=tk.GROOVE, width=400)
        self.output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=8, pady=8)

        self.output_label = tk.Label(self.output_frame, text="COMPILER + BATTLE LOG", font=("Courier New", 12, "bold"), fg="#b0c8ff", bg="#101622")
        self.output_label.pack(anchor="nw", padx=4, pady=2)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, font=("Courier New", 10), bg="#050811", fg="#e0e8ff", insertbackground="#e0e8ff")
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        # Make battle log / compiler output read-only.
        self.output_text.config(state=tk.DISABLED)

        self.refresh_ui()

    def build_hand_cards(self):
        """Render the 5-card hand as draggable cards on the canvas."""
        self.hand_canvas.delete("all")
        self.card_home_positions.clear()

        hand = self.game.player.hand
        # Layout cards like a fanned, overlapping deck.
        card_w = 230
        card_h = 125
        gap = -85  # heavier overlap, like a real hand
        start_x = 8
        base_y = 8

        for idx in range(5):
            x = start_x + idx * (card_w + gap)
            # Slight fan curve
            y = base_y + abs(idx - 2) * 3
            self.card_home_positions[idx] = (x, y)

            if idx >= len(hand):
                # Empty slot
                self.hand_canvas.create_rectangle(x, y, x + card_w, y + card_h, fill="#222222", outline="#444444")
                self.hand_canvas.create_text(x + 10, y + 10, anchor="nw", text="Empty", fill="#777777", font=("Courier New", 10))
                continue

            c = hand[idx]
            snippet = c.code.replace("\n", " ").strip()
            title = f"{c.energy_cost} mana"
            label = snippet

            fill = "#705028" if self.selected_card_index == idx else "#342414"
            outline = "#d0a060" if self.selected_card_index == idx else "#8a6a3a"

            # Drop shadow (tagged with the card so it moves/raises together)
            self.hand_canvas.create_rectangle(
                x + 4, y + 6, x + card_w + 4, y + card_h + 6,
                fill="#0d0d0d", outline="",
                tags=(f"card_{idx}", "card"),
            )
            self.hand_canvas.create_rectangle(
                x, y, x + card_w, y + card_h,
                fill=fill, outline=outline, width=2,
                tags=(f"card_{idx}", "card"),
            )
            # Cost badge
            self.hand_canvas.create_text(x + 8, y + 6, anchor="nw", text=title, fill="#f8f8f8", font=("Courier New", 10, "bold"), tags=(f"card_{idx}", "card"))
            # Snippet text
            # Use width-based wrapping so text never overlaps.
            self.hand_canvas.create_text(
                x + 8,
                y + 30,
                anchor="nw",
                text=label,
                width=card_w - 16,
                fill="#f8f8f8",
                font=("Courier New", 9),
                tags=(f"card_{idx}", "card"),
            )

    def _event_to_card_index(self, event) -> Optional[int]:
        items = self.hand_canvas.find_withtag("current")
        if not items:
            return None
        tags = self.hand_canvas.gettags(items[0])
        for t in tags:
            if t.startswith("card_"):
                try:
                    return int(t.split("_", 1)[1])
                except ValueError:
                    return None
        return None

    def on_hand_press(self, event):
        idx = self._event_to_card_index(event)
        hand = self.game.player.hand
        if idx is None or idx >= len(hand):
            return
        self.selected_card_index = idx
        self.dragging_idx = idx
        # Ensure dragged card stays visually on top of other cards.
        self.hand_canvas.tag_raise(f"card_{idx}")
        # Track drag offset using the rectangle bbox.
        bbox = self.hand_canvas.bbox(f"card_{idx}")
        if bbox:
            x1, y1, _, _ = bbox
            self.drag_offset_x = event.x - x1
            self.drag_offset_y = event.y - y1
        self.build_hand_cards()
        self.hand_canvas.tag_raise(f"card_{idx}")

        # Create a floating "ghost" card window that can draw above other widgets.
        self._start_drag_ghost(idx)

    def on_hand_drag(self, event):
        if self.dragging_idx is None:
            return
        idx = self.dragging_idx
        # Do not move the real card inside the canvas (it will get clipped by the canvas bounds).
        # The floating ghost is the only moving visual during drag.
        self.hand_canvas.tag_raise(f"card_{idx}")
        self._move_drag_ghost()

    def on_hand_release(self, event):
        if self.dragging_idx is None:
            return
        idx = self.dragging_idx
        self.dragging_idx = None
        self._end_drag_ghost()

        # If released over enemy panel, "play" the selected card.
        px = self.root.winfo_pointerx()
        py = self.root.winfo_pointery()
        ex1 = self.enemy_frame.winfo_rootx()
        ey1 = self.enemy_frame.winfo_rooty()
        ex2 = ex1 + self.enemy_frame.winfo_width()
        ey2 = ey1 + self.enemy_frame.winfo_height()
        over_enemy = (ex1 <= px <= ex2) and (ey1 <= py <= ey2)

        if over_enemy:
            # The card is chosen; user still must have typed the snippet correctly.
            self.selected_card_index = idx
            self.play_selected_card()
            return

        # Otherwise, nothing to do (card never moved in-canvas).

    def _on_global_release(self, event):
        # If user releases outside the hand canvas, still finalize drag.
        if self.dragging_idx is None:
            return
        # Synthesize a release handling path.
        self.on_hand_release(event)

    def _start_drag_ghost(self, idx: int):
        if self.drag_ghost is not None:
            try:
                self.drag_ghost.destroy()
            except tk.TclError:
                pass
            self.drag_ghost = None

        hand = self.game.player.hand
        if idx >= len(hand):
            return
        c = hand[idx]
        snippet = c.code.replace("\n", " ").strip()

        ghost = tk.Toplevel(self.root)
        ghost.overrideredirect(True)
        try:
            ghost.attributes("-topmost", True)
        except tk.TclError:
            # Fallback for some Tk builds
            ghost.wm_attributes("-topmost", 1)
        ghost.wm_attributes("-topmost", 1)
        ghost.transient(self.root)
        ghost.configure(bg="#000000")

        frame = tk.Frame(ghost, bg="#342414", bd=2, relief=tk.SOLID)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text=f"{c.energy_cost} mana", bg="#342414", fg="#ffffff", font=("Courier New", 10, "bold")).pack(anchor="nw", padx=6, pady=(6, 0))
        tk.Label(frame, text=snippet, bg="#342414", fg="#ffffff", font=("Courier New", 9), wraplength=220, justify=tk.LEFT).pack(anchor="nw", padx=6, pady=(6, 6))

        self.drag_ghost = ghost
        ghost.lift()
        ghost.deiconify()
        self.drag_ghost_running = True
        self._move_drag_ghost()
        self._ghost_tick()

    def _move_drag_ghost(self):
        if self.drag_ghost is None:
            return
        x = self.root.winfo_pointerx() + 10
        y = self.root.winfo_pointery() + 10
        try:
            self.drag_ghost.geometry(f"+{x}+{y}")
        except tk.TclError:
            self.drag_ghost = None

    def _ghost_tick(self):
        # Keep the ghost following the mouse even when cursor leaves the canvas.
        if not self.drag_ghost_running:
            return
        if self.drag_ghost is None:
            self.drag_ghost_running = False
            return
        self._move_drag_ghost()
        try:
            self.drag_ghost.lift()
        except tk.TclError:
            self.drag_ghost = None
            self.drag_ghost_running = False
            return
        self.root.after(16, self._ghost_tick)

    def _end_drag_ghost(self):
        if self.drag_ghost is None:
            self.drag_ghost_running = False
            return
        try:
            self.drag_ghost.destroy()
        except tk.TclError:
            pass
        self.drag_ghost = None
        self.drag_ghost_running = False

    def refresh_ui(self):
        # Player stats
        p = self.game.player
        self.player_stats.config(
            text=f"HP: {p.hp}/{p.max_hp}\n"
                 f"Mana: {p.energy}/{p.max_energy + p.mana_bonus} (base 10 + {p.mana_bonus} bonus)\n"
                 f"Block: {p.block}  (+{p.block_bonus} on gain)\n"
                 f"Strength: {p.strength}\n"
                 f"Damage Bonus: +{p.damage_bonus}\n"
                 f"Deck: {len(p.deck)}  Discard: {len(p.discard_pile)}"
        )

        # Enemy stats and floor
        e = self.battle.enemy
        self.floor_label.config(text=f"FLOOR {self.game.current_floor}/{self.game.max_floor}")
        self.enemy_label.config(text=e.name.upper())
        intent = e.get_intent()
        self.enemy_stats.config(
            text=f"HP: {e.hp}/{e.max_hp}\n"
                 f"Pattern: {e.attack_pattern}\n"
                 f"Next intent: {intent['damage']} damage"
        )

        # Hand cards
        self.build_hand_cards()

    def select_card(self, index: int):
        """Select which card/snippet the next program will belong to."""
        hand = self.game.player.hand
        if index >= len(hand):
            return
        self.selected_card_index = index
        # Do NOT auto-write the snippet; the player must type it.
        self.code_text.delete("1.0", tk.END)
        self.refresh_ui()

    def append_output(self, text: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

    def play_selected_card(self):
        if self.selected_card_index is None:
            self.append_output("Choose a snippet from the hand bar first.")
            return

        hand = self.game.player.hand
        if not hand or self.selected_card_index >= len(hand):
            self.append_output("Selected snippet slot is empty. End the turn to draw 5 new snippets.")
            return

        # Update selected card's code with whatever is in the editor
        new_code = self.code_text.get("1.0", tk.END).strip()
        card = hand[self.selected_card_index]
        card.code = new_code

        # Compile card code and execute
        compiler = CodexCompiler(new_code)
        result, errors = compiler.compile()
        output = compiler.get_output()

        symbol_table_text = ""
        if result is not None:
            symbol_table_text = format_symbol_table(result["symbol_table"])

        full_output = output
        if symbol_table_text:
            full_output += "\n\n" + symbol_table_text

        # Apply card via battle engine (player turn only) if compile succeeded; otherwise the card fizzles
        if result is not None:
            self.battle.log = []
            # Play only this card index; battle logic will move it to discard.
            # Only the player's turn is executed here. The enemy will act when End Turn is pressed.
            self.battle.player_turn([self.selected_card_index])
            full_output += "\n\n--- BATTLE LOG ---\n" + self.battle.get_log()
        else:
            full_output += "\n\n--- BATTLE LOG ---\nThe snippet failed to compile. Your attack/ability fizzles."

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, full_output)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)

        # After playing, clear selection and refresh
        self.selected_card_index = None
        self.check_battle_end()
        self.refresh_ui()

    def end_turn(self):
        # Unused cards go back to the "snippet" deck and deck is reshuffled.
        player = self.game.player
        while player.hand:
            card = player.hand.pop()
            player.deck.append(card)
        random.shuffle(player.deck)

        # Enemy turn via battle engine
        self.battle.enemy_turn()
        self.append_output(self.battle.get_log())

        # Start next player turn or end run
        if not player.is_alive():
            self.append_output("\nYou have been defeated. Run over.")
            self.disable_inputs()
            return

        if not self.battle.enemy.is_alive:
            # One enemy in this floor segment defeated.
            self.game.enemies_remaining_on_floor -= 1
            if self.game.enemies_remaining_on_floor > 0:
                # Heal to full and start another enemy on the same floor.
                self.append_output(f"\nEnemy defeated. {self.game.enemies_remaining_on_floor} more foe(s) remain on this floor.")
                self.battle = self.game.start_battle()
                self.refresh_ui()
            else:
                # Floor cleared.
                self.append_output("\nAll enemies on this floor defeated.")
                self.advance_floor()
            return

        # New player turn: reset mana and draw 5 new cards
        player.reset_turn()
        self.refresh_ui()

    def advance_floor(self):
        # Move to next floor until max_floor
        self.game.current_floor += 1
        if self.game.current_floor > self.game.max_floor:
            self.append_output("\nYou cleared all floors of the Snippet Spire. Victory!")
            self.disable_inputs()
            return

        # Light heal between floors before choosing a reward
        self.game.player.hp = self.game.player.max_hp

        # Offer reward choices so the player can keep up with stronger enemies
        self.show_reward_choice()

        # Randomize how many enemies next floor will have (1-3)
        self.game.enemies_remaining_on_floor = random.randint(1, 3)

        # After reward is chosen, start the next battle
        self.battle = self.game.start_battle()
        self.append_output(f"\nNew floor: {self.game.current_floor}. A new foe appears: {self.battle.enemy.name}.")
        self.refresh_ui()

    def show_reward_choice(self):
        reward_window = tk.Toplevel(self.root)
        reward_window.title("Choose Your Reward")
        reward_window.grab_set()

        label = tk.Label(
            reward_window,
            text="Floor cleared! Choose one reward:",
            font=("Courier New", 12, "bold"),
        )
        label.pack(padx=10, pady=8)

        def take_damage_buff():
            self.game.player.damage_bonus += 2
            self.append_output("Reward: Permanent +2 damage to your snippets.")
            reward_window.destroy()

        def take_health_buff():
            self.game.player.max_hp += 10
            self.game.player.hp = min(self.game.player.max_hp, self.game.player.hp + 10)
            self.append_output("Reward: +10 maximum HP (and a small heal).")
            reward_window.destroy()

        def take_block_buff():
            self.game.player.block_bonus += 3
            self.append_output("Reward: Permanent +3 block when you gain block.")
            reward_window.destroy()

        def take_mana_buff():
            self.game.player.mana_bonus += 1
            self.append_output("Reward: +1 mana every turn.")
            reward_window.destroy()

        def take_new_card():
            new_card = random.choice(CARD_LIBRARY)
            self.game.player.deck.append(CardInstance(new_card.name, new_card.code, new_card.energy_cost, new_card.description, new_card.card_type))
            self.append_output(f"Reward: New snippet added to deck -> {new_card.code}")
            reward_window.destroy()

        tk.Button(reward_window, text="Damage Buff (+2)", command=take_damage_buff, width=28).pack(padx=8, pady=4)
        tk.Button(reward_window, text="Health Buff (+10 max HP)", command=take_health_buff, width=28).pack(padx=8, pady=4)
        tk.Button(reward_window, text="Defense Buff (+3 block)", command=take_block_buff, width=28).pack(padx=8, pady=4)
        tk.Button(reward_window, text="Extra Mana (+2/turn)", command=take_mana_buff, width=28).pack(padx=8, pady=4)
        tk.Button(reward_window, text="New Snippet Card", command=take_new_card, width=28).pack(padx=8, pady=4)

    def check_battle_end(self):
        if not self.battle.enemy.is_alive:
            self.append_output(f"\nEnemy {self.battle.enemy.name} defeated.")
            self.advance_floor()
        elif not self.game.player.is_alive():
            self.append_output("\nYou have been defeated. Run over.")
            self.disable_inputs()

    def disable_inputs(self):
        self.play_button.config(state=tk.DISABLED)
        self.end_turn_button.config(state=tk.DISABLED)
        self.hand_canvas.unbind("<ButtonPress-1>")
        self.hand_canvas.unbind("<B1-Motion>")
        self.hand_canvas.unbind("<ButtonRelease-1>")


def main():
    root = tk.Tk()
    app = CodeSpireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
